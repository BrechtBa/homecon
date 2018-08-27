#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from multiprocessing import Process


logger = logging.getLogger(__name__)


_document_root = os.path.join(sys.prefix, 'var', 'www', 'homecon')
_http_server = None


class HttpRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        logger.debug('GET {}'.format(self.path))
        if '.' in self.path:
            # if an extension is supplied return the file
            if '?' in self.path:
                splitpath = self.path.split('?')
                temppath = splitpath[0][1:]
            else:
                temppath = self.path[1:]

            abspath = os.path.abspath(os.path.join(_document_root, temppath))
        else:
            # else return index.html
            abspath = os.path.abspath(os.path.join(_document_root, 'index.html'))

        _, ext = os.path.splitext(abspath)
        ext = ext.lower()
        content_type = {
            '.css': 'text/css',
            '.gif': 'image/gif',
            '.html': 'text/html',
            '.jpeg': 'image/jpeg',
            '.jpg': 'image/jpg',
            '.js': 'text/javascript',
            '.png': 'image/png',
            '.text': 'text/plain',
            '.txt': 'text/plain',
        }

        # If it is a known extension, set the correct content type
        if ext in content_type:
            if os.path.exists(abspath):
                self.send_response(200)
                self.send_header('Content-type', content_type[ext])
                self.end_headers()

                with open(abspath, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, 'File Not Found: {}'.format(self.path))
        return


class HttpServer(object):
    def __init__(self, address='0.0.0.0', port=12300, document_root=_document_root):
        """

        Parameters
        ----------
        address : str
            The ip-address to serve on.

        port : int
            The port to serve on.

        document_root : str
            The root path from where files are retrieved.
            Defaults to :code:`/var/www/homecon`.

        """
        self.name = 'HttpServer'
        self.address = address
        self.port = port
        self.document_root = document_root
        self.http_server = None
        self.process = None

    def _run(self):
        global _document_root
        _document_root = self.document_root
        try:
            self.http_server = HTTPServer((self.address, self.port), HttpRequestHandler)
            logger.info('Running the HomeCon http server at {}:{}'.format(self.address, self.port))
            self.http_server.serve_forever()
        except KeyboardInterrupt:
            self.http_server.shutdown()
            self.http_server.socket.close()

    def start(self):
        self.process = Process(target=self._run, name='HTTPServer')
        self.process.start()

    def stop(self):
        self.process.join()
        logger.info('HomeCon http server stopped')
