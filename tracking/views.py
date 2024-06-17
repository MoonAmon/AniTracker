from django.shortcuts import render
from .forms import SearchForm
from .maaboo import MangaData, AnimeData, BookData, AniListAPI


def search(request):
    form = SearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data['query']
        api = AniListAPI()
        anime_data = api.search_anime(title=query)
        return render(request, 'search_results.html', {'anime': anime_data})
    else:
        return render(request, 'search.html', {'form': form})
