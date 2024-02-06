from django.urls import include, path
from rest_framework import routers

from .views import UserViewSet, SubscriptionViewSet

router = routers.SimpleRouter()

#router.register(r'users', UserViewSet, basename='users')
router.register(r'users', SubscriptionViewSet, basename='users')


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    #path('', include('djoser.urls')),
]
