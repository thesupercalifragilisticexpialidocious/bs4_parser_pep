from collections import Counter
from urllib.parse import urljoin
import logging
import re

from bs4 import BeautifulSoup
from requests_cache import CachedSession
from tqdm import tqdm
import requests


from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL, PEP_URL
from outputs import control_output
from utils import find_tag, get_response


class Pep:
    def __init__(self, number=None, url=None, preview_status=None,
                 actual_status=None, row=None, session=None):
        if not row:
            self.number = number
            self.url = url
            self.preview_status = preview_status
            self.actual_status = actual_status
            return
        a_tag = find_tag(row, 'a')
        self.number = int(a_tag.text)
        self.url = urljoin(PEP_URL, find_tag(row, 'a')['href'])
        self.preview_status = find_tag(row, 'abbr')['title'].split(', ')[-1]
        if session:
            response = get_response(session, self.url)
        else:
            response = requests.get(self.url)
        for dt in BeautifulSoup(response.text, features='lxml').find_all('dt'):
            if dt.text == 'Status:':
                self.actual_status = dt.next_sibling.next_sibling.string
                # next twice, because first next is an empty string
        if self.preview_status != self.actual_status:
            logging.info(f'Несовпадающий статус:\n{self.url}\n'
                         f'Статус в карточке: {self.actual_status}\n'
                         f'Статус в каталоге: {self.preview_status}')

    def __str__(self):
        return (f'{self.number}:{self.preview_status}/'
                f'{self.actual_status}[{self.url}]')


def pep(session):
    response = get_response(session, PEP_URL)
    if response is None:
        return
    peps = [Pep(row=row, session=session) for row in tqdm(find_tag(
        find_tag(
            BeautifulSoup(response.text, features='lxml'),
            id="numerical-index"
        ),
        'tbody',
    ).find_all('tr'))]
    counter = Counter(pep.actual_status for pep in peps)
    return list(counter.items()) + [('Total', sum(counter.values()))]
    # no total() as of 3.7


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', id='what-s-new-in-python')
    div_with_ul = find_tag(main_div, 'div', class_='toctree-wrapper')
    sections_by_python = div_with_ul.find_all('li', class_='toctree-l1')
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ').encode('utf-8')  # Polish letters!
        results.append((version_link, h1.text, dl_text))
    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        match = re.search(pattern, a_tag.text)
        if match:
            version, status = match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((link, version, status))
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')

    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag,
        'a',
        {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]

    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


MODE_TO_FUNCTION = {
    'pep': pep,
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    session = CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
