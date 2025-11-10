from django.urls import path
from .views import ReferralListView, ReferralStatsView, MyReferralCodeView, ActivateReferralCodeView

app_name = 'referrals'

urlpatterns = [
    path('my-code/', MyReferralCodeView.as_view(), name='my_code'),
    path('stats/', ReferralStatsView.as_view(), name='stats'),
    path('list/', ReferralListView.as_view(), name='list'),
    path('activate-code/', ActivateReferralCodeView.as_view(), name='activate_code'),
]
