from django.contrib.auth.views import LoginView
from django.urls import path
from .views import (
    set_cookie_view,
    get_cookie_view,
    # MyLogoutView,
    logout_view,
    AboutMeView,
    RegisterView,

)


app_name = 'myauth'

urlpatterns = [
    path('login/', LoginView.as_view(
        template_name='myauth/login.html',
        redirect_authenticated_user=True,
    ),
         name='login'),
    # path('logout/', MyLogoutView.as_view(), name='logout'),
    path('logout/', logout_view, name='logout'),
    path('about-me/', AboutMeView.as_view(), name='about-me'),
    path('register/', RegisterView.as_view(), name='register'),
    path('cookie/get/', get_cookie_view, name='cookie_get'),
    path('cookie/set/', set_cookie_view, name='cookie_set'),
]