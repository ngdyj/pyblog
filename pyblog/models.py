from django.db import models


class Tag(models.Model):
    id = models.AutoField('ID', primary_key=True)
    name = models.CharField('标签.', max_length=10, null=False, blank=False, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'


class Category(models.Model):
    id = models.AutoField('ID', primary_key=True)
    name = models.CharField('分类', max_length=15, null=False, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'


class Article(models.Model):
    id = models.AutoField('ID', primary_key=True)
    is_pub = models.BooleanField('是否发布', null=False, blank=False)
    title = models.CharField('文章标题', max_length=255)
    content = models.TextField('内容')
    tags = models.ManyToManyField(Tag)
    category = models.ForeignKey(Category, verbose_name='分类', on_delete=False, null=True)
    pub_date = models.DateTimeField(verbose_name="发布日期", auto_now_add=True)  # auto_now_add 创建时自动添加时间
    mod_date = models.DateTimeField(verbose_name="更新日期", auto_now=True)      # auto_now 更新时,自动更新时间

    def __str__(self):
        return self.title

    class Meta:
        # https://docs.djangoproject.com/en/2.2/ref/models/options/
        verbose_name = '文章'
        verbose_name_plural = '文章'



