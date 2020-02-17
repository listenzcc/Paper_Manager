
"""
Profiles of the project.
"""

import os
import logging

SCHORLAR_DIR = os.path.join(os.environ.get('OneDrive'), 'Documents', 'schorlar')
PAPERS_DIR = os.path.join(SCHORLAR_DIR, 'papers')
BUFFER_DIR = os.path.join(SCHORLAR_DIR, 'buffer')
LOGGING_PATH = os.path.join('.', 'logging.log')


class PROFILES():
    def __init__(self):
        # Basic profiles
        self.papers_dir = PAPERS_DIR
        self.buffer_dir = BUFFER_DIR
        # Basic check
        self._check_dirs()
        logging.info('PROFILES instance initialized.')

    def _check_dirs(self):
        """
        Check dirs if they exist, make them if not.
        """
        for dir in [self.papers_dir,
                    self.buffer_dir]:
            if not os.path.exists(dir):
                message = f'Dir not exists: {dir}. Making it.'
                logging.warning(message)
                os.mkdir(dir)


class LOGGER():
    def __init__(self, level=logging.DEBUG):
        logging.basicConfig(filename=LOGGING_PATH,
                            level=level,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    def info(self, message):
        logging.info(message)
        print(f'[INFO]: {message}')
    
    def warning(self, message):
        logging.warning(message)
        print(f'[WARNING]: {message}')

    def error(self, message):
        logging.error(message)
        print(f'[!!!ERROR]: {message}')


logger = LOGGER()
profiles = PROFILES()
