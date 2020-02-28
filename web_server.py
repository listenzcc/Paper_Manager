import socket
import urllib.parse
import sys
import json
import threading

from local_profiles import logger
from worker import WORKER


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
        while self.running:
            # Accept new connection
            connection, client_address = sock.accept()
            logger.info(
                f'WEBSERVER is connected {connection} from {client_address}.')
            # Start new thread to serve the connection
            t = threading.Thread(target=self.serve_connection, args=(
                connection, client_address, idx))
            t.start()
            # idx increase
            idx = (idx + 1) % 65536

        logger.info("WEBSERVER stopped.")

    def serve_connection(self, connection, address, idx=None):
        """
        Method to serve [connection] of [idx] from [address].
        """
        try:
            # Fetch request
            request = connection.recv(65536).decode()
            length = len(request)
            logger.info(f'WEBSERVER-{idx} receives {length} bits')
            # Respond
            content = self.respond(request)
            if not isinstance(content, bytes):
                content = content.encode()
            length = len(content)
            logger.info(f'WEBSERVER-{idx} responses {length} bits')
            connection.sendall(content)
            idx += 1
        except Exception as e:
            logger.error(
                f'WEBSERVER runtime error. connection={connection}, client_address={address}, error={e}')
        finally:
            connection.close()
            logger.info(f'WEBSERVER-{idx} connection closed')

    def respond(self, request):
        """
        Respond to [request]
        outputs:
            content: Content to respond
        """
        requestType = request.split('/')[0].strip()
        request = request.replace('+', ' ')
        request = urllib.parse.unquote(request)

        # Handle GET and POST request
        if requestType == 'GET':
            return do_GET(request)
        if requestType == 'POST':
            return do_POST(request)
        # Handle invalid request types
        return mk_RESP('text/plain',
                       f'Invalid request type [requestType]')


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
    Respond to [request] of POST
    outputs:
        Return response
    """
    # Default content
    content = request
    content_type = 'text/plain'

    # Parse request
    path, query = parse(request, method='POST')

    # Buffer server working
    if path == '/[buffer]':
        # Handle commit request
        if all([query.get('method', '') == 'commit',
                'name' in query]):
            if worker.buffer_commit(query['name'], query) == 0:
                content = 'Commit success.' + content
                return mk_RESP(content_type, content)

    # Parse request
    return mk_RESP(content_type, 'Something is wrong.\n' + content)


def do_GET(request):
    """
    Respond to [request] of GET
    outputs:
        Return response
    """
    # Default content as raw request in plain text
    content = request
    content_type = 'text/plain'

    # Parse request
    path, query = parse(request, method='GET')

    # Buffer server workload
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

        # Parse file in buffer server
        if all([query.get('method', '') == 'parse',
                not query.get('name', '') == '']):
            info = json.dumps(worker.buffer_parse(query['name']))
            if not info is None:
                content_type = 'application/pdf'
                return mk_RESP(content_type, info)

    # Papers server workload
    if path == '/[papers]':
        # Get all keywords
        if query.get('method', '') == 'keywords':
            keywords = worker.papers_server.get_keywords()
            content_type = 'application/json'
            content = json.dumps(keywords)
            return mk_RESP(content_type, content)

        # Get all description names
        if query.get('method', '') == 'descriptions':
            names = worker.papers_server.get_descriptions()
            content_type = 'application/json'
            content = json.dumps(names)
            return mk_RESP(content_type, content)

        # Get file by title
        if all([query.get('method', '') == 'get',
                not query.get('title', '') == '']):
            paper_content = worker.papers_get_by_title(query['title'])
            # If failed on getting by title,
            # make an empty paper_content,
            # if success, convert paper_contents values to json
            if paper_content is None:
                paper_content = dict(
                    keywords=json.dumps(dict()),
                    descriptions=json.dumps(dict()),
                )
                pass
            else:
                for k in ['keywords', 'descriptions']:
                    if k in paper_content:
                        paper_content[k] = paper_content[k].to_json()
            # Return contents
            content_type = 'application/json'
            content = json.dumps(paper_content)
            return mk_RESP(content_type, content)

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
    path, remains = text.split('?', 1)

    # Fetch [query]
    query = dict()
    for q in remains.split('&'):
        # Ignore segment without '='
        if not '=' in q:
            continue
        # Add a query
        a, b = q.split('=', 1)
        query[a] = b

    # Fetch contents if on 'POST'
    if method == 'POST':
        contents = request.split('\r\n')[-1]
        for q in contents.split('&kkk'):
            # Ignore segment without '='
            if not '=' in q:
                continue
            # Add a query
            a, b = q.split('=', 1)
            if a.startswith('kkk'):
                a = a[3:]
            query[a] = b

    # Return
    return path, query


if __name__ == '__main__':
    webserver = WEBSERVER()
    webserver.run()
