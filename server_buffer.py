"""
Buffer server
"""

import os
import time
import pandas as pd
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
        self.pdfs = pd.DataFrame()
        self.update()
        logger.info('BUFFER_SERVER new instance initialized.')

    def update(self):
        """
        Update pdfs from buffer folder.
        yield:
            self.pdfs
        """
        pdfs = pd.DataFrame()
        # Walk through folder
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
        logger.info('BUFFER_SERVER updated.')

    def get_names(self):
        """Get Names from self.pdfs."""
        return self.pdfs.index.to_list()

    def get_by_name(self, name):
        """
        Get entry from self.pdfs by name.
        outputs:
            A series containing information of name,
            will return None if error occurred.
        """
        # Get series by name
        try:
            obj = self.pdfs.loc[name]
        except:
            logger.error(f'BUFFER_SERVER failed to get by name: {name}')
            return None
        # Return series
        if isinstance(obj, pd.Series):
            logger.info(f'BUFFER_SERVER successly get by name: {name}')
            return obj
        else:
            logger.error(f'BUFFER_SERVER failed to get by name: {name}')
            return None


if __name__ == '__main__':
    server = BUFFER_SERVER()
    print(server.pdfs)
