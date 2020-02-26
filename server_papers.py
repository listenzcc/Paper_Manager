"""
Paper server.
Manager of organized papers
"""


import os
import time
import pandas as pd
from pprint import pprint
from local_profiles import profiles, logger


class PAPERS_SERVER():
    """
    Paper server to manage organized papers.
    variables:
    functions:
    """

    def __init__(self):
        self.papers_dir = profiles.papers_dir
        self.keywords_path = os.path.join(self.papers_dir, 'keywords.json')
        self.descriptions_path = os.path.join(
            self.papers_dir, 'descriptions.xlsx')
        self.read_keywords()
        self.read_descriptions()
        logger.info('PAPERS_SERVER started.')

    def _title2fname_(self, title):
        """ Transform [title] to legal file name.
        All title user input will pass by this method. """
        fname = title.replace(':', '--').replace('?', '--q--')
        return f'{fname}.pdf'

    def _fname2title_(self, fname):
        """ Transform file name [fname] to title """
        if fname.endswith('.pdf'):
            fname = fname[:-4]
        return fname.replace('?', '--q--').replace('--', ':')

    def read_descriptions(self):
        """ Get descriptions table. 
        Try to read descriptions table from self.descriptions_path.
        yield:
            self.descriptions: DataFrame contains Titles and Descriptions,
            empty if file of descriptions_path not exist."""
        if not os.path.exists(self.descriptions_path):
            logger.warning(f'descriptions path does not exist.')
            self.descriptions = pd.DataFrame()
        else:
            self.descriptions = pd.read_excel(self.descriptions_path)
            self.descriptions = self.descriptions.set_index('Unnamed: 0', drop=True)

    def insert_description(self, desc, cont, title):
        """ Insert new [desc]: [cont] and [title] into [self.descriptions],
        inputs:
            desc: Name of description
            cont: Content of description
            title: Title of paper
        """
        for i in [desc, cont, title]:
            assert(isinstance(i, str))
        # If title not found, add new row
        if not title in self.descriptions.index:
            self.descriptions = self.descriptions.append(
                pd.Series(name=title))
        # If description not found, add new column
        if not desc in self.descriptions:
            dc = pd.DataFrame(columns=[desc])
            self.descriptions = pd.concat([self.descriptions, dc])
        # Set description for title
        self.descriptions[desc].loc[title] = cont
        # Save descriptions table
        self.descriptions.to_excel(self.descriptions_path)

    def read_keywords(self):
        """ Get keywords table. 
        Try to read keywords table from self.keywords_path.
        yield:
            self.keywords: DataFrame contains Titles and Keywords,
            empty if file of keywords_path not exist."""
        if not os.path.exists(self.keywords_path):
            logger.warning(f'Keywords path does not exist.')
            self.keywords = pd.DataFrame()
        else:
            self.keywords = pd.read_json(self.keywords_path)

    def insert_keyword(self, keyword, title, timestamp):
        """
        Add [timestamp] into [keyword] column and [title] row in [self.keywords].
        """
        for e in [keyword, title]:
            assert(isinstance(e, str))
        assert(isinstance(timestamp, float))
        # If title not found, add new row
        if not title in self.keywords.index:
            self.keywords = self.keywords.append(
                pd.Series(name=title, dtype=float))
        # If keyword not found, add new column
        if not keyword in self.keywords:
            kc = pd.DataFrame(columns=[keyword])
            self.keywords = pd.concat([self.keywords, kc])
        # Set keyword for title
        self.keywords[keyword].loc[title] = timestamp
        # Save keywords table
        self.keywords.to_json(open(self.keywords_path, 'w'))

    def get_titles_by_keyword(self, keyword):
        """ Get titles by [keyword],
        output:
            titles: A list of titles of [keyword] """
        # Return empty list if [keyword] not found
        if not keyword in self.keywords:
            logger.warning(f'Keyword {keyword} not found.')
            return []
        # Get titles
        alltitles = self.keywords[keyword]
        return [e for e in alltitles[alltitles == 1].index]

    def get_keywords_by_title(self, title):
        """ Get keywords by [title],
        outputs:
            titles: A list of keywords of [title] """
        # Return empty list if [title] not found
        if not title in self.keywords.index:
            logger.warning(f'Title {title} not found.')
            return []
        # Get keywords
        keywordsTrans = self.keywords.T
        allkeywords = keywordsTrans[title]
        return [e for e in allkeywords[allkeywords == 1].index]

    def new_commit(self, content, pdfbits):
        """
        Handle new commit based on [content] and [pdfbits].
        inputs:
            content: Contents of the paper.
            pdfbits: The pdf file in bits.
        """
        # Check all required field exist
        title = content['title']
        keywords = content['keywords']
        timestamp = content['timestamp']
        descriptions = content['descriptions']

        # Write pdf file to [fname]
        # Get legal file name
        fname = self._title2fname_(title)
        with open(os.path.join(self.papers_dir, fname), 'wb') as f:
            f.write(pdfbits)

        # Update keywords
        for kw in keywords:
            print(kw)
            self.insert_keyword(kw, title, timestamp)

        # Update descriptions
        for desc in descriptions:
            print(desc)
            self.insert_description(desc, descriptions[desc], title)

        # Done
        logger.info(f'PAPERS_SERVER received new commit of {title}')

    def get_keywords(self):
        """ Get all keywords.
        outputs:
            keywords: All keywords. """
        keywords = self.keywords.columns
        return [e for e in keywords]

    def get_descriptions(self):
        """ Get all description names.
        outputs:
            names: All descriptions names. """
        names = self.descriptions.columns
        return [e for e in names]

    def get_by_title(self, title, fields):
        """ Get paper and its content by [title] according to [fields].
        inputs:
            title: Title of the paper
            fields: Fields to be returned
        outputs:
            Outputs are according to [fields], may contains following fields
            fpath: Path to the pdf file
            bits: Bits stream of pdf file
            keywords: Keywords
            descriptions: Descriptions """
        contents = dict()

        # Get fname and fpath
        fname = self._title2fname_(title)
        fpath = os.path.join(self.papers_dir, fname)
        if 'fpath' in fields:
            contents['fpath'] = fpath

        # Assert descriptions, keywords and pdf file exists
        assert(title in self.descriptions.index)
        assert(title in self.keywords.index)
        assert(os.path.exists(fpath))

        # Get contents
        # Descriptions
        if 'descriptions' in fields:
            descriptions = self.descriptions.loc[title]
            contents['descriptions'] = descriptions[descriptions.notna()]
        # Keywords
        if 'keywords' in fields:
            keywords = self.keywords.loc[title]
            contents['keywords'] = keywords[keywords.notna()]
        # Get bits of pdf file
        if 'bits' in fields:
            with open(fpath, 'rb') as f:
                bits_list = f.readlines()
            contents['bits'] = b''.join(bits_list)

        logger.info(f'PAPERS_SERVER get_by_title success on {title}')
        return contents


if __name__ == '__main__':
    server = PAPERS_SERVER()
    pprint(server.keywords)
    pprint(server.descriptions)
