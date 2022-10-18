import psycopg2
import pandas as pd


def search(query):
    connection_string = "dbname=airc user=threatbeacon host=airc.cs.vt.edu password=7moP8s4IVoKyspSBGte4Tn8YZ7WjbzogPeJF9EP19UW8dYGxka"
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute(query)

    colnames = [desc[0] for desc in cursor.description]
    recList = [record for record in cursor]
    records = [dict(zip(colnames, r)) for r in recList]
    return records
