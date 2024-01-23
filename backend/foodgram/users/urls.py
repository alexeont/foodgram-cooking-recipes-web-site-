from django.urls import include, path

from .views import SubscriptionAPI


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('users/<id>/subscribe/', SubscriptionAPI.as_view()),
    path('users/subscriptions/', SubscriptionAPI.as_view()),
    path('', include('djoser.urls')),
]
