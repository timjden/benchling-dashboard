import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import base64

#Database info and credentials
DB_NAME = 'warehouse'
DB_HOST = 'postgres-warehouse.cbp.benchling.com'
DB_USER = 'u$timdennis_au'
DB_PASS = '8J4PKYTyAmNMIoLR'

#Database connection
while True:
    try:
        print("Connecting to DB...")
        conn = psycopg2.connect(dbname = DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        print("Success!")
        break
    except:
        print("Error, retrying...")

def get_dashboard ():
    #Get the date range for the data to be displayed (i.e. the current month)
    date = datetime.datetime.now()
    month = date.strftime("%m")
    year = date.strftime("%Y")
    nextMonth = int(date.strftime("%m")) + 1
    startRange = year + "-" + month + "-01"
    endRange = year + "-" + str(nextMonth) + "-01"

    #Temporary change in date - can be removed for live dashboard
    #startRange = '2021-03-01'
    #endRange = '2021-03-31'

    print(startRange)
    print(endRange)

    #List database queries 
    #Select protein batches and mg of protein

    #CONCAT(pb.file_registry_id$, '\n',
    query = """

    SELECT CONCAT(pb.file_registry_id$, ' ', pb.name) AS "ID", 

    (CASE 
        WHEN pb.name = 'S1-His' THEN COALESCE((qc.volume_ul/1000)*blitz_mgml, 0)
    ELSE COALESCE((qc.volume_ul/1000)*uv280_mgml, 0) 
    END) AS "Mass (mg)"
    FROM protein_batches pb
    LEFT JOIN quality_control qc
    ON pb.id = qc.protein_batch
    WHERE qc.date_time >= '""" + startRange + """' AND  qc.date_time <= '""" + endRange + """' AND pb.file_registry_id$ != 'PR-B114' AND pb.file_registry_id$ != 'PR-B116'
    AND (qc.quality_control_passfail != 'Fail' OR qc.quality_control_passfail IS NULL)
    ORDER BY pb.file_registry_id$

    """

    #Select date and number of plants infiltrated
    inflQuery = """

    SELECT infiltrated_on, SUM(COALESCE(plant_count, 0)::numeric)
    FROM infiltrations$raw
    WHERE (infiltrated_on >= '""" + startRange + """' AND infiltrated_on <= '""" + endRange + """')
    GROUP BY infiltrated_on
    ORDER BY infiltrated_on

    """

    #Select harvested leaf biomass per date
    harvestQuery = """

    SELECT l.protein_name as "Name", SUM(lb.weight_g) as "Kg"
    FROM container_content cc
    JOIN leaf_box lb ON lb.id = cc.container_id
    LEFT JOIN leaves l ON cc.entity_id = l.id
    LEFT JOIN location loc ON lb.location_id$ = loc.id
    WHERE lb.archived$ = 'false'
    GROUP BY l.protein_name

    """

    #Select plant weight prior to infiltration per infiltration date
    weightQuery = """
    SELECT pb.file_registry_id$, AVG(pm.avg_plant_weight_g)
    FROM infiltrations i
    LEFT JOIN plant_batches pb ON i.plant_lot = pb.id
    LEFT JOIN plant_measurements$raw pm ON pb.id = pm.plant_batch
    WHERE (i.infiltrated_on >= '""" + startRange + """' AND i.infiltrated_on <= '""" + endRange + """') AND pb.file_registry_id$ IS NOT NULL
    GROUP BY pb.file_registry_id$, i.infiltrated_on
    ORDER BY i.infiltrated_on
    """
    #Select yield per protein batch
    yieldQuery = """

    WITH total_vol as
    (SELECT h.file_registry_id$ as id,
            COUNT(h.file_registry_id$),
            SUM(c.homogenate_volume_l) as total_vol
    FROM clarificates c
    LEFT JOIN homogenates h ON h.id = c.homogenate
    GROUP BY h.file_registry_id$
    ORDER BY h.file_registry_id$)
    SELECT CONCAT(pb.file_registry_id$, ' ', pb.name) AS "ID",
       (CASE
            WHEN pb.name = 'S1-His' THEN ROUND((COALESCE((qc.volume_ul/1000)*blitz_mgml, 0)/ROUND(((c.homogenate_volume_l/total_vol.total_vol)*h.leaf_weight)::numeric, 2))::numeric, 2)
            ELSE ROUND((COALESCE((qc.volume_ul/1000)*uv280_mgml, 0)/ROUND(((c.homogenate_volume_l/total_vol.total_vol)*h.leaf_weight)::numeric, 2))::numeric, 2)
        END) AS yield_mgkg
    FROM protein_batches pb
    LEFT JOIN jsonb_array_elements_text(pb.clarificate_batch) AS cla_id ON TRUE
    LEFT JOIN clarificates c ON cla_id = c.id
    LEFT JOIN homogenates h ON c.homogenate = h.id
    LEFT JOIN total_vol ON h.file_registry_id$ = total_vol.id
    LEFT JOIN quality_control qc ON pb.id = qc.protein_batch
    WHERE qc.date_time >= '""" + startRange + """'
        AND qc.date_time <= '""" + endRange + """' AND pb.file_registry_id$ != 'PR-B114' AND pb.file_registry_id$ != 'PR-B116' AND (qc.quality_control_passfail != 'Fail' OR qc.quality_control_passfail IS NULL)
    ORDER BY pb.file_registry_id$

    """

    #Select total mg protein in inventory
    stockQuery = """

    SELECT pb.name as "Name", SUM(COALESCE((e.volume_si$*1000*cc.concentration_si*1000), (ft.volume_si$*1000*cc.concentration_si*1000))) as "Mass (mg)"
    FROM container_content cc
    LEFT JOIN eppendorf_tube e ON e.id = cc.container_id
    LEFT JOIN falcon_tube ft ON ft.id = cc.container_id
    LEFT JOIN protein_batches pb ON cc.entity_id = pb.id
    LEFT JOIN box b ON b.id = e.box_id$
    LEFT JOIN location l ON b.location_id = l.id OR ft.location_id$ = l.id
    WHERE (l.name = 'Antigen Stocks' OR l.name = 'Antibody Stocks') AND b.archived$ = 'false'
    GROUP BY "Name"
    ORDER BY "Name" DESC

    """

    def bar_plot (query, conn, ymin, ymax, xlabel, ylabel, xaxis_date): #the database query, the psycopg2 conn object, ymin value, ymax value, xlabel, ylabel, is the xaxis a date? (T/F)

        #Read SQL output to dataframe
        SQL_Query = pd.read_sql_query(query, conn)
        df = pd.DataFrame(SQL_Query)
        print(df)
        if df.empty:
            print("No new data this month, yet...")
            return
        #Define X and Y axes for barplot
        xaxis = df.iloc[:,0]
        yaxis = df.iloc[:,1]

        #Produce barplot
        plt.bar(xaxis, yaxis)
        plt.xlabel(xlabel, fontsize = 18)
        plt.ylabel(ylabel, fontsize = 18)
        plt.xticks(fontsize = 10, rotation = 90)
        plt.yticks(fontsize = 15)

        #Define axis limits
        if yaxis.empty:
            plt.ylim(ymin, ymax)
        elif max(yaxis) < ymax:
            plt.ylim(ymin, ymax)
            
        if xaxis_date:
            ticks = pd.date_range(start=startRange, end=endRange).strftime("%Y-%m-%d")
            plt.xticks(ticks, ticks, fontsize = 10, rotation=90)

        
    #Dashboard size
    plt.figure(figsize = (20, 10))
    rows = 2
    columns = 3

    #Subplot 1
    plt.subplot(rows,columns,4)
    bar_plot(query, conn, 0, 50, 'Protein Batch', 'Mass (mg)', False)

    #Subplot 2
    plt.subplot(rows,columns,2)
    bar_plot(inflQuery, conn, 0, 5000, 'Date', 'Plants Infiltrated', True)

    #Subplot 3
    plt.subplot(rows,columns,3)
    bar_plot(harvestQuery, conn, 0, 100, 'Protein Name', 'Frozen Leaf Mass (kg)', False)

    #Subplot 4
    plt.subplot(rows, columns, 1)
    bar_plot(weightQuery, conn, 0, 20, 'Plant Batch', 'Avg Plant Mass (g)', False)

    #Subplot 5
    plt.subplot(rows, columns, 5)
    bar_plot(yieldQuery, conn, 0, 50, 'Protein Batch', 'Yield (mg/kg)', False)

    #Subplot 6
    plt.subplot(rows, columns, 6)
    bar_plot(stockQuery, conn, 0, 500, 'Protein Name', 'Stock Level (mg)', False)

    plt.tight_layout()

    #Save dashboard as .svg
    plt.savefig('C:/Users/timjd/OneDrive - Cape Biologix Technologies (Pty) Ltd/Data Management Specialist/Benchling/Batch Reports/Automated Batch Reports/Python Script/Dashboards/images/' + date.strftime("%B-%Y") + '.svg')

    #Convert .svg to base64
    with open('C:/Users/timjd/OneDrive - Cape Biologix Technologies (Pty) Ltd/Data Management Specialist/Benchling/Batch Reports/Automated Batch Reports/Python Script/Dashboards/images/' + date.strftime("%B-%Y") + '.svg', "rb") as img_file:
        my_string = base64.b64encode(img_file.read())
    image = my_string.decode('utf-8')

    #Write HTML file
    html = """

    <html>
        <head>
        <style>

            * {
            margin: 0;
            padding: 0;
        }
        .imgbox {
            display: grid;
            height: 100%;
        }
        .center-fit {
            max-width: 100%;
            max-height: 100vh;
            margin: auto;
        }

        </style>
        <meta http-equiv="refresh" content="300">
        </head>
        <body>
        <div class = "imgbox">
            <img class = "center-fit" src='data:image/svg+xml;base64,""" + image + """'>
        </div>
        </body>
    <html>

    """

    #Save HTML file
    fileName = date.strftime("%B-%Y")+ "-Dashboard"
    with open("C:/Users/timjd/OneDrive - Cape Biologix Technologies (Pty) Ltd/BenchlingReports/Dashboards/" + fileName + ".html", "w") as file: #This is the file path to the Sharepoint folder (through OneDrive)
        file.write(html)

    print("Dashboard Created!")
#Run
get_dashboard()

'''
#Run again?
answer = input("Run again? (Y/N)")
while answer == 'Y':
    get_dashboard()
    answer = input("Run again? (Y/N)")
else:
    print("Goodbye")
'''

#Close connection
conn.close()