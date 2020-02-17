"""
Buffer server
"""

import os
import pandas as pd
from local_profiles import profiles, logger


class BUFFER_SERVER():
    def __init__(self):
        self.pdfs = pd.DataFrame()
        self._update()
        logger.info('BUFFER_SERVER instance initialized.')

    def _update(self):
        names = [n for n in os.listdir(profiles.buffer_dir)
                 if n.endswith('.pdf')]
        self.pdfs['name'] = names
        self.pdfs['path'] = [os.path.join(profiles.buffer_dir, n)
                             for n in names]
        logger.info('BUFFER_SERVER updated.')
        return names


if __name__ == '__main__':
    server = BUFFER_SERVER()
    print(server.pdfs)
