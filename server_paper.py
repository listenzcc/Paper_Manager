"""
Paper server.
Manager of organized papers
"""


import os
import time
import pandas as pd
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
        logger.info('PAPERS_SERVER started.')

    def read_keywords(self):
        """ Get keywords table. 
        Try to read from self.keywords_path,
        create one if not exist.
        yield:
            self.keywords: DataFrame contains Titles of keywords."""
        if not os.path.exists(self.keywords_path):
            self.keywords = pd.DataFrame()
        else:
            self.keywords = pd.read_json(self.keywords_path)

    def insert_keywords(self, keyword, title):
        """ Insert new [keyword] and [title] into [self.keywords] """
        if not title in self.keywords.index:
            self.keywords = self.keywords.append(pd.Series(name=title, dtype=int))
        if not keyword in self.keywords:
            self.keywords[keyword] = 0
        self.keywords[keyword].loc[title] = 1
        self.keywords[self.keywords.isnull()] = 0
        self.keywords = self.keywords.astype(int)

    def get_by_keyword(self, keyword):
        """ Get titles by [keyword],
        output:
            titles: A list of titles of [keyword] """
        
        # Return empty list if [keyword] not Found
        if not keyword in self.keywords:
            logger.warning(f'Keyword {keyword} not found.')
            return []

        # Get titles
        alltitles = self.keywords[keyword]
        return [e for e in alltitles[alltitles == 1].index]


if __name__ == '__main__':
    server = PAPERS_SERVER()
    server.read_keywords()
    server.insert_keywords('a', 'abc')
    server.insert_keywords('a', 'abb')
    server.insert_keywords('c', 'cbb')
    print(server.keywords)
    print(server.get_by_keyword('a'))