import glob
import json
import os.path
from typing import TypedDict

class Quote(TypedDict):
    text: str
    reference: str
    id: str

class Category(TypedDict):
    name: str
    subcategories: dict[str, "Category"]
    quotes: dict[str, Quote]

class FlatQuote(TypedDict):
    categories_path: list[str]
    quote: Quote


class QuotesLoader:
    def __init__(self, quotes_dir):
        self.categories: Category = {'name': '', 'subcategories': {}, 'quotes': {}}
        self.flat_quotes: list[FlatQuote] = []
        self.quote_id_to_quote: dict[str, Quote] = {}

        for filename in glob.iglob( quotes_dir + '/**/*', recursive=True):
            if not os.path.isfile(filename):
                continue
            print("Loading", filename)
            fname = filename.split('/')[-1].split('.')[0]
            categories_path = filename.split('/')[1:-1]
            category = self._find_category(categories_path)
            if filename.endswith('.txt'):
                with open(filename, 'r') as file:
                    for line in file:
                        category["name"] = line.strip()
            if filename.endswith('.json'):
                with open(filename, 'r') as file:
                    quotes = json.load(file)
                    for quote in quotes:
                        id = '_'.join(categories_path) + '_' + fname + '_' + str(quote['id'])
                        print('...', id)
                        quote = Quote(text=quote['text'], reference=quote['reference'], id=id)
                        self.quote_id_to_quote[id] = quote
                        self.flat_quotes.append({'categories_path': categories_path, 'quote': quote})
                        category['quotes'][id] = quote

        self.flat_quotes.sort(key=lambda x: x['quote']['id'])

    def _find_category(self, categories_path: list[str]) -> Category:
        category = self.categories
        for category_name in categories_path:
            if category_name not in category['subcategories']:
                category['subcategories'][category_name] = {'name': '', 'subcategories': {}, 'quotes': {}}
            category = category['subcategories'][category_name]
        return category

    def filter_by_top_category(self, top_level_categories: list[str]) -> list[FlatQuote]:
        outcome = []
        for flat_quote in self.flat_quotes:
            for category in top_level_categories:
                if flat_quote['quote']['id'].startswith(category):
                    outcome.append(flat_quote)
                    break

        return outcome



