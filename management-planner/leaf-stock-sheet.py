import psycopg2
import pandas as pd
import os
from datetime import datetime
import openpyxl

#Database info and credentials
DB_NAME = 'warehouse'
DB_HOST = 'postgres-warehouse.cbp.benchling.com'
DB_USER = 'u$timdennis_au' #input("Input Username:")
DB_PASS = '8J4PKYTyAmNMIoLR' #input("Input Password:")

#Database connection
while True:
    try:
        print("Connecting to DB...")
        conn = psycopg2.connect(dbname = DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        print("Success!")
        break
    except:
        print("Error, retrying...")

#Change out of the parent directory into the management-planner subfolder
os.chdir("C:/Users/timjd/OneDrive/Documents/GitHub/github-upload/management-planner")

#Get date
today = datetime.today()

def run_query(sql_file):
    query = open(sql_file).read()

    get_data = pd.read_sql_query(query, conn)
    df = pd.DataFrame(get_data)
    return(df)

df = run_query("get-leaf-stocks.sql")
print(df)

#SHAMELESSLY SMOOSHED TOGETHER FROM STACK OVERFLOW
filename = "C:/Users/timjd/OneDrive - Cape Biologix Technologies (Pty) Ltd/1. Stock/Live Frozen Leaf Stock " + str(today.strftime("%Y-%b")) + ".xlsx"
sheetname = str(today.strftime("%Y-%m-%d %H_%M%p"))
with pd.ExcelWriter(filename) as writer:
    if not df.index.name:
        df.index.name = 'Index'
    df.to_excel(writer, sheet_name=sheetname, index=False)
    worksheet = writer.sheets[sheetname]
    worksheet.set_column('A:A', 11, None)
    worksheet.set_column('B:B', 7, None)

wb = openpyxl.load_workbook(filename = filename)
tab = openpyxl.worksheet.table.Table(displayName="df", ref=f'A1:{chr(len(df.columns)+64)}{len(df)+1}')
wb[sheetname].add_table(tab)
wb.save(filename)

conn.close()