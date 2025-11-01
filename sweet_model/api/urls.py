from django.urls import path
from .views import sweets , search , login, register


urlpatterns = [
    path('sweets',sweets , name="sweets"),
    path('sweets/search/' ,search  , name="Search" ),
    path('auth/login' , login , name="Login"),
    path('auth/register' , register , name="Register")
]
