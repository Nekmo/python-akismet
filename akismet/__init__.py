import datetime
import requests

from akismet.exceptions import AkismetError, InternalPykismetError, MissingApiKeyError, MissingParameterError, \
    ExtraParametersError, AkismetServerError


__version__ = '0.1.0'

PYTHON_AKISMET_USER_AGENT = "Python-Akismet/{0}".format(__version__)

# API URIs
AKISMET_PROTOCOL = 'https'
AKISMET_DOMAIN = 'rest.akismet.com'
AKISMET_VERSION = '1.1'
AKISMET_CHECK_URL = "{protocol}://{api_key}.{domain}/{version}/comment-check"
AKISMET_SUBMIT_SPAM_URL = "{protocol}://{api_key}.{domain}/{version}/submit-spam"
AKISMET_SUBMIT_HAM_URL = "{protocol}://{api_key}.{domain}/{version}/submit-ham"

# API Permitted parameter lists
AKISMET_CHECK_VALID_PARAMETERS = {
        'blog',
        'user_ip',
        'user_agent',
        'referrer',
        'permalink',
        'content_type',
        'comment_author',
        'comment_author_email',
        'comment_author_url',
        'comment_content',
        'comment_date_gmt',
        'comment_post_modified_gmt',
        'blog_lang',
        'blog_charset',
        'is_test',
}

AKISMET_SUBMIT_SPAM_VALID_PARAMETERS = AKISMET_CHECK_VALID_PARAMETERS
AKISMET_SUBMIT_HAM_VALID_PARAMETERS = AKISMET_CHECK_VALID_PARAMETERS


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
        del data['self']
        data = dict((key, value) for key, value in data.items() if value is not None)
        if not 'blog' in data and not self.blog:
            raise MissingParameterError("blog is a required parameter if blog is not set on the akismet object")
        elif not 'blog' in data:
            data['blog'] = self.blog
        for dt_param in ['comment_date_gmt', 'comment_post_modified_gmt']:
            value = data.pop(dt_param, None)
            if not value:
                continue
            assert type(value) is datetime.datetime
            data[dt_param + '_gmt'] = value.isoformat()
        return data

    def get_url(self, url):
        return url.format(protocol=self.protocol, api_key=self.api_key, domain=self.domain, version=self.version)

    def get_check_url(self):
        return self.get_url(AKISMET_CHECK_URL)

    def get_headers(self):
        return {
            "User-Agent": self.user_agent,
        }

    def check(self, user_ip, user_agent, comment_author=None, comment_author_email=None, comment_author_url=None,
              comment_content=None, referrer='unknown', blog=None, permalink=None, comment_type=None, blog_lang=None,
              comment_date=None, comment_post_modified=None, user_role=None, is_test=False):
        parameters = self._get_parameters(locals())
        r = requests.post(self.get_check_url(), data=parameters, headers=self.get_headers())
        try:
            return r.json()
        except ValueError:
            raise AkismetServerError("Akismet server returned an error: {0}".format(
                r.headers.get('X-akismet-debug-help') or r.text
            ))

    def submit_spam(self, parameters):
        self.submit("spam", parameters)

    def submit_ham(self, parameters):
        self.submit("ham", parameters)

    def submit(self, t, parameters):

        # Check if the API key is set
        if self.api_key is None:
            raise MissingApiKeyError("api_key must be set on the akismet object before calling any API methods.")

        # Throw appropriate exception if any mandatory parameters are missing
        if not 'blog' in parameters:
            if self.blog is None:
                raise MissingParameterError("blog is a required parameter if blog is not set on the akismet object")
            parameters['blog'] = self.blog
        if not 'user_ip' in parameters:
            raise MissingParameterError("user_ip is a required parameter")
        if not 'user_agent' in parameters:
            raise MissingParameterError("user_agent is a required parameter")

        # Check for any invalid extra parameters
        if t is "spam":
            leftovers = set(parameters.keys()).difference_update(AKISMET_SUBMIT_SPAM_VALID_PARAMETERS)
        elif t is "ham":
            leftovers = set(parameters.keys()).difference_update(AKISMET_SUBMIT_HAM_VALID_PARAMETERS)
        else:
            raise InternalPykismetError("submit called with invalid t")

        if leftovers and leftovers.count() != 0:
            raise ExtraParametersError("The following unrecognised parameters were supplied:" + str(leftovers))

        # Build the HTTP Headers for the Akismet query
        headers = {
                "User-Agent": self.user_agent,
        }

        # Construct the GET request to akismet.
        if t is "spam":
            url = "http://"+self.api_key+"."+AKISMET_SUBMIT_SPAM_URL
        elif t is "ham":
            url = "http://"+self.api_key+"."+AKISMET_SUBMIT_HAM_URL
        else:
            raise InternalPykismetError("submit called with invalid t")

        r = requests.post(url, data=parameters, headers=headers)

        # Deal with the response
        if r.text == "Thanks for making the web a better place.":
            return
        else:
            raise AkismetServerError("Akismet server returned an error: "+r.text)

