from .openbook import OpenBookAPI
api = OpenBookAPI()

book_data = api.get_book('0140328726')

print(book_data)