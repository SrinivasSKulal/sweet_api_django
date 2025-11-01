from django.urls import path
from .views import get_users,create_user,sweets


urlpatterns = [
    path('sweets',sweets , name="sweets"),
]
