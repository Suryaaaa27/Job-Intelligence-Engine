from search.query_manager import QueryManager


class SearchService:

    def __init__(self):

        self.query_manager = QueryManager()

    def get_queries(self, role):

        return self.query_manager.get_queries(role)