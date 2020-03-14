from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from datetime import datetime, timedelta, timezone
import hashlib
import os
import subprocess
import gzip

# set work dir
os.chdir(os.path.dirname(os.path.realpath(__file__)))


# https://console.cloud.tencent.com/api/explorer?Product=cos&Version=2018-11-26&Action=PutObjectACL&SignVersion=


# tencent settings
secret_id = '替换为你自己的secret_id'
secret_key = '替换为你自己的secret_key'
region = 'ap-shanghai(根据情况替换)'
bucket = '替换为你自己的桶名'
bucket_dirname = 'pyblog'
scheme = 'https'

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=None, Scheme=scheme)
client = CosS3Client(config)

backup_dirname = '.backup'  # 数据库备份的文件夹名字


# mysql settings
mysql_user = 'pyblog'
mysql_password = '123456'
mysql_backup_db_name = 'pyblog'


def gen_backup_time() -> str:
    return datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d_%H_%M_%S")


def put_file(dirname, file) -> bool:
    filename = file
    file_path = file if file.startswith(backup_dirname) else '{0}/{1}'.format(backup_dirname, file)

    # gzip file
    with open(file_path, 'rb') as f_in, gzip.open('{0}.gz'.format(file_path), 'wb') as f_out:
        f_out.writelines(f_in)

    with open('{0}.gz'.format(file_path), 'rb') as fp:
        response = client.put_object(
            Bucket=bucket,
            Body=fp,
            Key='{dirname}/{name}.gz'.format(dirname=dirname, name=filename),
            StorageClass='STANDARD',
            EnableMD5=False
        )
        # print(response['ETag'])
        record_log(filename)  # write log file
        print("backup success!")
    return True


def compose_md5(file1, file2) -> bool:
    file1_md5 = None
    file2_md5 = None
    if file1 is None or file2 is None:
        return False

    file1_path = file1 if file1.startswith(backup_dirname) else '{0}/{1}'.format(backup_dirname, file1)
    file2_path = file2 if file1.startswith(backup_dirname) else '{0}/{1}'.format(backup_dirname, file2)

    with open(file1_path, "rb") as f:
        md5_hash = hashlib.md5()
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
        file1_md5 = md5_hash.hexdigest()

    with open(file2_path, "rb") as f:
        md5_hash = hashlib.md5()
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
        file2_md5 = md5_hash.hexdigest()
    if file1_md5 is not None and (file1_md5 == file2_md5):
        return True
    return False


def mysql_dump(save_filename):
    # mysqldump -upyblog -p pyblog  2>/dev/null |gzip > pyblog.sql.gz
    p = subprocess.Popen(
        'mysqldump --dump-date=false --user={user} --password={pwd} {dbname}'.format(user=mysql_user,
                                                                                     pwd=mysql_password,
                                                                                     dbname=mysql_backup_db_name),
        stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    std_out, std_err = p.communicate()

    if p.returncode > 0:
        print(std_err)
        return False
    else:
        with open("{backup_dir}/{filename}".format(backup_dir=backup_dirname, filename=save_filename), "wb") as f:
            f.write(std_out)
            return True


def tree() -> list:
    return sorted(list(filter(lambda name: str(name).endswith('.sql'), os.listdir(backup_dirname))), reverse=True)


def record_log(filename):
    with open(backup_dirname + "/backup.log", "a+") as f:
        f.writelines(filename + "\n")


def in_record(filename) -> bool:
    with open(backup_dirname + "/backup.log", "r") as f:
        if filename + "\n" in f.readlines():
            return True
    return False


def init():
    if not os.path.exists(backup_dirname):
        os.mkdir(backup_dirname)
    if not os.path.exists(backup_dirname + "/backup.log"):
        with open(backup_dirname + "/backup.log", "w+") as f:
            pass


def main():
    save_filename = "pyblog-{time}.sql".format(time=gen_backup_time())
    dump_status = mysql_dump(save_filename)
    if dump_status is False:
        exit(1)

    files = tree()
    if files.__len__() <= 1:
        put_file(bucket_dirname, save_filename)
    elif in_record(files[0]):
        pass
    elif in_record(files[0]) is False and compose_md5(files[0], files[1]) is False:
        put_file(bucket_dirname, files[0])
    else:
        print("The file has been backed up to the server")


if __name__ == '__main__':
    init()
    main()