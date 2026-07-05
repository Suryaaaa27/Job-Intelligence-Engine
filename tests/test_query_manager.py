from search.query_manager import QueryManager

qm = QueryManager()

print(qm.get_all_roles())

print()

print(qm.get_queries("AIML Engineer"))