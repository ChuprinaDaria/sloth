from django.urls import path
from .views import (
    PlanListView, SubscriptionView, activate_code,
    create_checkout_session, cancel_subscription, UsageView
)

app_name = 'subscriptions'

urlpatterns = [
    path('plans/', PlanListView.as_view(), name='plan_list'),
    path('current/', SubscriptionView.as_view(), name='current'),
    path('activate-code/', activate_code, name='activate_code'),
    path('checkout/', create_checkout_session, name='checkout'),
    path('cancel/', cancel_subscription, name='cancel'),
    path('usage/', UsageView.as_view(), name='usage'),
]
