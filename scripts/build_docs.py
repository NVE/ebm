""" Build documents in docs/source, start webserver and open the most recent file in a browser

"""


import os
import pathlib
import webbrowser
from http.server import HTTPServer

from loguru import logger
from sphinx.cmd.build import build_main

from scripts.build_and_watch_docs import NoCacheHTTPRequestHandler

def find_most_recent_rst(directory):
    # Get all .rst files recursively
    rst_files = pathlib.Path(directory).rglob('*.rst')

    # Find the most recently changed file
    most_recent_file = max(rst_files, key=lambda f: f.stat().st_mtime, default=None)

    return most_recent_file


def main() -> int:
    source_directory = '..\\Energibruksmodell\\docs\\source'
    output_directory = pathlib.Path('output/html/')
    recent_rst = find_most_recent_rst(source_directory)

    # Find path and name of the same document as HTML.
    file_path = recent_rst.relative_to(source_directory).with_suffix('.html')

    result = build_main(argv=[source_directory, str(output_directory)])
    logger.info('Most recently changed file', recent_rst)
    if result == 0:
        # Start the web server
        os.chdir(output_directory)
        server_address = ('', 8000)
        httpd = HTTPServer(server_address, NoCacheHTTPRequestHandler)
        logger.info(f"Serving on http://localhost:8000")

        # Open index.html in the default web browser
        url = f'http://localhost:8000/{file_path}'
        logger.info(f'Opening  {url}')
        webbrowser.open(url)

        # Serve until interrupted
        httpd.serve_forever()
    else:
        logger.error(f'Sphinx build returned error code  {result}')
    return result


if __name__ == '__main__':
    raise SystemExit(main())