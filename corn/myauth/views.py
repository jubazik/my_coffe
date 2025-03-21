from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpRequest, HttpResponse

def login_view(request: HttpRequest):
    if request.user.is_authenticated:
        return redirect('/admin/.html')
    return render(request, 'myauth/login.html')

    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('/admin/.html')

    return render(request, 'myauth/login.html', {'error': "invalid login credentials"})

def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response

def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.GET.get('fizz', 'default velue')
    return HttpResponse(f'cookie: {value!r}')