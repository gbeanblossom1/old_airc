from query.pysql import search


def query_database(sql_query):
    return search.search(sql_query)