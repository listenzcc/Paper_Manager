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
        self.read_keywords()
        logger.info('PAPERS_SERVER started.')

    def read_keywords(self):
        """ Get keywords table. 
        Try to read keywords table from self.keywords_path.
        yield:
            self.keywords: DataFrame contains Titles of keywords,
            empty if file of keywords_path not exist."""
        if not os.path.exists(self.keywords_path):
            logger.warning(f'Keywords path does not exist.')
            self.keywords = pd.DataFrame()
        else:
            self.keywords = pd.read_json(self.keywords_path)

    def insert_keyword(self, keyword, title=None):
        """ Insert new [keyword] and [title] into [self.keywords],
        will only add keyword if [title] is None"""
        # If title not found, add new row
        if not title is None:
            if not title in self.keywords.index:
                self.keywords = self.keywords.append(
                    pd.Series(name=title, dtype=int))
        # If keyword not found, add new column
        if not keyword in self.keywords:
            self.keywords[keyword] = 0
        # Set keyword for title
        if not title is None:
            self.keywords[keyword].loc[title] = 1
        # Regulation
        self.keywords[self.keywords.isnull()] = 0
        self.keywords = self.keywords.astype(int)
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

    def new_commit(self, content):
        """ Handle new commit based on content. 
        Return 0 if success,
        return others if failed. """
        # Check all required field exist
        try:
            title = content['title']
            fname = content['fname']
            keywords = content['keywords']
            date = content['date']
            description = content['description']
        except:
            logger.error(f'Failed on handle new commit {content}')
            return 1

        # Check title exist
        if not os.path.exists(os.path.join(self.papers_dir, fname)):
            logger.error(f'{fname} not exists in {self.papers_dir}')
            return 1

        # Update keywords
        for kw in keywords:
            self.insert_keyword(kw, title)

        # Return 0 for success
        logger.info(f'PAPERS_SERVER received {title}')
        return 0


if __name__ == '__main__':
    server = PAPERS_SERVER()
    server.read_keywords()
    server.insert_keyword('a', 'abc')
    server.insert_keyword('b', 'abc')
    server.insert_keyword('a', 'abb')
    server.insert_keyword('c', 'cbb')
    server.insert_keyword('d')
    print(server.keywords)
    print(server.get_titles_by_keyword('a'))
    print(server.get_titles_by_keyword('d'))
    print(server.get_keywords_by_title('abc'))
