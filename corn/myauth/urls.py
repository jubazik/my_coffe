from django.contrib.auth.views import LoginView
from django.urls import path
from .views import set_cookie_view, get_cookie_view


app_name = 'myauth'

urlpatterns = [
    path('login/', LoginView.as_view(
        template_name='myauth/login.html',
        redirect_authenticated_user=True,
    ),
         name='login'),
    path('cookie/get/', get_cookie_view, name='cookie_get'),
    path('cookie/set/', set_cookie_view, name='cookie_set'),
]