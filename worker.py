"""
Data worker.
Link http server and data servers (buffer and paper server).
"""


import os
from pprint import pprint
from local_profiles import profiles, logger
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
                 papers_server=PAPERS_SERVER(),
                 profiles=profiles):
        self.buffer_server = buffer_server
        self.papers_server = papers_server
        self.profiles = profiles
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
        # Profiles and basic check
        print('name: ', name)
        print('content: ', content)
        try:
            new_content = dict(
                date=float(content['date']),
                title=content['title'],
                fname=self._title2fname_(content['title']),
                keywords=[e.strip() for e in content['keywords'].split(',')
                          if e.strip()],
                description=self._description2dict_(content['description']))
            pass
        except:
            logger.error(f'Failed on parse {content}')
            return 1

        # Copy name into new_content['fname']
        try:
            with open(os.path.join(self.profiles.papers_dir, new_content['fname']), 'wb') as f:
                pdf = self.buffer_get(name)
                assert(pdf is not None)
                f.write(pdf)
        except:
            logger.error('Failed to copy file from {src} to {des}'.
                         format(src=name, des=new_content['fname']))
            return 1

        # Paper server issue
        # Commit to papers_server
        if not self.papers_server.new_commit(new_content) == 0:
            logger.error('Failed to commit {new_content} to paper_server')
            return 1

        # Buffer server issue
        # Ignore new name in buffer_server
        self.buffer_server.new_ignore(name)

        return 0

        # Check all required field exist
        if not all(['title' in content,
                    'keywords' in content,
                    'description' in content,
                    'date' in content]):
            logger.error(f'Failed on handle new commit {content}')
            return 1
        server = self.buffer_server
        server.new_ignore(name)
        logger.info(f'Commit success: name={name}, content={content}')
        return 0


if __name__ == '__main__':
    worker = WORKER()
    worker.buffer_get(name='1-s2.0-S0028393217300593-main.pdf', method='start')
