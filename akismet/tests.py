from __future__ import with_statement

import datetime
import sys
import os

try:
    from urllib.parse import parse_qsl
except ImportError:
    from urlparse import parse_qsl

import requests
import requests_mock
from requests.exceptions import ConnectTimeout

from akismet import Akismet, SpamStatus, AKISMET_CHECK_URL, AKISMET_DOMAIN, AKISMET_VERSION, AKISMET_SUBMIT_SPAM_URL, \
    AKISMET_SUBMIT_HAM_URL
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
        self.api_key = 'mock'
        self.is_test = True
        self.blog = 'http://127.0.0.1'
        self.user_ip = '127.0.0.1'
        self.akismet = Akismet('mock', is_test=self.is_test)
        self.mock = requests_mock.Mocker()
        self.mock.start()

    def tearDown(self):
        self.mock.stop()

    def _get_url(self, url_format, api_key=None):
        return url_format.format(
            protocol='https',
            api_key=api_key or self.api_key,
            domain=AKISMET_DOMAIN,
            version=AKISMET_VERSION,
        )

    def _get_default_parameters(self):
        return {
            'user_ip': self.user_ip,
            'referrer': 'unknown',
            'user_agent': USER_AGENT,
            'charset': Akismet.charset,
            'is_test': str(self.is_test),
            'blog': self.blog,
        }

    def test_check(self):
        parameters = dict(self._get_default_parameters(), user_agent=USER_AGENT)
        self.mock.post(self._get_url(AKISMET_CHECK_URL), json=False,
                       additional_matcher=lambda request: dict(parse_qsl(request.text)) == parameters)
        self.assertEqual(self.akismet.check(self.user_ip, USER_AGENT, blog=self.blog), SpamStatus.Ham)

    def test_check_spam(self):
        comment_author = 'viagra-test-123'
        parameters = dict(self._get_default_parameters(), user_agent=EVIL_USER_AGENT,
                          comment_author=comment_author)
        self.mock.post(self._get_url(AKISMET_CHECK_URL), json=True,
                       additional_matcher=lambda request: dict(parse_qsl(request.text)) == parameters)
        self.assertEqual(self.akismet.check(self.user_ip, EVIL_USER_AGENT, comment_author=comment_author,
                                            blog=self.blog), SpamStatus.ProbableSpam)

    def test_invalid_api_key(self):
        api_key = 'invalid_api_key'
        self.mock.post(self._get_url(AKISMET_CHECK_URL, api_key=api_key), text='')
        akismet = Akismet(api_key, is_test=True)
        with self.assertRaises(AkismetServerError):
            akismet.check(self.user_ip, EVIL_USER_AGENT, blog=self.blog)

    def test_submit_spam(self):
        parameters = dict(self._get_default_parameters(), user_agent=EVIL_USER_AGENT, is_spam='True')
        self.mock.post(self._get_url(AKISMET_SUBMIT_SPAM_URL), text="Thanks for making the web a better place.",
                       additional_matcher=lambda request: dict(parse_qsl(request.text)) == parameters)
        self.akismet.submit_spam(self.user_ip, EVIL_USER_AGENT, blog=self.blog)

    def test_submit_ham(self):
        parameters = dict(self._get_default_parameters(), user_agent=USER_AGENT, is_spam='False')
        self.mock.post(self._get_url(AKISMET_SUBMIT_HAM_URL), text="Thanks for making the web a better place.",
                       additional_matcher=lambda request: dict(parse_qsl(request.text)) == parameters)
        self.akismet.submit_ham(self.user_ip, USER_AGENT, blog=self.blog)

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

    def test_timeout(self):
        self.mock.post(self._get_url(AKISMET_SUBMIT_HAM_URL), exc=ConnectTimeout)

        with self.assertRaises(requests.ConnectionError):
            self.akismet.submit_ham(self.user_ip, USER_AGENT, blog=self.blog)

    def test_require_blog_param(self):
        with self.assertRaises(MissingParameterError):
            self.akismet._get_parameters({})


if __name__ == '__main__':
    unittest.main()
