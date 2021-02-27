import mysql.connector

from make_log import log_exceptions
from settings import conn_data

with mysql.connector.connect(**conn_data) as con, open('te.csv') as fp:
    cur = con.cursor()
    q = "select * FROM portals.paths where api_field like '%Last%'"
    cur.execute(q)
    result = cur.fetchall()
    for row in result:
        af = '0:' + row[6]
        q = "update paths set api_field = %s where insurer=%s and process=%s and field=%s"
        cur.execute(q, (af, row[0], row[1], row[2]))
    con.commit()