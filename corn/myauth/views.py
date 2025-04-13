from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LogoutView
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, CreateView


class AboutMeView(TemplateView): #Создал для проверки  регистрации и авторизации
    template_name = "base.html"


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)

        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(
            self.request,
            username=username,
            password=password,
        )
        login(self.request, user)
        return response

def login_view(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('/admin/')
    return render(request, 'myauth/login.html')

    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('/admin/')

    return render(request, 'myauth/login.html', {'error': "invalid login credentials"})

def logout_view(request: HttpRequest):
    logout(request)
    return redirect(reverse("myauth:login"))


def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response

def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get('fizz', 'default velue')
    return HttpResponse(f'cookie: {value!r}')