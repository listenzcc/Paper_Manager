"""
Data worker.
Link http server and data servers (buffer and paper server).
"""


import os
import json
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
            fpath, info, bits = self.buffer_server.get_by_name(name)
            if method == 'open':
                return bits
            if method == 'start':
                logger.info(f'WORKER buffer_get starts {name}')
                os.system(fpath)
                return None
        except Exception as e:
            logger.error(f'WORKER buffer_get failed: {e}')
            return None

    def buffer_parse(self, name):
        """ Parse file by [name] in buffer_server """
        try:
            fpath, info, bits = self.buffer_server.get_by_name(name)
            contents = dict(title='', doi='')
            if '/Title' in info:
                contents['title'] = info['/Title'][1:-1]
            if '/doi' in info:
                doi = info['/doi'][1:-1].split('/')[1]
                contents['doi'] = doi
            return contents
        except Exception as e:
            logger.error(f'WORKER buffer_parse failed: {e}')
            return None

    def papers_get_by_title(self, title, fields=['keywords', 'descriptions']):
        """
        Get paper and its contents by [title]. 
        outputs:
            A dict contains bits, keywords, descriptions in the format of json.
            None if failed.
        """
        try:
            paper_contents = self.papers_server.get_by_title(
                title, fields=fields)
            return paper_contents
        except AssertionError as e:
            logger.warning(
                f'WORKER papers_get_by_title cannot get not existing title: {title}.')
            return None
        except Exception as e:
            logger.error(f'WORKER papers_get_by_title failed: {e}')
            return None

    def papers_get_keywords(self):
        """ Get all the keywords from papers_server """
        try:
            keywords = self.papers_server.get_keywords()
            return [e for e in keywords]
        except Exception as e:
            logger.error(f'WORKER papers_get_keywords failed: {e}')
            return None

    def papers_get_descriptions(self):
        """ Get all the description names from papers_server """
        try:
            names = self.papers_server.get_descriptions()
            return [e for e in names]
        except Exception as e:
            logger.error(f'WORKER papers_get_descriptions failed: {e}')
            return None

    def _description2dict_(self, description):
        """ Transform [description] into dict.
        It is a finite state machine to walk throught description.
        outputs:
            A dict contains descriptions """
        # Init desDict as dict
        desDict = dict()

        # Split description
        des = [e.strip() for e in description.split('\n')]

        # Starts with 'Default' key with an empty list
        k = 'Default'
        desDict[k] = []
        for d in des:
            if d.startswith('##'):
                # Meet a key, use it
                k = d[2:].strip().title()
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
                timestamp=float(content['date']) / 1000,  # Commit timestamp
                title=content['title'],  # Title of the paper
                keywords=[e.strip().title()
                          for e in content['keywords'].split(',')
                          if e.strip()],  # Keywords of the paper, list
                descriptions=self._description2dict_(content['descriptions']))  # Descriptions of the paper, dict
            logger.info(f'WORKER buffer_commit parsed content')
        except Exception as e:
            logger.error(
                f'WORKER buffer_commit failed on parsing content: {content}, error: {e}')
            return 1

        # Get pdfbits
        pdfbits = self.buffer_get(name)
        if pdfbits is None:
            logger.error(
                f'WORKER buffer_commit failed on getting pdf file {name}')
            return 1

        try:
            # Commit to papers_server
            self.papers_server.new_commit(new_content, pdfbits)
            # Ignore new name in buffer_server
            self.buffer_server.new_ignore(name)
            logger.info(f'WORKER buffer_commit committed {new_content}.')
            return 0
        except Exception as e:
            logger.error(
                f'Worker buffer_commit failed on committing content: {new_content}, error: {e}')
            return 1

    def edit_currents(self, query):
        """ Handle edit_currents request. """
        tmpfname = 'tmp.md'
        with open(tmpfname, 'w') as f:
            f.writelines(['# {title}\n\n'.format(**query),
                          '## Keywords\n{keywords}\n\n'.format(**query),
                          '{descriptions}'.format(**query)])
        os.system(f'code.cmd -w -n {tmpfname}')
        keywords = 'keywords'
        descriptions = 'descriptions'
        with open(tmpfname, 'r') as f:
            lines = f.readlines()
        title = lines[0][1:].strip()
        keywords = lines[4].strip()
        descriptions = ''.join(lines[5:]).strip()
        return dict(title=title,
                    keywords=keywords,
                    descriptions=descriptions)


if __name__ == '__main__':
    worker = WORKER()
    worker.buffer_get(name='1-s2.0-S0028393217300593-main.pdf', method='start')
