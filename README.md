# Python documentation parsing

This module's scripts allow for automated collection of some top-level Python documentation data. Namely, it tracks notes on version releases, statuses of Python versions, and PEP statuses.

Three output modes are supported -- simple terminal output, pretty output, and csv.

The project is built upon BeautifulSoup, request-cache, and tqdm libraries.

To run the script install dependencies in a virtual environment `pip install -r requirements.txt`, then launch `src/main.py *mode*`

```
usage: main.py [-h] [-c] [-o {pretty,file}]s
               {pep,whats-new,latest-versions,download}

positional arguments:
  {pep,whats-new,latest-versions,download}
                        Funcional modes

optional arguments:
  -h, --help            show this help message and exit
  -c, --clear-cache     cache reset
  -o {pretty,file}, --output {pretty,file}
                        additional output modes ('ugly' stdout is default)
```

github.com/thesupercalifragilisticexpialidocious, 2023.
