# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from searcher.lazyarray import LazyArray
import subprocess
import six


class SearchMedia(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        pass


class SearchMediaUseShell(SearchMedia):

    def __init__(self):
        pass

    @abstractmethod
    def get_command(self):
        pass

    @abstractmethod
    def read_output(self, output):
        pass


class SearchAgMedia(SearchMediaUseShell):

    command = 'ag'

    def get_command(self):
        return self.command

    def __init__(self):
        pass

    def read_output(self, output):
        res = []
        for line in output.split('\n'):
            if line.strip() != '':
                zline = line.split(':')
                filename = zline[0]
                position = zline[1]
                matched_str = ''.join(zline[2:]).strip()
                # res.append((line, filename, position, matched_str))
                res.append({
                    'filename': filename,
                    'position': position,
                    'matched_str': matched_str
                })
        return res

    def search(self, query):
        if query.strip() != '':
            output = subprocess.check_output(['ag', query])
            return self.read_output(output)
        else:
            return None


# ====================== #
# Searcher
# ====================== #


class Searcher(object):
    __metaclass__ = ABCMeta

    def __init__(self, **args):
        pass

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def search(self, query):
        pass

    invert_match = False
    lazy_searching = False

    def get_results(self, query):
        if self.lazy_searching:
            return LazyArray(())
        else:
            return [result for result in self.search(query)]

# ====================== #
# CachedSearcher
# ====================== #


class CachedSearcher(Searcher):

    def __init__(self, **args):
        self.results_cache = {}

    def get_collection_from_trie(self, query):
        pass

    def get_results(self, query):
        return Searcher.get_results(self, query)


class SearcherMulitQuery(CachedSearcher):

    def get_name(self):
        return 'SearcherMulitQuery'

    def __init__(self, split_str=" ", media=SearchAgMedia):
        self.media = media()
        CachedSearcher.__init__(self)
        self.split_str = split_str

    and_search = True  
    split_query = True
    case_insensitive = True

    dummy_res = [["", [(0, 0)]]]

    def search(self, query):
        collection = self.media.search(query)

        query_is_empty = query == ''

        if self.case_insensitive:
            query = query.lower()

        if self.split_query:
            queries = [self.transform_query(sub_query)
                       for sub_query in query.split(self.split_str)]
        else:
            queries = [self.transform_query(query)]

        if collection is None:
            collection = []

        for idx, col in enumerate(collection):
            if query_is_empty:
                res = self.dummy_res
            else:
                res = self.find_queries(queries, col['matched_str'])
            if res:
                yield col['matched_str'],\
                    res,\
                    idx,\
                    col['filename'],\
                    col['position']

    def find_queries(self, sub_queries, line):
        res = []

        and_search = self.and_search
        for subq in sub_queries:
            if subq:
                find_info = self.find_query(subq, line)
                if find_info:
                    res.append((subq, find_info))
                elif and_search:
                    return None
        return res

    def find_query(self, needle, haystack):
        # return [(pos1, pos1_len), (pos2, pos2_len), ...]
        #
        # where `pos1', `pos2', ... are begining positions of all occurence of needle in `haystack'
        # and `pos1_len', `pos2_len', ... are its length.
        stride = len(needle)
        start = 0
        res = []

        while True:
            found = haystack.find(needle, start)
            if found < 0:
                break
            res.append((found, stride))
            start = found + stride
        return res

    def transform_query(self, query):
        return query

if __name__ == '__main__':
    def test_searchAgMedia():
        SearchAgMedia().search('def')
    print test_searchAgMedia()
