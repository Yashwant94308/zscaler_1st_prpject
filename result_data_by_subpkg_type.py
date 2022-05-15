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
def get_subpkg_type_wise_result_data():
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
        query = f"""SELECT runid,subpkgname,
        COALESCE(t.type, 'select') AS type,
        Count(*)  filter (WHERE t.result='f') AS "total_failed",
        Count(*)  as total_testcases
        FROM(SELECT DISTINCT trr.runid,
                        sp.subpkgname,
                        COALESCE(trr.type, 'select') AS type,
                        trr.scriptid,
                        trr.testcase,
                        trr.result
        FROM    testrun_results trr,
                scripts s,
                testrun_logs trl,
                subpackages sp
        WHERE   trr.runid IN ( {runid} )
                AND trl.runid = trr.runid
                AND Lower(trr.testcase) NOT IN (
                   'startup', 'setup', 'postcondition',
                   'precondition'
                   , 'teardown', 'initializedata', 'logout', 'logout_data' )
                AND trr.scriptid = s.scriptid
                AND trl.subpkgid = sp.subpkgid
                AND trr.rerun_attempt = trl.rerun_attempt
                AND trl.rerun_attempt IN (SELECT Max(rerun_attempt)
                                        FROM   testrun_logs
                                        WHERE  runid = trl.runid
                                        AND scriptid = s.scriptid
                                        AND subpkgid = sp.subpkgid)) t
                GROUP  BY t.runid,
                subpkgname,
                t.type
                ORDER  BY t.runid,
                subpkgname;"""
        cursor=conn.cursor()
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
        all_subpkg_result_data = rec_dd()
        for row in results:
            # print(row)
            all_subpkg_result_data[row['runid']][row['subpkgname']] [row['type']] = row



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
                <h1 align = \"center\">Subpkg-wise Result Data Summary</h1>""")
        print(f"""<p style=\"float: right;\"><a href=\"http://localhost/result_data_by_subpkg_type.py?run_id={runid}\">Link</a></p>
                <br><br><table border = \"1\" cellspacing=\"1\" cellpadding=\"2\" align=\"left\">""")
        print("<tr style=\"background-color:#4169E1;color:white;align:center\"><td><b>Run Id</b></td><td style=\"padding-left: 50px;padding-right: 50px;\"><b>Subpackage</b></td><td style=\"padding-left: 20px;padding-right: 20px;\"><b>#Testcases</b></td><td style=\"padding-left: 20px;padding-right: 20px;\"><b>#Failed</b></td><td style=\"padding-left: 30px;padding-right: 30px;\"><b>Config</b></td><td style=\"padding-left: 30px;padding-right: 30px;\"><b>Script</b></td><td style=\"padding-left: 30px;padding-right: 30px;\"><b>Bug</b></td><td style=\"padding-left: 30px;padding-right: 30px;\"><b>Setup</b></td><td style=\"padding-left: 30px;padding-right: 30px;\"><b>Skipped</b></td><td style=\"padding-left: 30px;padding-right: 30px;\"><b>Unknown</b></td></tr>\n")
        total_fail_cnt,  total_config_cnt, total_script_cnt, total_bug_cnt,  total_setup_cnt, total_skip_cnt, total_unknown_cnt, total_executed_count, total_failed_count = 0,0,0,0,0,0,0,0,0
        for each_run_id in all_subpkg_result_data.keys():
            print("<tr>")
            print(f"<td rowspan=\"{len(all_subpkg_result_data[each_run_id])}\">$each_run_id</td>")
            for subpkg in all_subpkg_result_data[each_run_id].keys():
                # print(type(all_subpkg_result_data[each_run_id][subpkg]['config']['total_failed'] )if all_subpkg_result_data[each_run_id][subpkg]['config']['total_failed'] else 0)
                a = (all_subpkg_result_data[each_run_id][subpkg]['config']['total_failed']  if all_subpkg_result_data[each_run_id][subpkg]['config']['total_failed'] else 0)
                
                total_config_cnt += a
                b = (all_subpkg_result_data[each_run_id][subpkg]['script']['total_failed']  if all_subpkg_result_data[each_run_id][subpkg]['script']['total_failed'] else 0)
                total_script_cnt += b
                c = (all_subpkg_result_data[each_run_id][subpkg]['bug']['total_failed']  if all_subpkg_result_data[each_run_id][subpkg]['bug']['total_failed'] else 0)
                total_bug_cnt += c
                d = (all_subpkg_result_data[each_run_id][subpkg]['setup']['total_failed']  if all_subpkg_result_data[each_run_id][subpkg]['setup']['total_failed'] else 0)
                total_setup_cnt += d
                e = (all_subpkg_result_data[each_run_id][subpkg]['skip']['total_failed']  if all_subpkg_result_data[each_run_id][subpkg]['skip']['total_failed'] else 0)
                total_skip_cnt += e

                f = (all_subpkg_result_data[each_run_id][subpkg]['select']['total_failed']  if all_subpkg_result_data[each_run_id][subpkg]['select']['total_failed'] else 0)
                total_unknown_cnt += f

                total_failed_testcases = a+b+c+d+e+f
                total_failed_count += total_failed_testcases
                

                total_testcases = (all_subpkg_result_data[each_run_id][subpkg]['config']['total_testcases'] if all_subpkg_result_data[each_run_id][subpkg]['config']['total_testcases'] else 0 ) + (all_subpkg_result_data[each_run_id][subpkg]['script']['total_testcases'] if all_subpkg_result_data[each_run_id][subpkg]['script']['total_testcases'] else 0 ) + (all_subpkg_result_data[each_run_id][subpkg]['bug']['total_testcases'] if all_subpkg_result_data[each_run_id][subpkg]['bug']['total_testcases'] else 0 ) + (all_subpkg_result_data[each_run_id][subpkg]['setup']['total_testcases'] if all_subpkg_result_data[each_run_id][subpkg]['setup']['total_testcases'] else 0 ) + (all_subpkg_result_data[each_run_id][subpkg]['skip']['total_testcases'] if all_subpkg_result_data[each_run_id][subpkg]['skip']['total_testcases'] else 0 ) + (all_subpkg_result_data[each_run_id][subpkg]['select']['total_testcases'] if all_subpkg_result_data[each_run_id][subpkg]['select']['total_testcases'] else 0 ) 
                total_executed_count += total_testcases

                print(f"""<td>{subpkg}</td><td align=\"center\">
	                    <a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={each_run_id}&tab=testrun target=_blank>{total_testcases}</a>
	                    </td><td align=\"center\">
                        <a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={each_run_id}&tab=testrun&search=fail target=_blank>{total_failed_testcases}</a>
                        </td><td align=\"center\">
	                    <a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={each_run_id}&tab=testrun&search=config target=_blank>{(all_subpkg_result_data[each_run_id][subpkg]['config']['total_failed'] if all_subpkg_result_data[each_run_id][subpkg]['config']['total_failed'] else 0)}</a>
	                    </td><td align=\"center\">
	                    <a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={each_run_id}&tab=testrun&search=script target=_blank>{b}</a>
	                    </td><td align=\"center\">
	                    <a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={each_run_id}&tab=testrun&search=bug target=_blank>{c}</a>
	                    </td><td align=\"center\">
	                    <a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={each_run_id}&tab=testrun&search=setup target=_blank>{d}</a>
                        </td><td align=\"center\">
                        <a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={each_run_id}&tab=testrun&search=skipped target=_blank>{e}</a>
	                    </td><td align=\"center\">
	                    <a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={each_run_id}&tab=testrun&search=unknown target=_blank>{f}</a>
	                    </td></tr>\n""")
        print(f"<tr><td colspan=\"2\" align=\"center\"><b>Total Count</b></td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun target=_blank>{total_executed_count}</a></td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=fail target=_blank style=\"color:red\">{total_failed_count}</a></td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=config target=_blank style=\"color:red\">{total_config_cnt}</a></td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=script target=_blank style=\"color:red\">{total_script_cnt}</a></td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=bug target=_blank style=\"color:red\">{total_bug_cnt}</a></td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=setup target=_blank style=\"color:red\">{total_setup_cnt}</a></td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=skip target=_blank style=\"color:red\">{total_skip_cnt}</a></td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=unknown target=_blank style=\"color:red\">{total_unknown_cnt}</a></td></tr>")
        print(f"<tr><td colspan=\"3\" align=\"center\"><b>Total %</b></td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=fail target=_blank style=\"color:red\">", end='')
        print("{0:.2f}".format(((total_failed_count/total_executed_count)*100)), end='')
        print(f"%</a></td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=config target=_blank style=\"color:red\">", end='')
        print("{0:.2f}".format(((total_config_cnt/total_executed_count)*100)), end='')
        print(f"%</a></td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=script target=_blank style=\"color:red\">", end='')
        print("{0:.2f}".format(((total_script_cnt/total_executed_count)*100)), end='')
        print(f"%</a></td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=bug target=_blank style=\"color:red\">", end='')
        print("{0:.2f}".format(((total_bug_cnt/total_executed_count)*100)), end='')
        print(f"%</a></td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=setup target=_blank style=\"color:red\">", end='')
        print("{0:.2f}".format(((total_setup_cnt/total_executed_count)*100)), end='')
        
        print(f"%</a></td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=skip target=_blank style=\"color:red\">", end='')
        
        print("{0:.2f}".format(((total_skip_cnt/total_executed_count)*100)), end='')
        print(f"%</a></td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id={runid}&tab=testrun&search=unknown target=_blank style=\"color:red\">", end='')
        print("{0:.2f}".format(((total_unknown_cnt/total_executed_count)*100)), end='')
        print("%</a></td></tr>")
        print("</table></body></html>")
    

    
get_subpkg_type_wise_result_data()