import psycopg2
import pandas as pd

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

def run_query(sql_file):
    query = open(sql_file).read()

    get_data = pd.read_sql_query(query, conn)
    df = pd.DataFrame(get_data)
    label = df.columns
    value = df.iloc[0,0]
    #print(label[0])
    #print(value)

    value_label = [str(value), str(label[0])]
    return value_label

html_template = open("critical-numbers-display.html").read()

left_value = run_query("avg-plant-biomass.sql")[0]
left_label = run_query("avg-plant-biomass.sql")[1]
middle_value = run_query("avg-protein-mass.sql")[0]
middle_label = run_query("avg-protein-mass.sql")[1]
right_value = run_query("avg-protein-yield.sql")[0]
right_label = run_query("avg-protein-yield.sql")[1]

display = html_template.format(Left = left_value, Middle = middle_value, Right = right_value)

print(display)

file = open("latest-critical-numbers.html", "w")
file.write(display)
file.close()

conn.close()