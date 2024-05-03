from django.contrib import admin
from .models import User, UserDetails, Account, Category, CategoryDetails, Pay, notification, helpInformation

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'type', 'email', 'mobile', 'last_login', 'is_active', 'modify_date',)
    search_fields = ('last_name', 'email',)
    list_filter = ('type',)
    ordering = ('id',)
    readonly_fields = ['id', 'is_superuser', 'last_login', 'is_active', 'modify_date']

@admin.register(UserDetails)
class UserDetailsAdmin(admin.ModelAdmin):
    list_display = ('user_details_id', 'user_id', 'u_image', 'u_gender', 'u_birthday', 'u_address', 'u_job', 'u_status', 'u_modify_date',)
    search_fields = ('user_details_id',)
    list_filter = ('user_details_id',)
    ordering = ('user_details_id',)
    readonly_fields = ['user_details_id', 'u_status', 'u_created_date', 'u_modify_date']

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('account_id', 'user_id', 'ac_name', 'ac_money', 'ac_type', 'ac_explanation', 'ac_status', 'ac_modify_date',)
    search_fields = ('account_id', 'ac_name',)
    list_filter = ('ac_type',)
    ordering = ('account_id',)
    readonly_fields = ['account_id', 'ac_status', 'ac_modify_date', 'ac_modify_date']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id','ca_type' , 'ca_name', 'ca_image', 'ca_explanation', 'ca_status', 'ca_modify_date',)
    search_fields = ('category_id', 'ca_name',)
    list_filter = ('ca_name',)
    ordering = ('category_id',)
    readonly_fields = ['category_id', 'ca_status', 'ca_modify_date', 'ca_modify_date']

@admin.register(CategoryDetails)
class CategoryDetailsAdmin(admin.ModelAdmin):
    list_display = ('category_details_id', 'category_id', 'cad_type', 'cad_name', 'cad_image', 'cad_explanation', 'cad_status', 'cad_modify_date',)
    search_fields = ('category_details_id', 'category_id', 'cad_name',)
    list_filter = ('category_details_id', 'cad_type',)
    ordering = ('category_details_id',)
    readonly_fields = ['category_details_id', 'cad_status', 'cad_created_date', 'cad_modify_date']
    
@admin.register(Pay)
class PayAdmin(admin.ModelAdmin):
    list_display = ('pay_id', 'user_id', 'category_details_id', 'account_id', 'p_type', 'p_money', 'p_explanation', 'p_date', 'p_status', 'p_modify_date',)
    search_fields = ('pay_id', 'user_id', 'p_type',)
    list_filter = ('p_type',)
    ordering = ('pay_id',)
    readonly_fields = ['pay_id', 'p_status', 'p_created_date', 'p_modify_date']

@admin.register(notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id_n','user_id','text_n','read_status','created')
    search_fields = ('created',)
    list_filter = ('read_status',)
    ordering = ('id_n',)
    readonly_fields = ['id_n']

@admin.register(helpInformation)
class HelpInformationAdmin(admin.ModelAdmin):
    list_display = ('id_hvsi','HDSD','website','followFB','shareFB','usageA','PAP')
    search_fields = ('id_hvsi',)
    list_filter = ('HDSD',)
    ordering = ('id_hvsi',)
    readonly_fields = ['id_hvsi']
