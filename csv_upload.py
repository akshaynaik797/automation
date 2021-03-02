import csv

import mysql.connector

from settings import conn_data

with mysql.connector.connect(**conn_data) as con, open('te.csv') as csv_file:
    cur = con.cursor()
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        q = "INSERT INTO `paths`(`insurer`,`process`,`field`,`is_input`,`path_type`,`path_value`,`api_field`,`default_value`,`step`,`seq`,`relation`,`flag`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cur.execute(q, tuple(row))
    con.commit()
