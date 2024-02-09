from django.urls import include, path
from rest_framework import routers


from .views import SubscriptionViewSet


router = routers.DefaultRouter()
router.register(r'users', SubscriptionViewSet, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
