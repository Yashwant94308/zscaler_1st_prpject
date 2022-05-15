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


def getownerwiseresult():
    f = False
    try:
        conn = psycopg2.connect(database="zarms50", user="postgres", password='newproject', host='127.0.0.1', port='5432')
        cursor=conn.cursor()
        try:
            # runid = form['run_id'][0]
            runid = 34575
        except:
            print(f"<h1 style='color:red; text-align:center;'>You have not written any run id. Please enter a run id</h1>")
            exit(0)
        
        query = """SELECT owner, 
        result, 
        type, 
        Count(*) 
        FROM   (SELECT DISTINCT tr.*, s.*
                FROM   testrun_results tr, 
                    testrun_logs tl, 
                    scripts s 
                WHERE  tr.runid in ( """+str(runid)+""" )
                    AND Lower(tr.testcase) NOT IN ( 
                        'startup', 'setup', 'postcondition', 
                        'precondition', 
                        'teardown', 'initializedata', 'logout', 'logout_data' ) 
                    AND tr.scriptid = s.scriptid 
                    AND tr.runid in( tl.runid )
                    AND tr.rerun_attempt = tl.rerun_attempt 
                    AND tr.scriptid = tl.scriptid 
                    AND tl.rerun_attempt IN (SELECT Max(rerun_attempt) 
                                                FROM   testrun_logs 
                                                WHERE  runid in( tl.runid )
                                                    AND scriptid = tl.scriptid 
                                                    AND subpkgid = tl.subpkgid)) t 
        GROUP  BY result, 
                type, 
                owner 
        ORDER  BY owner;"""
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
        rec_dd = lambda: defaultdict(rec_dd)
        final_result = rec_dd()
        for row in results:
            if row['result']:
                result = 'Pass'
            else:
                result = 'Fail'
            if row['result']:
                if row['type']:
                    typed = row['type']
                else:
                    typed = ""
            elif row['result'] == False and row['type'] not in ('config','setup','script','bug','skip'):
                typed = 'Unknown'
            else:
                typed = row['type']
            if final_result[row['owner']][result][typed]:
                final_result[row['owner']][result][typed] = final_result[row['owner']][result][typed] + row['count'] if row['count'] else final_result[row['owner']][result][typed] + 0
            else:
                final_result[row['owner']][result][typed] = 0 + row['count'] if row['count'] else 0
            
            if final_result[row['owner']][result]['total']:
                final_result[row['owner']][result]['total'] = final_result[row['owner']][result]['total'] + row['count'] if row['count'] else final_result[row['owner']][result]['total'] + 0
            else:
                final_result[row['owner']][result]['total'] = 0 + row['count'] if row['count'] else 0
            
            if final_result[row['owner']]['grand_total']:
                final_result[row['owner']]['grand_total'] = final_result[row['owner']]['grand_total'] + row['count'] if row['count'] else final_result[row['owner']]['grand_total'] + 0
            else:
                final_result[row['owner']]['grand_total'] = 0 + row['count'] if row['count'] else 0
        # print(final_result)
        all_ownerwise_result_data = final_result
        f = True
    except:
        pass
    finally:
        conn.close()


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
        </head>
        <body>
        <h1 align = \"center\">Ownerwise Result Data Summary</h1>
        <br><br><table border = \"1\" cellspacing=\"1\" cellpadding=\"2\" align=\"left\">""")
        print("<tr style=\"background-color:#4169E1;color:white;align:center\"><td style=\"padding-left: 50px;padding-right: 50px;\"><b>Owner</b></td><td style=\"padding-left: 30px;padding-right: 30px;\"><b>Total(Pass+Fail)</b></td><td style=\"padding-left: 30px;padding-right: 30px;\"><b>Pass</b></td><td style=\"padding-left: 30px;padding-right: 30px;\"><b>Fail</b></td><td style=\"padding-left: 30px;padding-right: 30px;\"><b>Config</b></td><td style=\"padding-left: 30px;padding-right: 30px;\"><b>Script</b></td><td style=\"padding-left: 30px;padding-right: 30px;\"><b>Bug</b></td><td style=\"padding-left: 30px;padding-right: 30px;\"><b>Setup</b></td><td style=\"padding-left: 30px;padding-right: 30px;\"><b>Skipped</b></td><td style=\"padding-left: 30px;padding-right: 30px;\"><b>Unknown</b></td></tr>\n")

        grand_total_cnt, total_pass_cnt,  total_fail_cnt, total_config_cnt, total_script_cnt, total_bug_cnt, total_setup_cnt, total_skip_cnt, total_unknown_cnt=0,0,0,0,0,0,0,0,0

        for owner in all_ownerwise_result_data.keys():
            if all_ownerwise_result_data[owner]['grand_total']:
                grand_total_cnt += all_ownerwise_result_data[owner]['grand_total']
            if all_ownerwise_result_data[owner]['Pass']['']:
                total_pass_cnt += all_ownerwise_result_data[owner]['Pass']['']
            if all_ownerwise_result_data[owner]['Fail']['total']:
                total_fail_cnt += all_ownerwise_result_data[owner]['Fail']['total']
            if all_ownerwise_result_data[owner]['Fail']['config']:
                total_config_cnt += all_ownerwise_result_data[owner]['Fail']['config']
            if all_ownerwise_result_data[owner]['Fail']['script']:
                total_script_cnt += all_ownerwise_result_data[owner]['Fail']['script']
            if all_ownerwise_result_data[owner]['Fail']['bug']:
                total_bug_cnt += all_ownerwise_result_data[owner]['Fail']['bug']
            if all_ownerwise_result_data[owner]['Fail']['setup']:
                total_setup_cnt += all_ownerwise_result_data[owner]['Fail']['setup']
            if all_ownerwise_result_data[owner]['Fail']['skip']:
                total_skip_cnt += all_ownerwise_result_data[owner]['Fail']['skip']
            if all_ownerwise_result_data[owner]['Fail']['Unknown']:
                total_unknown_cnt += all_ownerwise_result_data[owner]['Fail']['Unknown']
            
            print(f"<tr><td>{owner}</td><td align=\"center\">")
            print(f"<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search={owner} target=_blank>{all_ownerwise_result_data[owner]['grand_total'] if all_ownerwise_result_data[owner]['grand_total'] else 0}</a>")
            print(f"</td><td align=\"center\">")
            print(f"<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=passed-{owner.lower()} target=_blank style=\"color:green\">{all_ownerwise_result_data[owner]['Pass'][''] if all_ownerwise_result_data[owner]['Pass'][''] else 0}", end="")
            print("({:.2f}%) </a>".format(round(((all_ownerwise_result_data[owner]["Pass"][""] if all_ownerwise_result_data[owner]["Pass"][""] else 0) / (all_ownerwise_result_data[owner]['grand_total'] if all_ownerwise_result_data[owner]['grand_total'] else 1) *100), 2)))
            print("</td><td align=\"center\">")
            
            
            tot = ((all_ownerwise_result_data[owner]["Fail"]["total"] if all_ownerwise_result_data[owner]["Fail"]["total"] else 0) / (all_ownerwise_result_data[owner]['grand_total'] if all_ownerwise_result_data[owner]['grand_total'] else 1) *100)
            if tot > 0:
                print(f"<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=failed-{owner.lower()} target=_blank style=\"color:red\">")
                print(f"{all_ownerwise_result_data[owner]['Fail']['total'] if all_ownerwise_result_data[owner]['Fail']['total'] else 0}")
                
                print("({:.2f}%) </a>".format(round(tot, 2)))
            print("</td><td align=\"center\">")


            tot = ((all_ownerwise_result_data[owner]["Fail"]["config"] if all_ownerwise_result_data[owner]["Fail"]["config"] else 0) / (all_ownerwise_result_data[owner]['grand_total'] if all_ownerwise_result_data[owner]['grand_total'] else 1) *100)
            if tot > 0:
                print(f"<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=config-{owner.lower()} target=_blank >")
                print(f"{all_ownerwise_result_data[owner]['Fail']['config'] if all_ownerwise_result_data[owner]['Fail']['config'] else 0}")

            
                print("({:.2f}%) </a>".format(round(tot, 2)))
            print("</td><td align=\"center\">")


            tot = ((all_ownerwise_result_data[owner]["Fail"]["script"] if all_ownerwise_result_data[owner]["Fail"]["script"] else 0) / (all_ownerwise_result_data[owner]['grand_total'] if all_ownerwise_result_data[owner]['grand_total'] else 1) *100)
            if tot > 0:
                print(f"<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=script-{owner.lower()} target=_blank >")
                print(f"{all_ownerwise_result_data[owner]['Fail']['script'] if all_ownerwise_result_data[owner]['Fail']['script'] else 0}")
                
                print("({:.2f}%) </a>".format(round(tot, 2)))
            print("</td><td align=\"center\">")

            tot = ((all_ownerwise_result_data[owner]["Fail"]["bug"] if all_ownerwise_result_data[owner]["Fail"]["bug"] else 0) / (all_ownerwise_result_data[owner]['grand_total'] if all_ownerwise_result_data[owner]['grand_total'] else 1) *100)
            if tot > 0:
                print(f"<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=bug-{owner.lower()} target=_blank >")
                print(f"{all_ownerwise_result_data[owner]['Fail']['bug'] if all_ownerwise_result_data[owner]['Fail']['bug'] else 0}")
                
                print("({:.2f}%) </a>".format(round(tot, 2)))
            print("</td><td align=\"center\">")

            tot = ((all_ownerwise_result_data[owner]["Fail"]["setup"] if all_ownerwise_result_data[owner]["Fail"]["setup"] else 0) / (all_ownerwise_result_data[owner]['grand_total'] if all_ownerwise_result_data[owner]['grand_total'] else 1) *100)
            if tot > 0:
                print(f"<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=setup-{owner.lower()} target=_blank >")
                print(f"{all_ownerwise_result_data[owner]['Fail']['setup'] if all_ownerwise_result_data[owner]['Fail']['setup'] else 0}")
                
                print("({:.2f}%) </a>".format(round(tot, 2)))
            print("</td><td align=\"center\">")

            tot = ((all_ownerwise_result_data[owner]["Fail"]["skip"] if all_ownerwise_result_data[owner]["Fail"]["skip"] else 0) / (all_ownerwise_result_data[owner]['grand_total'] if all_ownerwise_result_data[owner]['grand_total'] else 1) *100)
            if tot > 0:
                print(f"<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=skipped-{owner.lower()} target=_blank >")
                print(f"{all_ownerwise_result_data[owner]['Fail']['skip'] if all_ownerwise_result_data[owner]['Fail']['skip'] else 0}")
                
                print("({:.2f}%) </a>".format(round(tot, 2)))
            print("</td><td align=\"center\">")

            tot = ((all_ownerwise_result_data[owner]["Fail"]["Unknown"] if all_ownerwise_result_data[owner]["Fail"]["Unknown"] else 0) / (all_ownerwise_result_data[owner]['grand_total'] if all_ownerwise_result_data[owner]['grand_total'] else 1) *100)
            if tot > 0:
                print(f"<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=unknown-{owner.lower()} target=_blank >")
                print(f"{all_ownerwise_result_data[owner]['Fail']['Unknown'] if all_ownerwise_result_data[owner]['Fail']['Unknown'] else 0}")
                
                print("({:.2f}%) </a>".format(round(tot, 2)))
            print("</td></tr>\n")

        print(f"<tr><td><b>Total</b></td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun target=_blank>{grand_total_cnt}</a></td>")
        print(f"<td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=total-passed target=_blank style=\"color:green\">{total_pass_cnt}", end='')
        print("({:.2f}%)</a></td>".format(round(((total_pass_cnt/grand_total_cnt)*100), 2)))
        print(f"<td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=fail target=_blank style=\"color:red\">{total_fail_cnt} (", end='')
        print("({:.2f}%)</a></td><td align = \"center\"".format(round(((total_fail_cnt/grand_total_cnt)*100), 2)))
        if total_config_cnt > 0:
            print(f"<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=config target=_blank style=\"color:red\">{total_config_cnt} (", end='')
            print("{:.2f}%)</a>".format(round(((total_config_cnt/grand_total_cnt)*100), 2)))
        print("</td><td align = \"center\">")


        if total_script_cnt > 0:
            print(f"<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=script target=_blank style=\"color:red\">{total_script_cnt} (", end='')
            print("({:.2f}%)</a>".format(round(((total_script_cnt/grand_total_cnt)*100), 2)))
        print("</td><td align = \"center\">")

        if total_bug_cnt > 0:
            print(f"<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=bug target=_blank style=\"color:red\">{total_bug_cnt} (", end='')
            print("({:.2f}%)</a>".format(round(((total_bug_cnt/grand_total_cnt)*100), 2)))
        print("</td><td align = \"center\">")

        if total_setup_cnt > 0:
            print(f"<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=setup target=_blank style=\"color:red\">{total_setup_cnt} (", end='')
            print("({:.2f}%)</a>".format(round(((total_setup_cnt/grand_total_cnt)*100), 2)))
        print("</td><td align = \"center\">")

        if total_skip_cnt > 0:
            print(f"<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=skip target=_blank style=\"color:red\">{total_skip_cnt} (", end='')
            print("({:.2f}%)</a>".format(round(((total_skip_cnt/grand_total_cnt)*100), 2)))
        print("</td><td align = \"center\">")

        if total_unknown_cnt > 0:
            print(f"<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=unknown target=_blank style=\"color:red\">{total_unknown_cnt} (", end='')
            print("({:.2f}%)</a>".format(round(((total_unknown_cnt/grand_total_cnt)*100), 2)))
        print("</td></tr>")

        print("</table></body></html>")
        

    
    
getownerwiseresult()

    
    
    
    
    

