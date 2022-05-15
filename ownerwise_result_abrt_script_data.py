#!/usr/bin/python3.8



# Code Contributed By Yashwant Kumar
# credit goes to Subhesh Sir


from cProfile import run
import psycopg2
from collections import defaultdict
import json
import cgi, cgitb
form = cgi.parse()

print("Content-type:text/html\n\r\n\r")

def getownerwiseresultabrt():
    f = False
    try:
        conn = psycopg2.connect(database="zarms50", user="postgres", password='newproject', host='127.0.0.1', port='5432')
        cursor=conn.cursor()
        
        try:
            runid = form['run_id'][0]
            
            
        except:
            print(f"<h1 style='color:red; text-align:center;'>You have not written any run id. Please enter a run id</h1>")
            exit(0)
        query = """select trl.runid,s.owner, s.scriptid, trl.script, trl.status, ceil(ceil(trl.end_time -trl.start_time)/60000) as "Time Taken (min)" from testrun_logs trl, scripts s where trl.runid in ("""+ str(runid) + """) and trl.status in('Aborted by user', 'Aborted due to timeout') and s.scriptid=trl.scriptid order by trl.runid, s.owner;"""
        
        cursor.execute(query)
        
        column = list(cursor.description)
        data = cursor.fetchall()
        
        if not data:
            print(f"<h1 style='color:red'>Enter valid RunId, Your run id is not valid --> {runid}</h1>")
            exit(0)
        results = []
        for row in data:
            row_dict = {}
            for i, col in enumerate(column):
                row_dict[col.name] = row[i]
            results.append(row_dict)
        all_ownerwise_result_data = results
        # print(all_ownerwise_result_data)



        f = True
    except:
        pass
    finally:
        conn.close()
    # <p style=\"float: right;\"><a href=\"http://zarms.corp.zscaler.com:82/cgi-bin/TestBedMonitor/ownerwise_result_abrt_script_data.pl?run_id=$runid\">Link</a></p>
    if f:
        print("""<html>
                <head>
                <style>
                table, td, th
                {
                font-family: \"Times New Roman\", Times, serif;
                }
                th
                {
                background-color:grey;
                color:white;
                align:center;
                }
                body {font-size:100%;}
                    </style>
                </head>""")
        print(f"""
                <body>
                <h1 align = \"center\">Ownerwise Aborted/Timedout scripts Data Summary</h1>
                <h3 align = \"center\" style=\"color:red\">Total Skipped Scripts: {len(all_ownerwise_result_data)} </h3>

                <br><br><table border = \"1\" cellspacing=\"1\" cellpadding=\"2\" align=\"left\">""")
        print("<tr style=\"background-color:#4169E1;color:white\"><td align=\"center\"><b>Run Id</b></td><td align=\"center\"><b>Owner</b></td><td align=\"center\"><b>Script</b></td><td align=\"center\"><b>Status</b></td><td align=\"center\"><b>Time Taken (min)</b></td></tr>\n")
        for each_script_data in all_ownerwise_result_data:
            print(f"""<tr><td><a href=\"https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={each_script_data['runid']}&tab=testrun\" target=_blank>{each_script_data['runid']}</a></td><td>{each_script_data['owner']}</td><td>"
            {each_script_data['script']}</td><td> {each_script_data['status']} </td><td align=\"center\"> <a href=\"https://zarms.corp.zscaler.com:8080/zarms50logs/test-runid{each_script_data['runid']}-{each_script_data['scriptid']}\" target=_blank> {each_script_data['Time Taken (min)']}</a></td></tr>\n""")
        print("</table></body></html>")
getownerwiseresultabrt()
