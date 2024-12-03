import unittest

from quotes_loader import QuotesLoader

class TestHistory(unittest.IsolatedAsyncioTestCase):
    def test_get_quotes_loader(self):
        quotes_loader = QuotesLoader('quotes-test')
        self.assertEqual(quotes_loader.categories, {'name': '', 'subcategories': {
            'category2': {
                'name': '',
                'subcategories': {},
                'quotes': {
                    'category2_quotes1_id1': {'text': 'quote1', 'source': 'author1', 'reference': 'reference1',
                                              'id': 'category2_quotes1_id1'},
                    'category2_quotes1_id2': {'text': 'quote2', 'source': 'author2', 'reference': 'reference2',
                                          'id': 'category2_quotes1_id2'}}},
            'category1': {
                'name': 'My Category 1',
              'subcategories': {
                  'sub1': {
                      'name': 'My Sub Category 1',
                      'subcategories': {},
                      'quotes': {
                          'category1_sub1_quotes1_id1': {
                              'text': 'quote1',
                              'source': 'author1',
                              'reference': 'reference1',
                              'id': 'category1_sub1_quotes1_id1'},
                          'category1_sub1_quotes1_id2': {
                              'text': 'quote2',
                              'source': 'author2',
                              'reference': 'reference2',
                              'id': 'category1_sub1_quotes1_id2'},
                          'category1_sub1_quotes2_id1': {
                              'text': 'quote1',
                              'source': 'author1',
                              'reference': 'reference1',
                              'id': 'category1_sub1_quotes2_id1'},
                          'category1_sub1_quotes2_id2': {
                              'text': 'quote2',
                              'source': 'author2',
                              'reference': 'reference2',
                              'id': 'category1_sub1_quotes2_id2'}
                      }
                  },
                'sub2': {
                    'name': 'My Sub Category 2',
                    'subcategories': {},
                    'quotes': {
                        'category1_sub2_quotes1_id1': {
                            'text': 'quote1',
                            'source': 'author1',
                            'reference': 'reference1',
                            'id': 'category1_sub2_quotes1_id1'},
                        'category1_sub2_quotes1_id2': {
                            'text': 'quote2',
                            'source': 'author2',
                            'reference': 'reference2',
                            'id': 'category1_sub2_quotes1_id2'}}}},
                  'quotes': {}}}, 'quotes': {}}
                         )

        self.assertEqual(quotes_loader.flat_quotes, [{'categories_path': ['category1', 'sub1'],
                                                      'quote': {'id': 'category1_sub1_quotes1_id1',
                                                                'reference': 'reference1',
                                                                'source': 'author1',
                                                                'text': 'quote1'}},
                                                     {'categories_path': ['category1', 'sub1'],
                                                      'quote': {'id': 'category1_sub1_quotes1_id2',
                                                                'reference': 'reference2',
                                                                'source': 'author2',
                                                                'text': 'quote2'}},
                                                     {'categories_path': ['category1', 'sub1'],
                                                      'quote': {'id': 'category1_sub1_quotes2_id1',
                                                                'reference': 'reference1',
                                                                'source': 'author1',
                                                                'text': 'quote1'}},
                                                     {'categories_path': ['category1', 'sub1'],
                                                      'quote': {'id': 'category1_sub1_quotes2_id2',
                                                                'reference': 'reference2',
                                                                'source': 'author2',
                                                                'text': 'quote2'}},
                                                     {'categories_path': ['category1', 'sub2'],
                                                      'quote': {'id': 'category1_sub2_quotes1_id1',
                                                                'reference': 'reference1',
                                                                'source': 'author1',
                                                                'text': 'quote1'}},
                                                     {'categories_path': ['category1', 'sub2'],
                                                      'quote': {'id': 'category1_sub2_quotes1_id2',
                                                                'reference': 'reference2',
                                                                'source': 'author2',
                                                                'text': 'quote2'}},
                                                     {'categories_path': ['category2'],
                                                      'quote': {'id': 'category2_quotes1_id1',
                                                                'reference': 'reference1',
                                                                'source': 'author1',
                                                                'text': 'quote1'}},
                                                     {'categories_path': ['category2'],
                                                      'quote': {'id': 'category2_quotes1_id2',
                                                                'reference': 'reference2',
                                                                'source': 'author2',
                                                                'text': 'quote2'}}])
