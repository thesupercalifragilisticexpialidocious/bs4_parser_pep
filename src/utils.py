from requests import RequestException

from bs4 import BeautifulSoup

from exceptions import ParserFindTagException

LOAD_ERROR_MESSAGE = 'Возникла ошибка при загрузке страницы {}'
SEARCH_ERROR_MESSAGE = 'Не найден тег {tag} {attrs} {kwargs}'


def get_response(session, url, encoding='utf-8'):
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException:
        raise RequestException(
            LOAD_ERROR_MESSAGE.format(url),
            stack_info=True
        )


def find_tag(soup, tag=None, attrs=None, **kwargs):
    searched_tag = soup.find(tag, attrs=(attrs or {}), **kwargs)
    if searched_tag is None:
        raise ParserFindTagException(SEARCH_ERROR_MESSAGE.format(
            tag=tag,
            attrs=attrs,
            kwargs=kwargs
        ))
    return searched_tag

def make_soup(session, url, features='lxml'):
    return BeautifulSoup(get_response(session, url).text, features=features)
