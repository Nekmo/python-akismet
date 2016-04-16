from __future__ import with_statement

import datetime
import sys
import os
from akismet import Akismet
from akismet.exceptions import AkismetServerError, MissingParameterError

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0'
EVIL_USER_AGENT = 'Bot Evil/0.1'


class TestAkismet(unittest.TestCase):
    akismet = None

    def setUp(self):
        try:
            akismet_api_key = os.environ['AKISMET_API_KEY']
        except KeyError:
            raise EnvironmentError('Provide AKISMET_API_KEY environment setting.')
        self.akismet = Akismet(akismet_api_key, is_test=True)

    def test_check(self):
        self.assertFalse(self.akismet.check('127.0.0.1', USER_AGENT, blog='http://127.0.0.1'))

    def test_check_spam(self):
        self.assertTrue(self.akismet.check('127.0.0.1', EVIL_USER_AGENT, comment_author='viagra-test-123',
                                           blog='http://127.0.0.1'))

    def test_invalid_api_key(self):
        akismet = Akismet('invalid_api_key', is_test=True)
        with self.assertRaises(AkismetServerError):
            akismet.check('127.0.0.1', EVIL_USER_AGENT, blog='http://127.0.0.1')

    def test_submit_spam(self):
        self.akismet.submit_spam('127.0.0.1', EVIL_USER_AGENT, blog='http://127.0.0.1')

    def test_submit_ham(self):
        self.akismet.submit_spam('127.0.0.1', USER_AGENT, blog='http://127.0.0.1')

    def test_datetime(self):
        blog_url = 'http://127.0.0.1'
        comment_date = datetime.datetime(2016, 4, 16, 15, 12, 5)
        comment_post_modified = datetime.datetime(2016, 4, 16, 16, 27, 31)
        data = self.akismet._get_parameters({'blog': blog_url, 'comment_post_modified': comment_post_modified,
                                             'comment_date': comment_date})
        for dtkey in ['comment_date', 'comment_post_modified']:
            self.assertIn('{0}_gmt'.format(dtkey), data)
            self.assertNotIn(dtkey, data)
            self.assertEqual(data['{0}_gmt'.format(dtkey)], locals()[dtkey].isoformat())

    def test_require_blog_param(self):
        with self.assertRaises(MissingParameterError):
            self.akismet._get_parameters({})


if __name__ == '__main__':
    unittest.main()
