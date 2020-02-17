"""
HTTP server.
"""


import urllib.parse
from local_profiles import profiles, logger
from http.server import HTTPServer, BaseHTTPRequestHandler
from server_buffer import BUFFER_SERVER

buffer_server = BUFFER_SERVER()

class HTTP_SERVER():
    def __init__(self, host, RequestHandler):
        self.server = HTTPServer(host, RequestHandler)
        logger.info('Starting server, listen at:{}:{}'.format(*host))
        logger.info('HTTP_SERVER initialized.')

    def start(self):
        try:
            logger.info('HTTP_SERVER starting.')
            self.server.serve_forever()
        except KeyboardInterrupt:
            logger.warning('Key interrupt.')
        finally:
            self.server.server_close()
            logger.info('HTTP_SERVER stopped.')


class RequestHandler(BaseHTTPRequestHandler):
    def send_response_content(self, content_type, content, allow_origin_access=True):
        # Response 200
        self.send_response(200)
        # Allow origin access
        if allow_origin_access:
            self.send_header('Access-Control-Allow-Origin', '*')
        # Send correct header
        '''
        Example:Content-Type:text/html;charset:utf-8;
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
        '''
        self.send_header('Content-Type', '{}'.format(content_type))
        self.end_headers()
        # Send content
        self.wfile.write(content)

    def do_GET(self):
        x = buffer_server.pdfs.to_json()
        self.send_response_content('application/json', x.encode('utf-8'))


if __name__ == '__main__':
    domain = 'localhost'
    port = 8619
    host = (domain, port)
    server = HTTP_SERVER(host, RequestHandler)
    server.start()