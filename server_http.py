"""
HTTP server.
"""


import json
import urllib.parse
from local_profiles import profiles, logger
from http.server import HTTPServer, BaseHTTPRequestHandler
from worker import WORKER

worker = WORKER()


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


class RequestHandler(BaseHTTPRequestHandler):
    def send_response_content(self, content_type, content, allow_origin_access=True):
        """
        Send response as [content_type] and [content].
        By default, we allow_origin_access.
        Example of Content-Type: text/html;charset:utf-8;
            text/html: HTML格式
            text/plain: 纯文本格式
            text/xml: XML格式
            image/gif: gif图片格式
            image/jpeg: jpg图片格式
            image/png: png图片格式
            application/xhtml+xml: XHTML格式
            application/xml: XML数据格式
            application/atom+xml: Atom XML聚合格式
            application/json: JSON数据格式
            application/pdf: pdf格式
            application/msword: Word文档格式
            application/octet-stream: 二进制流数据（如常见的文件下载）
            application/x-www-form-urlencoded: <form encType="">中默认的encType，form表单数据被编码为key/value格式发送到服务器（表单默认的提交数据的格式）
            multipart/form-data: 需要在表单中进行文件上传时，就需要使用该格式
        """
        # Response 200
        self.send_response(200)
        # Allow origin access
        if allow_origin_access:
            self.send_header('Access-Control-Allow-Origin', '*')
        # Send correct header
        self.send_header('Content-Type', '{}'.format(content_type))
        self.end_headers()
        # Send content
        self.wfile.write(content)

    def _parse_request_(self):
        """
        Builtin method to parse request from client browser.
        outputs:
            content_type: Content-Type of the response
            content: Content of the response in bits
        """
        charset = 'charset=utf-8'
        # Parse raw path
        request = urllib.parse.urlparse(urllib.parse.unquote(self.path))
        path = request.path
        logger.info(f'HTTP_SERVER receives {request}')
        # Response
        query = request.query
        # Require Buffer server
        if path == '/[buffer]':
            # Require to list file names
            if query == 'list':
                names = worker.list('buffer')
                if names is not None:
                    return f'application/json; {charset}', json.dumps(names).encode()
            # Require to pdf file as name
            if query.startswith('name='):
                name = query[len('name='):]
                bits = worker.get('buffer', name)
                if bits is not None:
                    return f'application/pdf; {charset}', bits
            # Commit new pdf file
            if query.startswith('commit&'):
                logger.info(f'Committing {query}')
                querys = query.split('&')
                name = querys[1][len('name='):]
                content = self.rfile.read(int(self.headers['content-length']))
                success = worker.commit('buffer', name, self.parse_content(content))
                if success == 0:
                    return f'text/plain; {charset}', b'Commit success.'
                else:
                    return f'text/plain; {charset}', b'Commit Fail. Check log for further information.'
        # It means a failure if reach here
        logger.error(f'Something went wrong: path={path}, query={query}')
        return f'text/plain; {charset}', b'Something wrong.'

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

    def parse_content(self, content):
        # Parse [content] from post request
        # content: content from post request
        content = urllib.parse.unquote(content.decode())
        datas = dict()
        for e in content.split('&'):
            if not '=' in e:
                continue
            a, b = e.split('=', 1)
            datas[a] = b
        logger.info(f'Parsed content: {datas}')
        return datas


if __name__ == '__main__':
    domain = 'localhost'
    port = 8619
    host = (domain, port)
    server = HTTP_SERVER(host, RequestHandler)
    server.start()