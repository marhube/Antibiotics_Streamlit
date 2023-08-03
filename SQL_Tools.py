print('Er inne i SQL_Tools.py')
#
import sys # For sys.exit()
import os
import re
import pandas as pd
import pyodbc
#
#********** Start importing auxiliary code
#********** End importing auxiliary code
def get_sql_filename(annual=False):
    if annual:
        pattern = r'.*.annual.*\.sql'
    else:
        pattern = r'.*monthly.*\.sql'
    #
    # Gjør nå både "pattern" og filnavn om til små bokstaver
    sql_filename = [filename for filename in os.listdir(".") 
                          if re.search(pattern, filename,re.IGNORECASE) is not None
                          ][0]
    return sql_filename
#
def get_sql_code(as_query=True,**kwargs):
    sql_filename = get_sql_filename(**kwargs)
    #
    sql_code = None
    # Get lines of code
    with open(sql_filename, 'r', encoding="latin-1") as sql_code:
        sql_code = sql_code.readlines()
    #
    if as_query:
        sql_code = " ".join(sql_code)        
    return sql_code

#
def generate_select(table_name):
    select_str = """SELECT *  """ + "FROM "  + table_name
    return select_str
#
def get_conn_str():
    # Velding Enkel hjelpefunksjon
   #conn_str = 'driver={SQL Server};server=sql-grossist;database=Grossist_DWH;trusted_connection=yes;'
    conn_str = 'Driver={SQL Server};' \
               'Server=sql-grossist;' \
               'Database=Grossist_DWH;' \
               'Trusted_Connection=yes;'
    
    
    return conn_str
#

def get_connection(conn_str=get_conn_str()):
    # Enkel hjelpefunksjon
    conn = pyodbc.connect(conn_str, autocommit=True)
    return conn
#
def get_table_from_db(sql_query= None,name_sql_table=None,conn_str=get_conn_str(),**kwargs):
    # Hjelpefunksjon for å hente tabell fra database
    if sql_query is None:
        sql_query = get_sql_code(**kwargs)
    #
    conn = get_connection(conn_str)
    crsr = conn.cursor()
    crsr.execute(sql_query)
    if name_sql_table is not None:
        sql_output_table = generate_select(name_sql_table)
        crsr.execute(sql_output_table)        
    #
    rows = crsr.fetchall()    
    columns = [column[0] for column in crsr.description]
    table_from_db = pd.DataFrame((tuple(row) for row in rows), columns=columns)
    crsr.close()
    return table_from_db
#





