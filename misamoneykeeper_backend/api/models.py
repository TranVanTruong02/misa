from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date
class User(AbstractUser):
    username = None
    type = models.PositiveIntegerField(default=1, choices=((1, 'User'), (2, 'Admin')))
    email = models.EmailField(max_length=100, default='', unique=True)
    mobile = models.CharField(max_length=15, default='')
    mobile_code = models.CharField(max_length=6, default='')
    password = models.CharField(max_length=100, default='')
    access_token = models.CharField(max_length=255, default='')
    refresh_token = models.CharField(max_length=255, default='')
    access_token_expiration = models.DateTimeField(auto_now_add=True)
    refresh_token_expiration = models.DateTimeField(auto_now_add=True)
    reset_code = models.CharField(max_length=6, default='0000')
    modify_date = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    def __str__(self):
        return self.email
    class Meta:
        db_table = 'User'
class UserDetails(models.Model):
    user_details_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    u_image = models.ImageField(upload_to='images', null=False, default=None)
    u_gender = models.PositiveIntegerField(default=1, help_text='1: Nam, 2: Nữ, ...')
    u_birthday = models.DateField(default=date.today)
    u_address = models.CharField(max_length = 200, default = '')
    u_job = models.CharField(max_length = 100, default = '')
    u_status = models.IntegerField(default=1, help_text='1: active, 2: deleted')
    u_created_date = models.DateTimeField(auto_now_add=True)
    u_modify_date = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.u_name
    
    class Meta:
        db_table = 'UserDetails'

class Account(models.Model):
    account_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    ac_name = models.CharField(max_length = 100, default = '')
    ac_money = models.IntegerField(default=0)
    ac_type = models.PositiveIntegerField(default=1, help_text='1: Tiền mặt, 2: Tài khoản ngân hàng, ...')
    ac_explanation = models.CharField(max_length = 1000, default = '')
    ac_status = models.IntegerField(default=1, help_text='1: active, 2: deleted')
    ac_created_date = models.DateTimeField(auto_now_add=True)
    ac_modify_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ac_name
    
    class Meta:
        db_table = 'Account'

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    ca_type = models.PositiveIntegerField(default=1, help_text='1: Chi tiền, 2: Thu tiền, ...')
    ca_name = models.CharField(max_length = 100, default = '')
    ca_image = models.ImageField(upload_to='images', null=False, default=None)
    ca_explanation = models.CharField(max_length = 1000, default = '')
    ca_status = models.IntegerField(default=1, help_text='1: active, 2: deleted')
    ca_created_date = models.DateTimeField(auto_now_add=True)
    ca_modify_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ca_name
    
    class Meta:
        db_table = 'Category'

class CategoryDetails(models.Model):
    category_details_id = models.AutoField(primary_key=True)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE, default=0)
    cad_type = models.PositiveIntegerField(default=1, help_text='1: Chi tiền, 2: Thu tiền, ...')
    cad_name = models.CharField(max_length = 100, default = '')
    cad_image = models.ImageField(upload_to='images', null=False, default=None)
    cad_explanation = models.CharField(max_length = 1000, default = '')
    cad_status = models.IntegerField(default=1, help_text='1: active, 2: deleted')
    cad_created_date = models.DateTimeField(auto_now_add=True)
    cad_modify_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cad_name
    
    class Meta:
        db_table = 'CategoryDetails'

class Pay(models.Model):
    pay_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    category_details_id = models.ForeignKey(CategoryDetails, on_delete=models.CASCADE, default=0)
    account_id = models.ForeignKey(Account, on_delete=models.CASCADE, default=0)
    p_type = models.PositiveIntegerField(default=1, help_text='1: Chi tiền, 2: Thu tiền, ...')
    p_money = models.IntegerField(default=0)
    p_explanation = models.CharField(max_length = 1000, default = '')
    p_date = models.DateField(default=date.today)
    p_status = models.IntegerField(default=1, help_text='1: active, 2: deleted')
    p_created_date = models.DateTimeField(auto_now_add=True)
    p_modify_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.p_explanation

    class Meta:
        db_table = 'Pay'

class notification(models.Model) :
    id_n = models.BigAutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, default=0)
    text_n = models.TextField()
    read_status =  models.IntegerField(default=1, help_text='1: active, 2: deleted')
    created = models.DateTimeField(auto_now_add=True)   

    def __str__(self) :
        return self.text_n
    class Meta:
        db_table = 'notification'


class helpInformation (models.Model):
    id_hvsi= models.BigAutoField(primary_key=True)
    HDSD= models.TextField()
    website= models.URLField()
    followFB= models.URLField()
    shareFB= models.URLField()
    usageA= models.TextField()
    PAP= models.TextField()

    def __str__(self) :
        return self.HDSD
    class Meta:
        db_table = 'helpInformation'


