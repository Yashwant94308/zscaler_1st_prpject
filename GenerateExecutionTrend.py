#!/usr/bin/python3.8



# Code Contributed By Yashwant Kumar
# credit goes to Subhesh Sir

from cProfile import run
import psycopg2
from collections import defaultdict
import json
import re
import cgi, cgitb
form = cgi.parse()



print("Content-type:text/html\n\r\n\r")
print("<html><body>")


try:
    # runid = form['run_id'][0]
    selected_build = '6.1r'
    selected_subpackage = '239'
    selected_testbed_id = 'all'
    selected_timout_val = '1'

    

except:
    print(f"<h1 style='color:red; text-align:center;'>Some is Wrong</h1>")
    exit(0)

def get_trend_data():

    try:
        conn = psycopg2.connect(database="zarms50", user="postgres", password='newproject', host='127.0.0.1', port='5432')
        cursor=conn.cursor()
        
        q = f"select subpkgname from subpackages where subpkgid={selected_subpackage};"
        cursor.execute(q)
        data = cursor.fetchall()
        subpackage_name=data[0][0]

        testbed_clause = '' if selected_testbed_id == 'all' else f" AND array[tr.resourceid] && array[{selected_testbed_id}] "
        
        query = f"""SELECT           summary.buildid, 
                summary.runid, 
                summary.buildname, 
                s.owner, 
                summary.scriptid, 
                summary.script, 
                summary."execution_time (in mins)" 
                FROM             scripts s 
                RIGHT OUTER JOIN 
                                ( 
                                    SELECT           build_runid_summary.buildid, 
                                                   build_runid_summary.runid, 
                                                   build_runid_summary.buildname, 
                                                   trl1.scriptid, 
                                                   trl1.script, 
                                                   Floor(Ceil(trl1.end_time - trl1.start_time)/(60 *1000)) "execution_time (in mins)"
                                    FROM             testrun_logs trl1 
                                    RIGHT OUTER JOIN 
                                                   ( 
                                                            SELECT   Max(tr.runid) AS runid, 
                                                                     betc.buildid, 
                                                                     betc.buildname 
                                                            FROM     testrun tr, 
                                                                     testrun_logs trl, 
                                                                     ( 
                                                                              SELECT   rbm.runid,
                                                                                       rbm.buildid,
                                                                                       bi.buildname
                                                                              FROM     runid_buildid_map rbm,
                                                                                       buildinfo bi
                                                                              WHERE    bi.buildid=rbm.buildid
                                                                              AND      bi.buildname LIKE '%{selected_build}.%'
                                                                              ORDER BY bi.buildid DESC) betc
                                                            WHERE    tr.runid=betc.runid 
                                                            AND      trl.runid=tr.runid 
                                                            AND      array[ tasktype] && array['testrun']
                                                            AND      tr.status='Complete' 
                                                            AND      array[trl.subpkgid] && array[{selected_subpackage}]
                                                            {testbed_clause}
															and trl.rerun_attempt IN (SELECT Max(rerun_attempt) 
                                            FROM   testrun_logs 
                                            WHERE  runid = trl.runid 
                                                AND scriptid = trl.scriptid 
                                                AND subpkgid = trl.subpkgid)
                                                            GROUP BY betc.buildid, 
                                                                     betc.buildname 
                                                            ORDER BY betc.buildid DESC limit 5) build_runid_summary
                                    ON               trl1.runid=build_runid_summary.runid 
                                    AND              array[trl1.subpkgid] && array[{selected_subpackage}] 
								    and trl1.rerun_attempt IN (SELECT Max(rerun_attempt) 
                                            FROM   testrun_logs 
                                            WHERE  runid = trl1.runid 
                                            AND scriptid = trl1.scriptid 
                                            AND subpkgid = trl1.subpkgid)
                                    AND              floor(ceil(trl1.end_time - trl1.start_time)/(60 *1000)) >= {selected_timout_val}) summary
                                    ON               s.scriptid=summary.scriptid 
                                    ORDER BY         summary.buildid DESC;"""
        

        cursor.execute(query)
        column = list(cursor.description)
        data = cursor.fetchall()
        results = []
        for row in data:
            row_dict = {}
            for i, col in enumerate(column):
                row_dict[col.name] = row[i]
            results.append(row_dict)
        rec_dd = lambda: defaultdict(rec_dd)
        final_result = rec_dd()
        for row in results:
            buld = (row['buildid'] if row['buildid'] else '')
            script = (row['scriptid'] if row['scriptid'] else '')

            final_result[buld][script] = row
        return subpackage_name, final_result
        

        
    except:
        pass
    finally:
        conn.close()



subpackage_name, final_result = get_trend_data()



def generate_master_summary_table(subpackage_name, report_data):

    all_script_ids = {}
    all_unique_script_ids = []


    for build_id in sorted(report_data.keys()):
        for el in report_data[build_id].keys():
            if el != '':
                all_script_ids[el] = 1
        
    for k in all_script_ids.keys():
        all_unique_script_ids.append(k)
    html_content = f"<table border=1>\n"
    html_content += f"<tr style=\"font-weight:bold\" align=\"center\" bgcolor=#3385ff><td rowspan=\"2\" style=\"color: white;\">Module</td><td rowspan=\"2\" style=\"color: white;\">Owner</td><td rowspan=\"2\" style=\"color: white;\">Script</td><td colspan=\"5\" style=\"color: white;\">Latest Builds/Script Execution Time(in mins)/ Threshold Time: {selected_timout_val} mins</td></tr>\n"
    html_content += f"<tr style=\"font-weight:bold\" align=\"center\" bgcolor=#3385ff style=\"color: white;\">\n"
    
    s = set()
    
    for build_id in sorted(report_data.keys()):
        arr = list(report_data[build_id].keys())
        
        build_name = report_data[build_id][arr[0]]['buildname']
        build_name=build_name.lstrip('sc_')
        build_name=build_name.rstrip('.sh')
        print(build_name)
        
        html_content += f"<td style=\"color: white;\">{build_name}</td>\n"
    html_content += "</tr>\n"

    html_content += f"<tr><td rowspan=\"{len(all_unique_script_ids)}\">{subpackage_name}</td>\n"
    # print(all_unique_script_ids)
    temp_build_id = ''
    for each_script in all_unique_script_ids:
        for build_id in sorted(report_data.keys()):
            if report_data[build_id][each_script]:
                temp_build_id = build_id
                pass
        sc = report_data[temp_build_id][each_script]['script']
        script_name = ''
        arr = sc.split()
        for elem in arr:
            if re.search('^.*p[m|y]$', elem):
                script_name = elem
        html_content += f"<td>{report_data[temp_build_id][each_script]['owner']}</td><td>{script_name}</td>\n"

        for build_id in sorted(report_data.keys()):
            if report_data[build_id][each_script]:
                run_id = report_data[build_id][each_script]['runid']
            else:
                run_id = report_data[build_id]['']['runid']
                
            if not run_id:
                temparr = list(report_data[build_id].keys())
                
                run_id = report_data[build_id][temparr[0]]['runid']
            html_content += f"<td align=\"center\"><a href=\"https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={run_id}&tab=testrun\" target=_blank>\n"
            html_content += "<font color="
            if report_data[build_id][each_script]:
                if int(report_data[build_id][each_script]['execution_time (in mins)'] )<= 50:
                    color = 'Orange'
                else:
                    color = 'Red'
                minute = report_data[build_id][each_script]['execution_time (in mins)'] 
            else:
                minute = 'Ok'
                color = 'Green'
            html_content += f"{color}>{minute}</font></a></td>\n"
        html_content += "</tr><tr>\n"
    html_content += "</table></body></html>\n"
    return html_content



                

html_content = generate_master_summary_table(subpackage_name, final_result)
# print(html_content)


