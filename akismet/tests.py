import unittest

import os

from akismet import Akismet
from akismet.exceptions import AkismetServerError


class TestAkismet(unittest.TestCase):
    def setUp(self):
        try:
            akismet_api_key = os.environ['AKISMET_API_KEY']
        except KeyError:
            raise EnvironmentError('Provide AKISMET_API_KEY environment setting.')
        self.akismet = Akismet(akismet_api_key, is_test=True)

    def test_check(self):
        self.assertFalse(self.akismet.check('127.0.0.1', 'Test Agent', blog='http://127.0.0.1'))

    def test_check_spam(self):
        self.assertTrue(self.akismet.check('127.0.0.1', 'Test Agent', comment_author='viagra-test-123',
                                           blog='http://127.0.0.1'))

    def test_invalid_api_key(self):
        akismet = Akismet('invalid_api_key', is_test=True)
        with self.assertRaises(AkismetServerError):
            akismet.check('127.0.0.1', 'Test Agent', blog='http://127.0.0.1')

if __name__ == '__main__':
    unittest.main()
