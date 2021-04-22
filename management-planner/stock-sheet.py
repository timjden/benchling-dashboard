import psycopg2
import pandas as pd
import os
from datetime import date

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
today = date.today()

def run_query(sql_file):
    query = open(sql_file).read()

    get_data = pd.read_sql_query(query, conn)
    df = pd.DataFrame(get_data)
    print(df)

df = run_query("get-stock-sheet.sql")
df.to_excel("Final Product Stock Sheet " + strftime("%Y-%m-%d"))

conn.close()