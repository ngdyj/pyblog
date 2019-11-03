from django.db import models


class Tag(models.Model):
    id = models.AutoField('ID', primary_key=True)
    name = models.CharField('标签.', max_length=10, null=False, blank=False, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    id = models.AutoField('ID', primary_key=True)
    name = models.CharField('分类', max_length=15, null=False, blank=False)

    def __str__(self):
        return self.name


class Article(models.Model):
    id = models.AutoField('ID', primary_key=True)
    is_pub = models.BooleanField('是否发布', null=False, blank=False)
    title = models.CharField('文章标题', max_length=255)
    content = models.TextField('内容')
    tags = models.ManyToManyField(Tag)
    category = models.ForeignKey(Category, verbose_name='分类', on_delete=False, null=True)

    def __str__(self):
        return self.title



