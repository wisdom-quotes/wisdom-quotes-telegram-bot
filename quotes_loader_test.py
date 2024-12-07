import unittest

from quotes_loader import QuotesLoader

class TestHistory(unittest.IsolatedAsyncioTestCase):

    def test_loading_fine(self):
        QuotesLoader('quotes')
        self.assertEqual(0, 0)

    def test_get_quotes_loader(self):
        quotes_loader = QuotesLoader('quotes-test')
        self.maxDiff = None
        self.assertEqual(quotes_loader.categories, {'name': '',
                                                    'quotes': {},
                                                    'subcategories': {'ru': {'name': '',
                                                                             'quotes': {},
                                                                             'subcategories': {'category1': {'name': 'My Category '
                                                                                                                     '1',
                                                                                                             'quotes': {},
                                                                                                             'subcategories': {'sub1': {'name': 'My '
                                                                                                                                                'Sub '
                                                                                                                                                'Category '
                                                                                                                                                '1',
                                                                                                                                        'quotes': {'ru_category1_sub1_quotes1_id1': {'id': 'ru_category1_sub1_quotes1_id1',
                                                                                                                                                                                     'reference': 'reference1',
                                                                                                                                                                                     'text': 'quote1'},
                                                                                                                                                   'ru_category1_sub1_quotes1_id2': {'id': 'ru_category1_sub1_quotes1_id2',
                                                                                                                                                                                     'reference': 'reference2',
                                                                                                                                                                                     'text': 'quote2'},
                                                                                                                                                   'ru_category1_sub1_quotes2_id1': {'id': 'ru_category1_sub1_quotes2_id1',
                                                                                                                                                                                     'reference': 'reference1',
                                                                                                                                                                                     'text': 'quote1'},
                                                                                                                                                   'ru_category1_sub1_quotes2_id2': {'id': 'ru_category1_sub1_quotes2_id2',
                                                                                                                                                                                     'reference': 'reference2',
                                                                                                                                                                                     'text': 'quote2'}},
                                                                                                                                        'subcategories': {}},
                                                                                                                               'sub2': {'name': 'My '
                                                                                                                                                'Sub '
                                                                                                                                                'Category '
                                                                                                                                                '2',
                                                                                                                                        'quotes': {'ru_category1_sub2_quotes1_id1': {'id': 'ru_category1_sub2_quotes1_id1',
                                                                                                                                                                                     'reference': 'reference1',
                                                                                                                                                                                     'text': 'quote1'},
                                                                                                                                                   'ru_category1_sub2_quotes1_id2': {'id': 'ru_category1_sub2_quotes1_id2',
                                                                                                                                                                                     'reference': 'reference2',
                                                                                                                                                                                     'text': 'quote2'}},
                                                                                                                                        'subcategories': {}}}},
                                                                                               'category2': {'name': '',
                                                                                                             'quotes': {'ru_category2_quotes1_id1': {'id': 'ru_category2_quotes1_id1',
                                                                                                                                                     'reference': 'reference1',
                                                                                                                                                     'text': 'quote1'},
                                                                                                                        'ru_category2_quotes1_id2': {'id': 'ru_category2_quotes1_id2',
                                                                                                                                                     'reference': 'reference2',
                                                                                                                                                     'text': 'quote2'}},
                                                                                                             'subcategories': {}}}}}})

        self.assertEqual(quotes_loader.flat_quotes, [{'categories_path': ['ru', 'category1', 'sub1'],
                                                      'quote': {'id': 'ru_category1_sub1_quotes1_id1',
                                                                'reference': 'reference1',
                                                                'text': 'quote1'}},
                                                     {'categories_path': ['ru', 'category1', 'sub1'],
                                                      'quote': {'id': 'ru_category1_sub1_quotes1_id2',
                                                                'reference': 'reference2',
                                                                'text': 'quote2'}},
                                                     {'categories_path': ['ru', 'category1', 'sub1'],
                                                      'quote': {'id': 'ru_category1_sub1_quotes2_id1',
                                                                'reference': 'reference1',
                                                                'text': 'quote1'}},
                                                     {'categories_path': ['ru', 'category1', 'sub1'],
                                                      'quote': {'id': 'ru_category1_sub1_quotes2_id2',
                                                                'reference': 'reference2',
                                                                'text': 'quote2'}},
                                                     {'categories_path': ['ru', 'category1', 'sub2'],
                                                      'quote': {'id': 'ru_category1_sub2_quotes1_id1',
                                                                'reference': 'reference1',
                                                                'text': 'quote1'}},
                                                     {'categories_path': ['ru', 'category1', 'sub2'],
                                                      'quote': {'id': 'ru_category1_sub2_quotes1_id2',
                                                                'reference': 'reference2',
                                                                'text': 'quote2'}},
                                                     {'categories_path': ['ru', 'category2'],
                                                      'quote': {'id': 'ru_category2_quotes1_id1',
                                                                'reference': 'reference1',
                                                                'text': 'quote1'}},
                                                     {'categories_path': ['ru', 'category2'],
                                                      'quote': {'id': 'ru_category2_quotes1_id2',
                                                                'reference': 'reference2',
                                                                'text': 'quote2'}}])

    def test_filter_by_top_category(self):
        quotes_loader = QuotesLoader('quotes-test')
        self.assertEqual(quotes_loader.filter_by_top_category(['ru_category1']), [{'categories_path': ['ru', 'category1', 'sub1'],
                                                                                   'quote': {'id': 'ru_category1_sub1_quotes1_id1',
                                                                                             'reference': 'reference1',
                                                                                             'text': 'quote1'}},
                                                                                  {'categories_path': ['ru', 'category1', 'sub1'],
                                                                                   'quote': {'id': 'ru_category1_sub1_quotes1_id2',
                                                                                             'reference': 'reference2',
                                                                                             'text': 'quote2'}},
                                                                                  {'categories_path': ['ru', 'category1', 'sub1'],
                                                                                   'quote': {'id': 'ru_category1_sub1_quotes2_id1',
                                                                                             'reference': 'reference1',
                                                                                             'text': 'quote1'}},
                                                                                  {'categories_path': ['ru', 'category1', 'sub1'],
                                                                                   'quote': {'id': 'ru_category1_sub1_quotes2_id2',
                                                                                             'reference': 'reference2',
                                                                                             'text': 'quote2'}},
                                                                                  {'categories_path': ['ru', 'category1', 'sub2'],
                                                                                   'quote': {'id': 'ru_category1_sub2_quotes1_id1',
                                                                                             'reference': 'reference1',
                                                                                             'text': 'quote1'}},
                                                                                  {'categories_path': ['ru', 'category1', 'sub2'],
                                                                                   'quote': {'id': 'ru_category1_sub2_quotes1_id2',
                                                                                             'reference': 'reference2',
                                                                                             'text': 'quote2'}}])