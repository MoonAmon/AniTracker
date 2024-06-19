from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from .forms import SearchForm, NewUserForm
from .maaboo import MangaData, AnimeData, BookData, AniListAPI

API_ANILIST = AniListAPI()


def search(request):
    form = SearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data['query']
        anime_data = API_ANILIST.search_anime(title=query)
        return render(request, 'search_results.html', {'anime': anime_data})
    else:
        return render(request, 'search.html', {'form': form})


def home(request):
    random_animes = API_ANILIST.search_anime('Naruto')
    return render(request, 'home.html', {'animes': random_animes})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            email = form.cleaned_data.get('email')
            user = authenticate(username=username, password=password, email=email)
            if user is not None:
                login(request, user)
                return redirect('home')

    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = NewUserForm()
    return render(request, 'register.html', {'register_form': form})


def logout_view(request):
    logout(request)
    return redirect('home')
