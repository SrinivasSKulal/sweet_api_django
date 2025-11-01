from django.urls import path
from .views import sweets , search , login, register, update


urlpatterns = [
    path('auth/login' , login , name="Login"),
    path('auth/register' , register , name="Register"),
    path('sweets',sweets , name="sweets"),
    path('sweets/search/' ,search  , name="Search" ),
    path('sweets/<int:id>' ,update , name="Update" )
]
