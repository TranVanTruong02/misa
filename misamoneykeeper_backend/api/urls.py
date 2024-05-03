from django.urls import path
from .views import CategoryCollectView, HistoryHomeView, PayDeleteView, PayUpdateView, RecentNotesHomeView, SpendingCollectedView, UserProfileView, UserRegisterAdmin, UserRegisterView, UserLoginView, UserLogoutView, AccountAddView, AccountView, AccountUpdateView, AccountDeleteView, RefreshAccessToken, PayAddView, BalanceAdjustmentView, CategoryView, HistoryView, RecentNotesView,SpendingView,CollectedView, ShowNotification, UserUpdateProfileView, UserUpdateView

urlpatterns = [
    path('misamoneykeeper/admin/register', UserRegisterAdmin.as_view(), name='register admin'),
    path('misamoneykeeper/register', UserRegisterView.as_view(), name='register'),
    path('misamoneykeeper/login', UserLoginView.as_view(), name='login'),
    path('misamoneykeeper/logout', UserLogoutView.as_view(), name='logout'),
    path('misamoneykeeper/refreshaccesstoken', RefreshAccessToken.as_view(), name='refresh access token'),
    path('misamoneykeeper/newpassword', UserUpdateView.as_view(), name='new password'),
    path('misamoneykeeper/profile', UserProfileView.as_view(), name='view profile'),
    path('misamoneykeeper/profile/update', UserUpdateProfileView.as_view(), name='update profile'),
    path('misamoneykeeper/add/pay', PayAddView.as_view(), name='Pay Add'),
    path('misamoneykeeper/update/pay', PayUpdateView.as_view(), name='Pay Update'),
    path('misamoneykeeper/delete/pay', PayDeleteView.as_view(), name='Pay Delete'),
    path('misamoneykeeper/balance/adjustment', BalanceAdjustmentView.as_view(), name='Balance Adjustment'),
    path('misamoneykeeper/category', CategoryView.as_view(), name='category'),
    path('misamoneykeeper/category/collect', CategoryCollectView.as_view(), name='category collect'),
    path('misamoneykeeper/history', HistoryView.as_view(), name='history'),
    path('misamoneykeeper/history/home', HistoryHomeView.as_view(), name='history view'),
    path('misamoneykeeper/recnetnote/home', RecentNotesHomeView.as_view(), name='recnet note home'),
    path('misamoneykeeper/recnetnote', RecentNotesView.as_view(), name='history'),
    path('misamoneykeeper/account', AccountView.as_view(), name='Account View'),
    path('misamoneykeeper/account/add', AccountAddView.as_view(), name='Add Account'),
    path('misamoneykeeper/account/update', AccountUpdateView.as_view(), name='Account Update'),
    path('misamoneykeeper/account/delete', AccountDeleteView.as_view(), name='Account Delete'),
    path('misamoneykeeper/spending',SpendingView.as_view(),name='Spending analysis'),
    path('misamoneykeeper/collected',CollectedView.as_view(),name='Collected analysis'),
    path('misamoneykeeper/spendingcollected',SpendingCollectedView.as_view(),name=' Spending Collected'),
    path('misamoneykeeper/notification',ShowNotification.as_view(),name=' notification'),
    
]
