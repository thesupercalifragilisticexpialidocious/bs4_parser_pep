from pathlib import Path

# PEP web resources
MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_URL = 'https://peps.python.org/'

# file routing and management
BASE_DIR = Path(__file__).parent
DOWNLOADS_DIR = BASE_DIR / 'downloads'
RESULTS_DIR = BASE_DIR / 'results'
FILE_NAME = '{parser_mode}_{now}.csv'
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'parser.log'
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

# PEP parsing logic
EXPECTED_STATUS = {  # should be plural
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
