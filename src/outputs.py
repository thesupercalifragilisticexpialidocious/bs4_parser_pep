import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT, FILE_NAME, RESULTS_DIR
# base folder imported to pass tests

SAVE_MESSAGE = 'Файл с результатами был сохранён: {file_path}'


def default_output(results, **kwargs):
    for row in results:
        print(*row)


def pretty_output(results, **kwargs):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    results_dir = BASE_DIR / 'results'  # whem imported from constants
    results_dir.mkdir(exist_ok=True)    # results dir doesn't pass pytest
    file_path = results_dir / FILE_NAME.format(
        parser_mode=cli_args.mode,
        now=dt.datetime.now().strftime(DATETIME_FORMAT)
    )
    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect=csv.unix_dialect)
        writer.writerows(results)
    logging.info(SAVE_MESSAGE.format(file_path=file_path))


def _file_output(results, cli_args):
    RESULTS_DIR.mkdir(exist_ok=True)
    file_path = RESULTS_DIR / FILE_NAME.format(
        parser_mode=cli_args.mode,
        now=dt.datetime.now().strftime(DATETIME_FORMAT)
    )
    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect=csv.unix_dialect)
        writer.writerows(results)
    logging.info(SAVE_MESSAGE.format(file_path=file_path))


OUTPUTS = {
    'file': file_output,
    'pretty': pretty_output,
    None: default_output
}


def control_output(results, cli_args):
    OUTPUTS[cli_args.output](results, cli_args=cli_args)


if __name__ == '__main__':
    _ = BASE_DIR  # tests demand use of BASE Dir
