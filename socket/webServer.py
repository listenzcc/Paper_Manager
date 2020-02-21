import socket
import urllib.parse
import sys
import json
import _thread
sys.path.append('..')
from local_profiles import logger  # noqa
from worker import WORKER  # noqa


# Profiles
worker = WORKER()
charset = 'utf-8'


class WEBSERVER():
    def __init__(self, ip='localhost', port=8612):
        self.running = True
        logger.info("WEBSERVER initialized.")

    def run(self, ip='localhost', port=8612):
        """ Run socket listening on [ip]:[port] """
        # Setup socket listener
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((ip, port))
        sock.listen(1)
        logger.info(f'WEBSERVER listen on {ip}:{port}')
        # Serving
        idx = 0
        try:
            while self.running:
                # Accept new connection
                connection, client_address = sock.accept()
                logger.info(
                    f'WEBSERVER is connected {connection} from {client_address}.')
                _thread.start_new_thread(serve_connection, (connection, client_address, idx))
                idx += 1
        except KeyboardInterrupt:
            logger.warning('KeyboardInterrupted')

        logger.info("WEBSERVER stopped.")

def respond(request):
    """
    Respond to [request]
    outputs:
        content: Content to respond
    """
    requestType = request.split('/')[0].strip()
    if requestType == 'GET':
        return do_GET(request)
    if requestType == 'POST':
        return do_POST(request)
    return ''


def serve_connection(connection, address, idx=None):
    """
    Method to serve [connection] of [idx] from [address].
    """
    try:
        # Fetch request
        request = connection.recv(1024).decode()
        logger.info(f'WEBSERVER-{idx} receive {request}')
        # Respond
        content = respond(request)
        if not isinstance(content, bytes):
            content = content.encode()
        length = len(content)
        logger.info(f'WEBSERVER-{idx} response {length} bits')
        connection.sendall(content)
        idx += 1
    except:
        logger.error(
            f'WEBSERVER runtime error. connection={connection}, client_address={address}.')
    finally:
        connection.close()

def mk_RESP(content_type, content):
    """
    Make regular response from default header and,
    [content_type] and [content].
    """

    def enc(src):
        # Encode src if it is not bytes
        if isinstance(src, bytes):
            return src
        else:
            return src.encode()

    content = enc(content)
    content_length = len(content)

    # Header
    response = ['HTTP/1.1 200 OK',
                'Accept-Ranges: bytes',
                'ETag: W/"269-1482321927478"',
                'Content-Language: zh-CN']
    # Allow origin access
    response.append('Access-Control-Allow-Origin: *')
    # Content-Type
    response.append(f'Content-Type: {content_type}; charset={charset}')
    # Content-Length
    response.append(f'Content-Length: {content_length} \n')
    # Content
    response.append(content)

    return b'\n'.join([enc(e) for e in response])


def do_POST(request):
    """
    Respond to [request] of GET
    outputs:
        Return response
    """
    content = request
    content_type = 'text/plain'
    return mk_RESP(content_type, content)


def do_GET(request):
    """
    Respond to [request] of GET
    outputs:
        Return response
    """

    request = urllib.parse.unquote(request)

    # Default content as raw request in plain text
    content = request
    content_type = 'text/plain'

    # Parse request
    path, query = parse(request, method='GET')

    # Buffer server working
    if path == '/[buffer]':
        # List file names in buffer server
        if query.get('method', '') == 'list':
            content = json.dumps(worker.buffer_list())
            content_type = 'application/json'
            return mk_RESP(content_type, content)

        # Get file in buffer server
        if all([query.get('method', '') == 'get',
                not query.get('name', '') == '']):
            bits = worker.buffer_get(query['name'])
            if not bits is None:
                content_type = 'application/pdf'
                return mk_RESP(content_type, bits)

    return mk_RESP(content_type, content)


def parse(request, method='GET'):
    """
    Parse request
    inputs:
        request: raw request
        method: 'GET' or 'POST'
    outputs:
        path: Path of request, a string.
        query: Queries of request, a dict.
    """
    # The format of text should be path?a=b&c=d
    text = request[len(method):].split('HTTP')[0].strip()

    # If not have query, return path and empty dict
    if not '?' in text:
        return text, dict()

    # Fetch [path]
    path, remains = text.split('?')

    # Fetch [query]
    query = dict()
    for q in remains.split('&'):
        # Ignore segment without '='
        if not '=' in q:
            continue
        # Add a query
        a, b = q.split('=', 1)
        query[a] = b

    # Return
    return path, query


if __name__ == '__main__':
    webserver = WEBSERVER()
    webserver.run()
