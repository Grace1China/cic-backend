from django.urls import path, include
from rest_framework.routers import DefaultRouter
from payment import views

# 创建路由器并注册我们的视图。
# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'iap/charges', views.IAPChargeViewSet)
# router.register(r'iap/orders', views.OrderViewSet)

# API URL现在由路由器自动确定。
# The API URLs are now determined automatically by the router.

urlpatterns = [
    path('payments/', include(router.urls)),
    path('payments/iap/verifyreceipt', views.IapVerifyReceipt.as_view()),
    path('payments/orders', views.OrderCreateAPIView.as_view()),
    # path('payments/iap/verify', views.IapVerification)
]
