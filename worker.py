"""
Data worker.
Link http server and data servers (buffer and paper server).
"""


import os
from local_profiles import profiles, logger
from server_buffer import BUFFER_SERVER


class WORKER():
    """
    Worker to operate servers of buffer and paper.
    variables:
        buffer_server: BUFFER_SERVER
        paper_server: [Not been implemented yet]
    methods:
        buffer_list(): Get a list of filenames in buffer_server
        buffer_get(name, method): Get file by [name] in buffer_server using [method='open' or 'start']
        buffer_commit(name, content): Commit file by [name] and [content] in buffer_server to paper_server
    """

    def __init__(self, buffer_server=BUFFER_SERVER(), paper_server=None):
        self.buffer_server = buffer_server
        self.paper_server = paper_server
        logger.info('WORKER initialized.')

    def buffer_list(self):
        """ Get a list of filenames in buffer_server """
        return self.buffer_server.get_names()

    def buffer_get(self, name, method='open'):
        """ Get file by [name] in buffer_server using [method='open' or 'start'] """
        # method = 'open' means return bits stream
        # method = 'start' means start the file using default app
        server = self.buffer_server
        # Find file
        series = server.get_by_name(name)
        if series is None:
            logger.error(f'WORKER failed on find {name}')
            return None
        # method == 'open'
        if method == 'open':
            with open(series['path'], 'rb') as fp:
                pdf_bits_list = fp.readlines()
            logger.info(f'WORKER successly opened {name}')
            return b''.join(pdf_bits_list)
        # method == 'start'
        if method == 'start':
            os.system(series['path'])
        logger.error(f'Invalid method {method}')
        return None

    def buffer_commit(self, name, content):
        """ Commit file by [name] and [content] in buffer_server to paper_server """
        server = self.buffer_server
        server.new_ignore(name)
        logger.info(f'Commit success: name={name}, content={content}')
        return 0

if __name__ == '__main__':
    worker = WORKER()
    worker.buffer_get(name='1-s2.0-S0028393217300593-main.pdf', method='start')
