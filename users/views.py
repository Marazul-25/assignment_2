from django.shortcuts import render,redirect
from users.forms import Registerform
from django.contrib.auth import login, logout
from users.forms import LoginForm
from django.contrib.auth.decorators import login_required
def sign_up(request):
    if request.method == 'GET':
        form = Registerform()
    if request.method == 'POST':
        form = Registerform(request.POST)
        if form.is_valid():
            form.save()

    return render(request ,'register.html',{"form": form})

def sign_in(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    return render(request, 'register.html', {'form': form})

@login_required
def sign_out(request):
    if request.method == 'POST':
        logout(request)
        return redirect('sign-in')
    
def home(request):
    return render(request, 'home.html')


def sign_out(request):
    return render(request, 'home.html')