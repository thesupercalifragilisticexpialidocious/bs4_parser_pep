# Python documentation parsing

This module's scripts allow for automated collection of some top-level Python documentation data. Namely, it tracks notes on version releases, statuses of Python versions, and PEP statuses.

Three output modes are supported -- simple terminal output, pretty output, and csv.

usage: main.py [-h] [-c] [-o {pretty,file}]
               {pep,whats-new,latest-versions,download}

positional arguments:
  {pep,whats-new,latest-versions,download}
                        Funcional modes

optional arguments:
  -h, --help            show this help message and exit
  -c, --clear-cache     cache reset
  -o {pretty,file}, --output {pretty,file}
                        additional output modes ('ugly' stdout is default)
