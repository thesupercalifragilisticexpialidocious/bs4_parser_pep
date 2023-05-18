import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (BASE_DIR, DATETIME_FORMAT, EXPORT_OUTPUT_KEY,
                       FILE_NAME, NICE_CONSOLE_OUTPUT_KEY, RESULTS)

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
    results_dir = BASE_DIR / RESULTS
    results_dir.mkdir(exist_ok=True)
    file_path = results_dir / FILE_NAME.format(
        parser_mode=cli_args.mode,
        now=dt.datetime.now().strftime(DATETIME_FORMAT)
    )
    with open(file_path, 'w', encoding='utf-8') as f:
        csv.writer(f, dialect=csv.unix_dialect).writerows(results)
    logging.info(SAVE_MESSAGE.format(file_path=file_path))


OUTPUTS = {
    EXPORT_OUTPUT_KEY: file_output,
    NICE_CONSOLE_OUTPUT_KEY: pretty_output,
    None: default_output
}


def control_output(results, cli_args):
    OUTPUTS[cli_args.output](results, cli_args=cli_args)
