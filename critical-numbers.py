import psycopg2
import pandas as pd

#Database info and credentials
DB_NAME = 'warehouse'
DB_HOST = 'postgres-warehouse.cbp.benchling.com'
DB_USER = input("Input Username:")
DB_PASS = input("Input Password:")

#Database connection
while True:
    try:
        print("Connecting to DB...")
        conn = psycopg2.connect(dbname = DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        print("Success!")
        break
    except:
        print("Error, retrying...")

def run_query(sql_file):
    query = open(sql_file).read()

    get_data = pd.read_sql_query(query, conn)
    df = pd.DataFrame(get_data)
    label = df.columns
    value = df.iloc[0,0]
    print(label[0])
    print(value)
    return str(value) + "<br>" + str(label[0])

html_template = open("critical-numbers-display.html").read()

left = run_query("avg-plant-biomass.sql")
middle = run_query("avg-protein-mass.sql")
right = run_query("avg-protein-yield.sql")

display = html_template.format(Left = left, Middle = middle, Right = right)

print(display)

file = open("latest-critical-numbers.html", "w")
file.write(display)
file.close()

conn.close()