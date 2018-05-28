from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
from django.db import models

#会计科目表（原有）
class Accounting_subjects(models.Model):
    #科目编号
    subject_ID = models.CharField(primary_key=True, max_length=50)
    #科目名称
    accounting_name = models.CharField(max_length=50)
    #科目类别
    subject_category = models.CharField(max_length=50)

    def __unicode__(self):
        return self.username

#会计科目表（新建）
class Accounting_subjects_new(models.Model):
    #科目编号
    subject_ID = models.CharField(max_length=50)
    #科目名称
    accounting_name = models.CharField(max_length=50)
    #公司ID
    company_ID = models.CharField(max_length=100)
    #科目类别
    subject_category = models.CharField(max_length=50)

    def __unicode__(self):
        return self.username

#用户表
class User(models.Model):
    #公司ID自动生成
    company_ID = models.AutoField(primary_key=True)
    #公司名称
    company_name = models.CharField(max_length=100,unique=True)
    #密码
    password = models.CharField(max_length=100)
    #邮箱
    email = models.EmailField(unique=True)
    #创建时间
    c_time = models.DateTimeField(auto_now_add=True, blank=True)
    #是否通过邮箱验证激活
    has_confirmed = models.BooleanField(default=False)

    def __unicode__(self):
        return self.company_name

#用户注册注册码
class ConfirmString(models.Model):
    code = models.CharField(max_length=256)
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    c_time = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.user.company_name + ": " + self.code

#日记账
class Journal(models.Model):
    #公司名称
    company_name = models.CharField(max_length=100)
    #日期
    time = models.DateTimeField()
    #科目编号
    subject_ID = models.CharField(max_length=100)
    #借贷
    Dr_Cr = models.CharField(max_length=50)
    #金额
    money = models.FloatField()
    #活动类型
    activity_type = models.CharField(max_length=50,blank=True)
    #摘要
    abstract = models.CharField(max_length=100,blank=True)

    def __unicode__(self):
        return self.username