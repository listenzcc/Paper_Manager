"""
Buffer server.
Manager of buffer folder
"""

import os
import time
import pandas as pd
from pdfrw import PdfReader
from local_profiles import profiles, logger


class BUFFER_SERVER():
    """
    Buffer server to manage buffer folder.
    variables:
        buffer_dir: Path of buffer folder.
        pdfs: A dataframe contains pdf file information in buffer folder.
    functions:
        update: Update pdfs from buffer folder.
        get_names: Get names from pdfs.
        get_by_name: Get series by name from pdfs.
    """

    def __init__(self):
        self.buffer_dir = profiles.buffer_dir
        self.ignores_path = os.path.join(self.buffer_dir, 'ignores.json')
        self.update()
        logger.info('BUFFER_SERVER started.')

    def read_ignores(self):
        """
        Read ignores for ignored by pdf file name.
        Try to read from self.ignores_path,
        create one if not exists.
        yield:
            self.ignores: DataFrame contains ignored file names.
        """
        if not os.path.exists(self.ignores_path):
            self.ignores = pd.DataFrame(columns=['name'])
        else:
            self.ignores = pd.read_json(self.ignores_path)

    def new_ignore(self, name):
        """
        Add new ignores by [name].
        Update this buffer.
        inputs:
            name: File name to be ignored.
        yield:
            Update self.ignores and write to disk.
        """
        if name not in self.ignores.name.values:
            self.ignores = self.ignores.append(
                {'name': name}, ignore_index=True)
            self.ignores.to_json(self.ignores_path)
        logger.info(f'Ignore name: {name}')
        self.update()

    def update(self):
        """
        Update pdfs from buffer folder.
        yield:
            self.pdfs
        """
        self.read_ignores()
        pdfs = pd.DataFrame()
        # Walk through folder
        # names = [n for n in os.listdir(self.buffer_dir)
        #          if all([n.endswith('.pdf'),
        #                  n not in self.ignores.name.values])]
        names = [n for n in os.listdir(self.buffer_dir)
                 if n.endswith('.pdf')]
        paths = [os.path.join(self.buffer_dir, n) for n in names]
        pdfs['name'] = names
        pdfs['path'] = paths
        # Parse informations
        for entry, method in [('atime', os.path.getatime),
                              ('ctime', os.path.getctime),
                              ('mtime', os.path.getmtime)]:
            pdfs[entry] = [time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(method(p)))
                           for p in paths]
        # Set index
        self.pdfs = pdfs.set_index('name', drop=True)
        # Done
        logger.info('Buffered file names updated.')

    def get_names(self):
        """Get Names from self.pdfs."""
        return self.pdfs.index.to_list()

    def get_by_name(self, name):
        """ Get paper and its path based on [name]
        output:
            bits: Bitstream of the pdf file
            fpath: Path to the pdf file """
        # Assert we have the paper
        assert(name in self.pdfs.index)
        # Get fpath
        fpath = self.pdfs['path'][name]
        info = PdfReader(fpath).Info
        # Get bits
        with open(fpath, 'rb') as f:
            bits_list = f.readlines()
        bits = b''.join(bits_list)
        logger.info(f'BUFFER_SERVER get_by_name success on {name}')
        return fpath, info, bits

if __name__ == '__main__':
    server = BUFFER_SERVER()
    print(server.pdfs)
