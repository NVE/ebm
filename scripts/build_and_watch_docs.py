""" Build documents in docs/source, start webserver and watch for changes

Requires watchdog:
```
  python -m pip install watchdog
```

"""

import os
import pathlib
import webbrowser
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler

from loguru import logger
from sphinx.cmd.build import build_main
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class NoCacheHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()


class RebuildHandler(FileSystemEventHandler):
    def __init__(self, build_func, server, source_directory):
        self.build_func = build_func
        self.server = server
        self.source_directory = source_directory
        self.last_file = None
        self.always_open = True

    def on_modified(self, event):
        if event.src_path.endswith('.rst'):
            logger.info(f"{event.src_path} has been modified. Rebuilding...")
            # self.server.shutdown()
            changed_path = pathlib.Path(event.src_path)
            target = changed_path.relative_to(self.source_directory).with_suffix('.html')
            raise_window = True
            if not self.last_file or self.last_file != target:
                self.last_file = target
            else:
                raise_window = self.always_open
                # target = None
            self.build_func(source_directory=self.source_directory,
                            file_to_open=target, auto_raise=raise_window)
            # start_server(self.server)

def build_docs(output_directory, source_directory, server_port=8000, file_to_open='index.html', auto_raise=True):
    logger.info(f'building to {output_directory}')
    result = build_main(argv=[str(source_directory), str(output_directory)])
    if result == 0:
        logger.info(f"Build successful. {auto_raise=}")
        if file_to_open:
            webbrowser.open(f'http://localhost:{server_port}/{file_to_open}', new=2,
                            autoraise=auto_raise)
    else:
        logger.error("Build failed.")
    return result

def make_server(output_directory):
    os.chdir(output_directory)
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, NoCacheHTTPRequestHandler)
    return httpd

def start_server(httpd):
    logger.info(f"Serving on http://localhost:{httpd.server_port}")
    webbrowser.open(f'http://localhost:{httpd.server_port}/index.html')
    httpd.serve_forever()

def main() -> int:
    output_directory = pathlib.Path('output/html/').absolute()
    source_directory = pathlib.Path('..\\Energibruksmodell\\docs\\source').absolute()
    result = build_docs(output_directory, source_directory)
    httpd = make_server(output_directory)

    if result == 0:
        event_handler = RebuildHandler(partial(build_docs, output_directory=output_directory, server_port=httpd.server_port), httpd, source_directory)
        observer = Observer()
        observer.schedule(event_handler, path=source_directory, recursive=True)
        observer.start()
        try:
            start_server(httpd)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    return result

if __name__ == '__main__':
    raise SystemExit(main())
