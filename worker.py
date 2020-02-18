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
    """

    def __init__(self, buffer_server=BUFFER_SERVER(), paper_server=None):
        self.buffer_server = buffer_server
        self.paper_server = paper_server
        logger.info('WORKER initialized.')

    def _get_server_(self, server):
        """
        Builtin method to get server by [server].
        outputs:
            server: buffer_server or paper_server,
                    None for invalid [server]
        """
        if server == 'buffer':
            return self.buffer_server
        if server == 'paper':
            return self.paper_server
        logger.error(f'WORKER receive illegal server name: {server}.')
        return None

    def list(self, server):
        """
        Return a list of names using [server]. None for fail.
        """
        server = self._get_server_(server)
        if server is None:
            return None
        return server.get_names()

    def start(self, server, name):
        """
        Start app for file by [name] of buffer or paper [server].
        inputs:
            server: 'buffer' or 'paper' means using buffer or paper server.
            name: File name to open.
        yields:
            Start app for file by name.
        outputs:
            Will return operation successful indicator.
            0 means success.
            1 means name not found error.
            2 means fail to start error.
            -1 means server name illegal error.
        """
        # Get server
        server = self._get_server_(server)
        if server is None:
            return -1
        # Find file
        series = server.get_by_name(name)
        if series is None:
            logger.error(f'WORKER failed on find {name}')
            return 1
        # Start app for file
        try:
            os.system(series['path'])
        except:
            logger.error(f'WORKER failed on start app for {name}')
            return 2
        logger.info(f'WORKER successly started {name}')
        return 0

    def get(self, server, name):
        """
        Get file by [name] of buffer or paper [server].
        inputs:
            server: 'buffer' or 'paper' means using buffer or paper server.
            name: File name to open.
        outputs:
            Will return file indicated by [server] and [name] in bits,
            will return None if failed.
        """
        # Get server
        server = self._get_server_(server)
        if server is None:
            return None
        # Find file
        series = server.get_by_name(name)
        if series is None:
            logger.error(f'WORKER failed on find {name}')
            return None
        # Open file
        with open(series['path'], 'rb') as fp:
            pdf_bits_list = fp.readlines()
        logger.info(f'WORKER successly opened {name}')
        return b''.join(pdf_bits_list)


if __name__ == '__main__':
    worker = WORKER()
    worker.start('buffer', '1-s2.0-S0028393217300593-main.pdf')
