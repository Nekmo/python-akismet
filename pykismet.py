import requests

# Akismet Settings
AKISMET_USER_AGENT = "Pykismet/0.0.0"

# API URIs
AKISMET_CHECK_URL = "rest.akismet.com/1.1/comment-check"

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

# Custom Exceptions
class AkismetError(Exception):
    pass

class MissingApiKeyError(AkismetError):
    pass

class MissingParameterError(AkismetError):
    pass

class ExtraParametersError(AkismetError):
    pass

class AkismetServerError(AkismetError):
    pass

# The main Akismet class
class Akismet:
    def __init__(self, api_key=None, blog_url=None, user_agent=None):
        self.api_key = api_key
        self.blog_url = blog_url
        self.user_agent = user_agent+" | "+AKISMET_USER_AGENT

    # Queries Akismet to find out whether the comment is ham or spam
    # Returns: True (for Spam)
    #          False (for Ham)
    def check(self, parameters):

        # Check if the API key is set
        if self.api_key is None:
            raise MissingApiKeyError("api_key must be set on the akismet object before calling any API methods.")
        
        # Throw appropriate exception if any mandatory parameters are missing
        if not 'blog' in parameters:
            if self.blog_url is None:
                raise MissingParameterError("blog is a required parameter if blog_url is not set on the akismet object")
            parameters['blog'] = self.blog_url
        if not 'user_ip' in parameters:
            raise MissingParameterError("user_ip is a required parameter")
        if not 'user_agent' in parameters:
            raise MissingParameterError("user_agent is a required parameter")
        if not 'referrer' in parameters:
            raise MissingParameterError("referrer is a required parameter")
        
        # Check for any invalid extra parameters
        leftovers = set(parameters.keys()).difference_update(AKISMET_CHECK_VALID_PARAMETERS)
        if leftovers and leftovers.count() != 0:
            raise ExtraParametersError("The following unrecognised parameters were supplied:"+str(leftovers))

        # Build the HTTP Headers for the Akismet query
        headers = {
                "User-Agent": AKISMET_USER_AGENT,
        }

        # Construct the GET request to akismet.
        r = requests.post("http://"+self.api_key+"."+AKISMET_CHECK_URL, data=parameters, headers=headers)

        # Deal with the response
        if r.text == "false":
            return False
        elif r.text == "true":
            return True
        else:
            raise AkismetServerError("Akismet server returned an error: "+r.text)

