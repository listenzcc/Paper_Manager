"""
Data worker.
Link http server and data servers (buffer and paper server).
"""


import os
from pprint import pprint
from local_profiles import logger
from server_buffer import BUFFER_SERVER
from server_papers import PAPERS_SERVER


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

    def __init__(self,
                 buffer_server=BUFFER_SERVER(),
                 papers_server=PAPERS_SERVER()):
        self.buffer_server = buffer_server
        self.papers_server = papers_server
        logger.info('WORKER initialized.')

    def buffer_list(self):
        """ Get a list of filenames in buffer_server """
        names = []
        try:
            names = self.buffer_server.get_names()
        except Exception as e:
            logger.error(f'WORKER buffer_list failed: {e}')
        finally:
            return names

    def buffer_get(self, name, method='open'):
        """
        Get file by [name] in buffer_server using [method='open' or 'start']
            method: 'open' means return bits stream
                    'start' means start the file using default app
        """
        try:
            assert(method in ['start', 'open'])
            # Find file
            series = self.buffer_server.get_by_name(name)
            # method == 'open'
            if method == 'open':
                with open(series['path'], 'rb') as fp:
                    pdf_bits_list = fp.readlines()
                logger.info(f'WORKER buffer_get opened {name}')
                return b''.join(pdf_bits_list)
            # method == 'start'
            if method == 'start':
                logger.info(f'WORKER buffer_get starts {name}')
                os.system(series['path'])
                return None
        except Exception as e:
            logger.error(f'WORKER buffer_get failed: {e}')
            return None

    def _title2fname_(self, title):
        """ Transform [title] to legal file name.
        All title user input will pass by this method. """
        return title.replace(':', '--') + '.pdf'

    def _fname2title_(self, fname):
        """ Transform file name [fname] to title """
        if fname.endswith('.pdf'):
            fname = fname[:-4]
        return fname.replace('--', ':')

    def _description2dict_(self, description):
        """ Transform [description] into dict.
        It is a finite state machine to walk throught description.
        outputs:
            A dict contains descriptions """
        # Init desDict as dict
        desDict = dict()

        # Split description
        des = [e.strip() for e in description.split('\n') if e.strip()]

        # Starts with 'Default' key with an empty list
        k = 'Default'
        desDict[k] = []
        for d in des:
            if all([d.startswith('['), d.endswith('].')]):
                # Meet a key, use it
                k = d[1:-2]
                # If the key not exists, create an empty list for it
                if k not in desDict:
                    desDict[k] = []
                continue
            # Append words into key [k]
            desDict[k].append(d)

        # Convert list into string
        for k in desDict:
            desDict[k] = '\n'.join(desDict[k])

        # Drop 'Default' entry if it is empty
        if desDict['Default'] == '':
            desDict.pop('Default')

        return desDict

    def buffer_commit(self, name, content):
        """ Handle new commit based on [name] and [content]. 
        Return 0 if success,
        return others if failed. """
        # Parse [content]
        try:
            new_content = dict(
                date=float(content['date']),  # Commit date
                title=content['title'],  # Title of the paper
                fname=self._title2fname_(content['title']),  # # Legal file name of the paper
                keywords=[e.strip() for e in content['keywords'].split(',')
                          if e.strip()],  # Keywords of the paper, list
                description=self._description2dict_(content['description']))  # Description of the paper, dict
            logger.info(f'WORKER buffer_commit parsed content')
        except Exception as e:
            logger.error(f'WORKER buffer_commit failed on parsing content: {content}, error: {e}')
            return 1

        # Get pdfbits
        pdfbits = self.buffer_get(name)
        if pdfbits is None:
            logger.error(f'WORKER buffer_commit failed on getting pdf file {name}')
            return 1

        try:
            # Commit to papers_server
            self.papers_server.new_commit(new_content, pdfbits)
            # Ignore new name in buffer_server
            self.buffer_server.new_ignore(name)
            logger.info(f'WORKER buffer_commit committed {new_content}.')
            return 0
        except Exception as e:
            logger.error(f'Worker buffer_commit failed on committing content: {new_content}, error: {e}')
            return 1


if __name__ == '__main__':
    worker = WORKER()
    worker.buffer_get(name='1-s2.0-S0028393217300593-main.pdf', method='start')
