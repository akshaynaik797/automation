import mysql.connector
from settings import conn_data
with mysql.connector.connect(**conn_data) as con:
    cur = con.cursor()
    query = "SELECT * FROM paths where insurer = %s order by seq"
    cur.execute(query)