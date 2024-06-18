import requests


class OpenBookAPI:
    BASE_URL = "https://openlibrary.org"

    def get_book(self, isbn):
        response = requests.get(f"{self.BASE_URL}/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data")
        if response.status_code == 200:
            response_json = response.json()
            return response_json[0]
        else:
            print(f"Error: {response.status_code}: {response.content}")
            return None

    def search_book(self, title):
        response = requests.get(f"{self.BASE_URL}/search.json", params={"title": title})
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}: {response.content}")
            return None

    def get_cover(self, isbn):
        book_data = self.get_book(isbn)
        if 'ISBN:' + isbn in book_data:
            cover_id = book_data['ISBN:' + isbn].get('cover', {}).get('medium')
            return cover_id
        else:
            print(f"No cover found for ISBN: {isbn}")
            return None


class MangaDexAPI:
    BASE_URL = "https://api.mangadex.org"
    COVER_URL = "https://uploads.mangadex.org"

    def get_manga(self, manga_id):
        response = requests.get(f"{self.BASE_URL}/manga/{manga_id}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}: {response.content}")
            return None

    def search_manga(self, title):
        response = requests.get(f"{self.BASE_URL}/manga/", params={"title": title})
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}: {response.content}")
            return None

    def get_cover_art(self, manga_id, cover_art_id):
        response = f"{self.COVER_URL}/covers/{manga_id}/{cover_art_id}.jpg"
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}: {response.content}")
            return None

    def get_chapter_list(self, manga_id):
        response = requests.get(f"{self.BASE_URL}/manga/{manga_id}/feed")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}: {response.content}")
            return None


class AniListAPI(MangaDexAPI):
    BASE_URL = "https://graphql.anilist.co"

    def __init__(self):
        self.cache = {}

    def get_anime(self, anime_id):
        query = """
        query ($id: Int) {
            Media (id: $id, type: ANIME) {
            id
            title {
                romaji
                english
                native
                }
            coverImage {
                large
                medium
                color
            }
            status
            startDate
            description
            episodes
            duration
            }
        }
        """
        variables = {
            'id': anime_id
        }

        response = requests.post(self.BASE_URL, json={'query': query, 'variables': variables})
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}, {response.content}")
            return None

    def search_anime(self, title):
        if title in self.cache:
            return self.cache[title]

        query = """
        query ($title: String) {
            Page { 
                media (search: $title, type: ANIME) {
                    id
                    title {
                        english
                        romaji
                        }
                    description
                    startDate {
                        year
                        }
                    status
                    coverImage {
                        large
                        medium
                    }
                    averageScore
                }
            }
        }
        """

        variables = {
            'title': title
        }

        response = requests.post(self.BASE_URL, json={'query': query, 'variables': variables})
        if response.status_code == 200:
            data = response.json()['data']['Page']['media']
            self.cache[title] = data
            return data
        else:
            print(f"Error: {response.status_code}, {response.content}")
            return None

    @staticmethod
    def clean_anime_data(raw_data):
        if raw_data is None:
            return None

        cleaned_data = {'id': raw_data.get('id', 'N/A'), 'title': raw_data.get('title', 'N/A'),
                        'description': raw_data.get('description', 'N/A'),
                        'coverImage': raw_data.get('coveImage', {}).get('large')}

        return cleaned_data

    def search_anime_clean(self, title):
        raw_data = self.search_anime(title)
        return [self.clean_anime_data(anime) for anime in raw_data]

    def search_manga(self, title):
        pass

    def get_manga(self, manga_id):
        pass


class MangaData(MangaDexAPI):
    def __init__(self, manga_id):
        self._manga_id = manga_id
        self._manga_response_data = self.get_manga(manga_id)
        self._cover_art_id = self._manga_response_data['data']['relationships'][2]['id']
        self._title = self._manga_response_data['data']['attributes']['title']['en']
        self._year = self._manga_response_data['data']['attributes']['year']
        self._status = self._manga_response_data['data']['attributes']['status']
        self._description = self._manga_response_data['data']['attributes']['description']['en']
        self._cover_art = self.get_cover_art(self._manga_id, self._cover_art_id)

    @property
    def manga_id(self):
        return self._manga_id

    @property
    def title(self):
        return self._title

    @property
    def year(self):
        return self._year

    @property
    def status(self):
        return self._status

    @property
    def description(self):
        return self._description

    @property
    def cover_art(self):
        return self._cover_art

    @property
    def number_of_chapters(self):
        chapter_list = self.get_chapter_list(self.manga_id)
        return len(chapter_list['results'])

    @property
    def chapter_list(self):
        return self.get_chapter_list(self.manga_id)


class AnimeData(AniListAPI):
    def __init__(self, anime_id):
        self._anime_id = anime_id
        self._anime_response_data = self.get_anime(anime_id)
        self._cover_art = self._anime_response_data['data']['coverImage']['large']
        self._title = self._anime_response_data['data']['title'][0]
        self._year = self._anime_response_data['data']['startDate']['year']
        self._status = self._anime_response_data['data']['status']
        self._description = self._anime_response_data['data']['description']
        self._episodes_number = self._anime_response_data['data']['episodes']
        self._duration_each_episode = self._anime_response_data['data']['duration']

    @property
    def title(self):
        return self._title

    @property
    def year(self):
        return self._year

    @property
    def status(self):
        return self._status

    @property
    def description(self):
        return self._description

    @property
    def cover_art(self):
        return self._cover_art

    @property
    def episodes_number(self):
        return self._episodes_number

    @property
    def duration(self):
        return self._duration_each_episode


class BookData(OpenBookAPI):
    def __init__(self, isbn):
        self._isbn = isbn
        self._book_response_data = self.get_book(isbn)
        self._cover_image = self._book_response_data['cover']['large']
        self._title = self._book_response_data['title']
        self._year = self._book_response_data['publish_date']
        self._description = self._book_response_data['subtitle']
        self._number_of_pages = self._book_response_data['number_of_pages']

    @property
    def title(self):
        return self._title

    @property
    def year(self):
        return self._year

    @property
    def number_of_pages(self):
        return self._number_of_pages

    @property
    def description(self):
        return self._description

    @property
    def cover_image(self):
        return self._cover_image


class Library:
    def __init__(self):
        self.manga_collection = []
        self.anime_collection = []
        self.book_collection = []

    def add_manga(self, manga):
        if isinstance(manga, MangaData):
            self.manga_collection.append(manga)

    def add_anime(self, anime):
        if isinstance(anime, AnimeData):
            self.manga_collection.append(anime)

    def add_book(self, book):
        if isinstance(book, BookData):
            self.manga_collection.append(book)


class User:
    def __init__(self, username):
        self.username = username
        self.library = Library()
