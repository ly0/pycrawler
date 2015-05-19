import requests.cookies
import Cookie

def cookie_to_dict(cookie):
    cookie_dict = dict()
    C = Cookie.Cookie(cookie)

    for morsel in C.values():
        cookie_dict[morsel.key] = morsel.value

    return cookie_dict

def dict_to_cookie(cookie_dict):
    attrs = []

    for (key, value) in cookie_dict.items():
        attrs.append("%s=%s" % (key, value))

    return "; ".join(attrs)

def make_cookiejar(cookiejar, request, response):
    """Returns cookie string by tonado AsyncHTTPClient's request and response
    :param cookiejar:
    :type cookiejar: request.cookie.RequestsCookiejar
    :param request: class:tornado.httpclient.HTTPRequest
    :param response: class:tornado.httpclient.HTTPResponse
    """

    if request and request.headers.get("Cookie"):
        request_cookie = request.headers.get("Cookie")
        if type("") != type(request_cookie):
            request_cookie = request_cookie.encode("utf-8")
        cookie_dict = cookie_to_dict(request_cookie)
        requests.cookies.cookiejar_from_dict(cookie_dict, cookiejar)

    for sc in response.headers.get_list("Set-Cookie"):
        C = Cookie.SimpleCookie(sc)
        for morsel in C.values():
            if morsel['max-age']:
                morsel['max-age'] = float(morsel['max-age'])

            cookie = requests.cookies.morsel_to_cookie(morsel)
            cookiejar.set_cookie(cookie)
    cookie_dict = cookiejar.get_dict(path="/")

    return dict_to_cookie(cookie_dict)