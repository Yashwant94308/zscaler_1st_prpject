#!/usr/bin/python3.8



# Code Contributed By Yashwant Kumar
# credit goes to Subhesh Sir

from cProfile import run
from json.tool import main
from threading import main_thread
from unittest import result
import psycopg2
from collections import defaultdict
import json
import cgi, cgitb
form = cgi.parse()

print("Content-type:text/html\n\r\n\r")
try:
    runids = form['run_ids'][0]
    runid = runids.split(',')
            
            
except:
    print(f"<h1 style='color:red; text-align:center;'>You have not written any run id. Please enter a run id</h1>")
    exit(0)


results = defaultdict(list)
def getskippedData(runid):
    
    
    try:
        conn = psycopg2.connect(database="zarms50", user="postgres", password='newproject', host='127.0.0.1', port='5432')
        cursor=conn.cursor()
        
        
        
        
        query = f"select s.subpkgname,concat('https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}','&tab=testrun') as log,trl.script,scrt.owner, CASE WHEN stdoutfile not like '%test-runid%' THEN 'Not Available' ELSE concat('https://zarms.corp.zscaler.com:8080/',stdoutfile) END as stdoutfile, CASE WHEN csvfile not like '%csv%' THEN 'Not Available' ELSE concat('https://zarms.corp.zscaler.com:8080/',csvfile) END as csvfile,status from testrun_logs trl,subpackages s, scripts scrt where runid={runid} and trl.scriptid not in (select distinct scriptid from testrun_results tr where runid={runid} and tr.rerun_attempt=trl.rerun_attempt) and s.subpkgid=trl.subpkgid and trl.scriptid=scrt.scriptid and trl.rerun_attempt in (select max(rerun_attempt) from testrun_logs where runid=trl.runid and scriptid=trl.scriptid);"
        cursor.execute(query)
        data = cursor.fetchall()
        
        
        column = list(cursor.description)
        cnt = 0
        for row in data:
            cnt += 1
            row_dict = {}
            for i, col in enumerate(column):
                row_dict[col.name] = row[i]
            results[row_dict['subpkgname']].append(row_dict)
        # print(results['SME Parallel Reg'][0]['owner'])
        
        
            

    except:
        pass
    finally:
        conn.close()
    
    return cnt

# print(runid)
num_records = 0
for r in runid:
    cnt  = getskippedData(r)
    num_records += cnt
all_ownerwise_result_data = results 

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
</head>
<body>""")
print(f"""<h1 align = \"center\">Subpackagewise Skipped Scripts Data Summary</h1>
<p style=\"float: right;\"><a href=\"http://localhost/skipped_scripts_data.py?run_ids={runids}\">Link</a></p>
<h3 align = \"center\" style=\"color:red\">Total Skipped Scripts: {num_records}</h3>

<br><br><table border = \"1\" cellspacing=\"1\" cellpadding=\"2\" align=\"left\">""")
print("<tr style=\"background-color:#4169E1;color:white\"><td align=\"center\"><b>Subpackage</b></td><td align=\"center\"><b>Owner</b></td><td align=\"center\"><b>Log</b></td><td align=\"center\"><b>Script</b></td><td align=\"center\"><b>Stdout File</b></td><td align=\"center\"><b>CSV File</b></td>")
print("</tr>\n")


if all_ownerwise_result_data:
    for each_subpkg_data in all_ownerwise_result_data.keys():
        # print(each_subpkg_data)
        print(f"<tr><td rowspan=\"{len(all_ownerwise_result_data[each_subpkg_data])}\">{each_subpkg_data}</td>")
        for each_script_data in all_ownerwise_result_data[each_subpkg_data]:
            print(f"<td>{each_script_data['owner']}</td>")
            print(f"<td><a href={each_script_data['log']} target=_blank> View</a></td>")
            print(f"<td>{each_script_data['script']}</td>")

            print(f"<td><a href={each_script_data['stdoutfile']} target=_blank> View</a></td>")
            print(f"<td><a href={each_script_data['csvfile']} target=_blank> View</a></td>")
            print("</tr>")

print("</table></body></html>")