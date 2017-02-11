import datetime
from akismet.exceptions import AkismetServerError, MissingParameterError

__version__ = '0.3.0'

PYTHON_AKISMET_USER_AGENT = "Python-Akismet/{0}".format(__version__)

# API URIs
AKISMET_PROTOCOL = 'https'
AKISMET_DOMAIN = 'rest.akismet.com'
AKISMET_VERSION = '1.1'
AKISMET_CHECK_URL = "{protocol}://{api_key}.{domain}/{version}/comment-check"
AKISMET_SUBMIT_SPAM_URL = "{protocol}://{api_key}.{domain}/{version}/submit-spam"
AKISMET_SUBMIT_HAM_URL = "{protocol}://{api_key}.{domain}/{version}/submit-ham"


def remove_self(params):
    params = dict(params)
    del params['self']
    return params


class Akismet:
    charset = 'utf-8'
    protocol = AKISMET_PROTOCOL
    domain = AKISMET_DOMAIN
    version = AKISMET_VERSION

    def __init__(self, api_key, blog=None, application_user_agent=None, is_test=False):
        self.api_key = api_key
        self.blog = blog
        self.is_test = is_test
        self.user_agent = '{0} | {1}'.format(application_user_agent or 'Unknown Application/0.0.0',
                                             PYTHON_AKISMET_USER_AGENT)

    def _get_parameters(self, data):
        data.pop('self', None)
        data = dict((key, value) for key, value in data.items() if value is not None)
        data['is_test'] = data.get('is_test') or self.is_test
        data['charset'] = self.charset
        if 'blog' not in data and not self.blog:
            raise MissingParameterError("blog is a required parameter if blog is not set on the akismet object")
        elif 'blog' not in data:
            data['blog'] = self.blog
        for dt_param in ['comment_date', 'comment_post_modified']:
            value = data.pop(dt_param, None)
            if not value:
                continue
            assert type(value) is datetime.datetime
            data[dt_param + '_gmt'] = value.isoformat()
        return data

    def _request(self, url, parameters, headers=None):
        import requests
        headers = headers or self.get_headers()
        return requests.post(url, data=parameters, headers=headers)

    def get_url(self, url):
        return url.format(protocol=self.protocol, api_key=self.api_key, domain=self.domain, version=self.version)

    def get_check_url(self):
        return self.get_url(AKISMET_CHECK_URL)

    def get_submit_spam_url(self):
        return self.get_url(AKISMET_SUBMIT_SPAM_URL)

    def get_submit_ham_url(self):
        return self.get_url(AKISMET_SUBMIT_HAM_URL)

    def get_headers(self):
        return {
            "User-Agent": self.user_agent,
        }

    def check(self, user_ip, user_agent, comment_author=None, comment_author_email=None, comment_author_url=None,
              comment_content=None, referrer='unknown', blog=None, permalink=None, comment_type=None, blog_lang=None,
              comment_date=None, comment_post_modified=None, user_role=None, is_test=False):
        parameters = self._get_parameters(locals())
        r = self._request(self.get_check_url(), parameters)
        try:
            return r.json()
        except ValueError:
            raise AkismetServerError("Akismet server returned an error: {0}".format(
                r.headers.get('X-akismet-debug-help') or r.text
            ))

    def submit_spam(self, user_ip, user_agent, comment_author=None, comment_author_email=None,
                    comment_author_url=None, comment_content=None, referrer='unknown', blog=None, permalink=None,
                    comment_type=None, is_test=False, blog_lang=None, comment_date=None, comment_post_modified=None,
                    user_role=None):
        self.submit(True, **remove_self(locals()))

    def submit_ham(self, user_ip, user_agent, comment_author=None, comment_author_email=None,
                   comment_author_url=None, comment_content=None, referrer='unknown', blog=None, permalink=None,
                   comment_type=None, is_test=False, blog_lang=None, comment_date=None, comment_post_modified=None,
                   user_role=None):
        self.submit(False, **remove_self(locals()))

    def submit(self, is_spam, user_ip, user_agent, comment_author=None, comment_author_email=None,
               comment_author_url=None, comment_content=None, referrer='unknown', blog=None, permalink=None,
               comment_type=None, is_test=False, blog_lang=None, comment_date=None, comment_post_modified=None,
               user_role=None):
        parameters = self._get_parameters(locals())
        r = self._request(self.get_submit_spam_url() if is_spam else self.get_submit_ham_url(), parameters)
        if r.text != "Thanks for making the web a better place.":
            raise AkismetServerError("Akismet server returned an error: {0}".format(r.text))
