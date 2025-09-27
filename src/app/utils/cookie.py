from http.cookies import SimpleCookie


def dict_to_cookie_str(cookie_dict):
    cookie = SimpleCookie()
    for key, value in cookie_dict.items():
        cookie[key] = value

    return "; ".join(
        [f"{key}={morsel.value}" for key, morsel in cookie.items()]
    )


def cookie_str_to_dict(cookie_str):
    cookie = SimpleCookie(cookie_str)
    cookies = {k: v.value for k, v in cookie.items()}

    return cookies
