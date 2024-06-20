from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse
from .forms import SearchForm, NewUserForm
from .models import Anime, Manga, Book
from .maaboo import MangaData, AnimeData, BookData, AniListAPI

API_ANILIST = AniListAPI()


class BaseDetailView(View):
    def get(self, request, media_id):
        data = self.get_data(media_id)
        return render(request, self.template_name, {'data': data})

    def post(self, request, media_id):
        pass

    def get_data(self, media_id):
        raise NotImplemented


class AnimeDetailView(BaseDetailView):
    template_name = 'anime_detail.html'

    def get_data(self, media_id):
        data = AnimeData(media_id)
        anime, created = Anime.objects.get_or_create(
            title=data.title,
            anilist_id=data.anime_id,
            defaults={
                'description': data.description,
                'cover_art': data.cover_art,
                'total_episodes': data.episodes_number,
                'duration': data.duration,
            }
        )
        anime.save()
        return data


class MangaDetailView(BaseDetailView):
    def get_data(self, media_id):
        data = MangaData(media_id)
        manga = Manga(
            title=data.title(),
            mangadex_id=data.manga_id(),
            description=data.description(),
            cover_art=data.cover_art(),
            total_chapters=data.number_of_chapters()
        )
        manga.save()
        return data


class BookDetailView(BaseDetailView):
    def get_data(self, media_id):
        return BookData.get_book(media_id)


def search(request):
    query = request.GET.get('query')
    search_results = API_ANILIST.search_anime(title=query)
    anime_data = [anime for anime in search_results if anime['title']['romaji']]
    for anime in anime_data:
        anime['detail_url'] = reverse('anime_detail', args=[anime['id']])
    return render(request, 'search_results.html', {'anime': anime_data})


def home(request):
    random_anime = API_ANILIST.search_anime('Naruto')
    return render(request, 'home.html', {'animes': random_anime})


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
