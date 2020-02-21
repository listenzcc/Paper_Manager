"""
HTTP server.
"""


import json
import urllib.parse
from local_profiles import profiles, logger
from http.server import HTTPServer, BaseHTTPRequestHandler
from worker import WORKER

worker = WORKER()
charset = 'charset=utf-8'


class HTTP_SERVER():
    def __init__(self, host, RequestHandler):
        self.server = HTTPServer(host, RequestHandler)
        logger.info('Starting server, listen at:{}:{}'.format(*host))
        logger.info('HTTP_SERVER initialized.')

    def start(self):
        try:
            logger.info('HTTP_SERVER starts.')
            self.server.serve_forever()
        except KeyboardInterrupt:
            logger.warning('Key interrupt.')
        finally:
            self.server.server_close()
            logger.info('HTTP_SERVER stopped.')


def text_message(message, content_type=None):
    """ Text message for local use """
    if content_type is None:
        content_type = f'text/plain; {charset}'
    return content_type, message


def handle_buffer_list():
    """ Handle buffer list require """
    names = worker.buffer_list()
    if names is not None:
        return f'application/json; {charset}', json.dumps(names)
    else:
        return text_message('Buffer list failed.')


def handle_buffer_name(name):
    """ Handle buffer name require, get file by [name] in buffer_server """
    bits = worker.buffer_get(name)
    if bits is not None:
        return f'application/pdf; {charset}', bits
    else:
        return text_message(f'Buffer get {name} failed')


def handle_buffer_commit(name, content):
    """ Handle buffer commit require, as [name] and [content] """
    # Parse content
    try:
        parsed_content = parse_content(content)
    except:
        return text_message(f'Parse content failed, content: {content}')
    # Commit
    success = worker.buffer_commit(name, parsed_content)
    # Return
    if success == 0:
        return text_message('Commit Success.')
    else:
        return text_message('Commit Fail. Buffer server failed on commit: name={name}, content={content}')


def parse_content(content):
    """ Parse [content] from post request.
        content: content from post request
    """
    # Resume `space`s
    # Raw '+' is '%2B' in content, so it is safe.
    content = content.replace(b'+', b' ')
    # Parse using urllib
    content = urllib.parse.unquote(content.decode())
    # Parse content into dict
    datas = dict()
    for e in content.split('&'):
        if not '=' in e:
            continue
        a, b = e.split('=', 1)
        datas[a] = b
    return datas


class RequestHandler(BaseHTTPRequestHandler):
    def send_response_content(self, content_type, content, allow_origin_access=True):
        """Send response content"""
        # Encode the content if require
        if not isinstance(content, bytes):
            content = content.encode('utf-8')
        # Send 200 OK
        code = 200
        self.send_response(code)
        # Allow origin access
        if allow_origin_access:
            self.send_header('Access-Control-Allow-Origin', '*')
        # Send header
        self.send_header('Content-Type', '{}'.format(content_type))
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        # Send content
        self.wfile.write(content)
        logger.info(f'Sent {code}, type={content_type}')

    def _parse_request_(self):
        """
        Builtin method to parse request from client browser.
        outputs:
            content_type: Content-Type of the response
            content: Content of the response in bits
        """
        # Parse raw path
        request = urllib.parse.urlparse(urllib.parse.unquote(self.path))
        path = request.path
        logger.info(f'HTTP_SERVER receives {request}')

        if path == '/favicon.ico':
            return text_message('NO ICON.')

        # Response
        query = request.query
        # Require Buffer server
        if path == '/[buffer]':
            # Require to list file names
            if query == 'list':
                return handle_buffer_list()

            # Require to pdf file as name
            if query.startswith('name='):
                name = query[len('name='):]
                return handle_buffer_name(name)

            # Commit new pdf file
            if query.startswith('commit&'):
                querys = query.split('&')
                name = querys[1][len('name='):]
                content = self.rfile.read(int(self.headers['content-length']))
                return handle_buffer_commit(name, content)

        # It means a failure if reach here
        logger.error(f'Something went wrong: path={path}, query={query}')
        return text_message('Something wrong.')

    def do_GET(self):
        """
        Override do_GET method to handle GET request.
        """
        logger.info('do_GET: {}'.format(self.path))
        content_type, content = self._parse_request_()
        self.send_response_content(content_type, content)
        # x = worker.open('buffer', '1-s2.0-S0028393217300593-main.pdf')
        # self.send_response_content('application/pdf', x)

    def do_POST(self):
        """
        Override do_POST method to handle POST request.
        """
        logger.info('do_POST: {}'.format(self.path))
        content_type, content = self._parse_request_()
        self.send_response_content(content_type, content)


if __name__ == '__main__':
    domain = 'localhost'
    port = 62019
    host = (domain, port)
    server = HTTP_SERVER(host, RequestHandler)
    server.start()
