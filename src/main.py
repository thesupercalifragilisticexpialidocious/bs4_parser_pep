from collections import Counter
from urllib.parse import urljoin
import logging
import re

from requests import RequestException
from requests_cache import CachedSession
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, DOWNLOADS, MAIN_DOC_URL, PEP_URL
from outputs import control_output
from utils import find_tag, make_soup

START = 'Парсер запущен!'
FINISH = 'Парсер завершил работу.'
DOWNLOAD_SUCCESS_MESSAGE = 'Архив был загружен и сохранён: {}'
FAILURE_MESSAGE = 'Аварийный выход: {}'
MISMATCH_MESSAGE = ('Несовпадающий статус:\n{}\n'
                    'Статус в карточке: {}\n'
                    'Статус в каталоге: {}')
SEARCH_ERROR = 'Ничего не нашлось'
SINGLE_PEP_LOAD_ERROR = 'PEP не прогрузился: {}'
SINGLE_VERSION_LOAD_ERROR = 'Карточка версии не прогрузилась: {}'


class Pep:
    def __init__(self, row=None, session=None):
        a_tag = find_tag(row, 'a')
        self.number = a_tag.text
        self.url = urljoin(PEP_URL, find_tag(row, 'a')['href'])
        self.preview_status = find_tag(row, 'abbr')['title'].split(', ')[-1]
        try:
            soup = make_soup(session, self.url)
        except RequestException as e:
            logging.exception(SINGLE_PEP_LOAD_ERROR(e))
            return
        for dt in soup.find_all('dt'):
            if dt.text == 'Status:':
                self.actual_status = dt.next_sibling.next_sibling.string
                # next twice, because first next is an empty line
        if self.preview_status != self.actual_status:
            logging.info(MISMATCH_MESSAGE.format(
                self.url,
                self.actual_status,
                self.preview_status
            ))

    def __str__(self):
        return (f'{self.number}:{self.preview_status}/'
                f'{self.actual_status}[{self.url}]')


def pep(session):
    with logging_redirect_tqdm():
        peps = [Pep(row=row, session=session) for row in tqdm(find_tag(
            find_tag(
                make_soup(session, PEP_URL),
                id="numerical-index"
            ),
            'tbody',
        ).find_all('tr'))]
    counter = Counter(pep.actual_status for pep in peps)
    return [
        ('Status', 'Number of PEPs'),
        *counter.items(),
        ('Total', sum(counter.values()))
    ]


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    with logging_redirect_tqdm():
        for section in tqdm(make_soup(session, whats_new_url).select(
            '#what-s-new-in-python div.toctree-wrapper li.toctree-l1'
        )):
            version_link = urljoin(
                whats_new_url,
                find_tag(section, 'a')['href']
            )
            try:
                soup = make_soup(session, version_link)
            except ConnectionError as e:
                logging.exception(SINGLE_VERSION_LOAD_ERROR.format(e))
            results.append((
                version_link,
                find_tag(soup, 'h1').text,
                find_tag(soup, 'dl').text.replace('\n', ' ').encode('utf-8')
            ))
    return results


def latest_versions(session):
    sidebar = find_tag(
        make_soup(session, MAIN_DOC_URL),
        'div',
        class_='sphinxsidebarwrapper'
    )
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise LookupError(SEARCH_ERROR)
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        match = re.search(pattern, a_tag.text)
        if match:
            version, status = match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((a_tag['href'], version, status))
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    archive_url = urljoin(
        downloads_url,
        make_soup(session, downloads_url).select_one(
            r'a[href$=pdf-a4\.zip]'
        )['href']
    )
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / DOWNLOADS
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(DOWNLOAD_SUCCESS_MESSAGE.format(archive_path))


MODE_TO_FUNCTION = {
    'pep': pep,
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
}


def main():
    configure_logging()
    logging.info(START)
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    try:
        session = CachedSession()
        if args.clear_cache:
            session.cache.clear()
        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results is not None:
            control_output(results, args)
    except Exception as e:
        logging.exception(FAILURE_MESSAGE.format(e))
    logging.info(FINISH)


if __name__ == '__main__':
    main()
