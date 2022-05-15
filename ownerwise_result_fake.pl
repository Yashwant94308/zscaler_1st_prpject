#!/usr/bin/perl

use Tie::IxHash;
use Data::Dumper;

use CGI qw(:standard);
use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
use CGI qw/Link/;

my $normal = "\e[0m";
my $green  = "\e[32m";
my $red    = "\e[1;31m";
my $blue   = "\e[1;34m";

=headmy $runid = param('run_id') || die "Please enter the run id" 34596 34575;
=cut
my $runid = 34596;
my %all_ownerwise_result_data;
tie %all_ownerwise_result_data, 'Tie::IxHash';
%all_ownerwise_result_data = %{ get_ownerwise_result_data() };

#print "all_ownerwise_result_data: " . Dumper( \%all_ownerwise_result_data );

sub get_ownerwise_result_data {
    require DBI;
    my $driver   = "Pg";
    my $database = "zarms50";
    my $dsn      = "dbi:$driver:database = $database;host = 127.0.0.1;port = 5432";
    my $userid   = "postgres";
    my $password = "newproject";
    my $dbh      = DBI->connect( $dsn, $userid, $password, { RaiseError => 1 } )
        or die $DBI::errstr;

=head
    my $stmt = qq(SELECT owner, 
       result, 
       type, 
       Count(*) 
FROM   (SELECT DISTINCT * 
        FROM   testrun_results tr, 
               scripts s 
        WHERE  tr.runid = $runid
               AND Lower(tr.testcase) NOT IN ( 
                   'startup', 'setup', 'postcondition', 
                   'precondition', 
                   'teardown' ) 
               AND tr.scriptid = s.scriptid) t 
GROUP  BY result, 
          type, 
          owner 
ORDER  BY owner; );
=cut

    my $stmt = qq(SELECT owner, 
       result, 
       type, 
       Count(*) 
FROM   (SELECT DISTINCT tr.*, s.*
        FROM   testrun_results tr, 
               testrun_logs tl, 
               scripts s 
        WHERE  tr.runid in ( $runid )
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
ORDER  BY owner;);

    my $results = $dbh->selectall_arrayref( $stmt, { Slice => {} } ) or die "Error: " . $dbh->errstr;
    

    my %final_result;
    tie %final_result, 'Tie::IxHash';

    foreach my $row ( @{$results} ) {
    	
        my $result = ( $row->{'result'} ? 'Pass' : 'Fail' );
        
        my $type = (
            $row->{'result'} ? ucfirst( $row->{'type'} )
            : ( ( ( !defined $row->{'type'} ) || ( $row->{'type'} !~ /^(config|setup|script|bug|skip)$/ ) ) ? "Unknown"
                : ucfirst( $row->{'type'} )
            )
        );
        $final_result{ $row->{'owner'} }->{$result}->{$type}
            = ( $final_result{ $row->{'owner'} }->{$result}->{$type} || 0 ) + ( $row->{'count'} || 0 );
        $final_result{ $row->{'owner'} }->{$result}->{'total'}
            = ( $final_result{ $row->{'owner'} }->{$result}->{'total'} || 0 ) + ( $row->{'count'} || 0 );
        $final_result{ $row->{'owner'} }->{'grand_total'}
            = ( $final_result{ $row->{'owner'} }->{'grand_total'} || 0 ) + ( $row->{'count'} || 0 );
    }

    $dbh->disconnect();

    #print "Final content is:: " . Dumper( \%final_result );

    return \%final_result;
    
}

print header, start_html("Producing results");

#my $outFile = "/home/zarms/tomcat8/webapps/zarms50logs/ownerwiseresult-$runid.html";

#open( OUTFILE, ">$outFile" );
#print OUTFILE "<html>
print "<html>
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
<p style=\"float: right;\"><a href=\"http://zarms.corp.zscaler.com:82/cgi-bin/TestBedMonitor/ownerwise_result.pl?run_id=$runid\">Link</a></p>
<br><br><table border = \"1\" cellspacing=\"1\" cellpadding=\"2\" align=\"left\">";

#print OUTFILE
print
    "<tr style=\"background-color:#4169E1;color:white;align:center\"><td style=\"padding-left: 50px;padding-right: 50px;\"><b>Owner</b></td><td style=\"padding-left: 30px;padding-right: 30px;\"><b>Total(Pass+Fail)</b></td><td style=\"padding-left: 30px;padding-right: 30px;\"><b>Pass</b></td><td style=\"padding-left: 30px;padding-right: 30px;\"><b>Fail</b></td><td style=\"padding-left: 30px;padding-right: 30px;\"><b>Config</b></td><td style=\"padding-left: 30px;padding-right: 30px;\"><b>Script</b></td><td style=\"padding-left: 30px;padding-right: 30px;\"><b>Bug</b></td><td style=\"padding-left: 30px;padding-right: 30px;\"><b>Setup</b></td><td style=\"padding-left: 30px;padding-right: 30px;\"><b>Skipped</b></td><td style=\"padding-left: 30px;padding-right: 30px;\"><b>Unknown</b></td></tr>\n";
my ($grand_total_cnt, $total_pass_cnt,  $total_fail_cnt, $total_config_cnt, $total_script_cnt,
    $total_bug_cnt,   $total_setup_cnt, $total_skip_cnt, $total_unknown_cnt
);
foreach my $owner ( keys %all_ownerwise_result_data ) {
    $grand_total_cnt   = ( $grand_total_cnt   || 0 ) + ( $all_ownerwise_result_data{$owner}->{'grand_total'}       || 0 );
    $total_pass_cnt    = ( $total_pass_cnt    || 0 ) + ( $all_ownerwise_result_data{$owner}->{'Pass'}->{''}        || 0 );
    $total_fail_cnt    = ( $total_fail_cnt    || 0 ) + ( $all_ownerwise_result_data{$owner}->{'Fail'}->{'total'}   || 0 );
    $total_config_cnt  = ( $total_config_cnt  || 0 ) + ( $all_ownerwise_result_data{$owner}->{'Fail'}->{'Config'}  || 0 );
    $total_script_cnt  = ( $total_script_cnt  || 0 ) + ( $all_ownerwise_result_data{$owner}->{'Fail'}->{'Script'}  || 0 );
    $total_bug_cnt     = ( $total_bug_cnt     || 0 ) + ( $all_ownerwise_result_data{$owner}->{'Fail'}->{'Bug'}     || 0 );
    $total_setup_cnt   = ( $total_setup_cnt   || 0 ) + ( $all_ownerwise_result_data{$owner}->{'Fail'}->{'Setup'}   || 0 );
    $total_skip_cnt    = ( $total_skip_cnt    || 0 ) + ( $all_ownerwise_result_data{$owner}->{'Fail'}->{'Skip'}    || 0 );
    $total_unknown_cnt = ( $total_unknown_cnt || 0 ) + ( $all_ownerwise_result_data{$owner}->{'Fail'}->{'Unknown'} || 0 );

    #print OUTFILE
    print "<tr><td>$owner</td><td align=\"center\">"
        . "<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search="
        . lc($owner)
        . " target=_blank>"
        . ( $all_ownerwise_result_data{$owner}->{'grand_total'} || 0 ) . "</a>"
        . "</td><td align=\"center\">"
        . "<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search=passed-"
        . lc($owner)
        . " target=_blank style=\"color:green\">"
        . ( $all_ownerwise_result_data{$owner}->{'Pass'}->{''} || 0 ) . " ("
        . sprintf(
        "%.2f",
        (     ( $all_ownerwise_result_data{$owner}->{'Pass'}->{''} || 0 )
            / ( $all_ownerwise_result_data{$owner}->{'grand_total'} || 0 )
                * 100
        )
        )
        . "%)" . "</a>"
        . "</td><td align=\"center\">";
        print "<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search=failed-"
        . lc($owner)
        . " target=_blank style=\"color:red\">"
        . ( $all_ownerwise_result_data{$owner}->{'Fail'}->{'total'} || 0 ) . " ("
        . sprintf(
        "%.2f",
        (     ( $all_ownerwise_result_data{$owner}->{'Fail'}->{'total'} || 0 )
            / ( $all_ownerwise_result_data{$owner}->{'grand_total'} || 0 )
                * 100
        )
        )
        . "%)" . "</a>" if ( $all_ownerwise_result_data{$owner}->{'Fail'}->{'total'} || 0 );
        print "</td><td align=\"center\">";
        print "<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search=config-"
        . lc($owner)
        . " target=_blank>"
        . $all_ownerwise_result_data{$owner}->{'Fail'}->{'Config'} . " ("
        . sprintf(
        "%.2f",
        (     ( $all_ownerwise_result_data{$owner}->{'Fail'}->{'Config'} || 0 )
            / ( $all_ownerwise_result_data{$owner}->{'grand_total'} || 0 )
                * 100
        )
        )
        . "%)" . "</a>" if ( $all_ownerwise_result_data{$owner}->{'Fail'}->{'Config'} || 0 );
        print "</td><td align=\"center\">";
        print "<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search=script-"
        . lc($owner)
        . " target=_blank>"
        . $all_ownerwise_result_data{$owner}->{'Fail'}->{'Script'} . " ("
        . sprintf(
        "%.2f",
        (     ( $all_ownerwise_result_data{$owner}->{'Fail'}->{'Script'} || 0 )
            / ( $all_ownerwise_result_data{$owner}->{'grand_total'} || 0 )
                * 100
        )
        )
        . "%)" . "</a>" if ( $all_ownerwise_result_data{$owner}->{'Fail'}->{'Script'} || 0 );
        print "</td><td align=\"center\">";
        print "<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search=bug-"
        . lc($owner)
        . " target=_blank>"
        . $all_ownerwise_result_data{$owner}{'Fail'}->{'Bug'} . " ("
        . sprintf(
        "%.2f",
        (     ( $all_ownerwise_result_data{$owner}->{'Fail'}->{'Bug'} || 0 )
            / ( $all_ownerwise_result_data{$owner}->{'grand_total'} || 0 )
                * 100
        )
        )
        . "%)" . "</a>" if ( $all_ownerwise_result_data{$owner}->{'Fail'}->{'Bug'} || 0 );
        print "</td><td align=\"center\">";
        print "<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search=setup-"
        . lc($owner)
        . " target=_blank>"
        . $all_ownerwise_result_data{$owner}->{'Fail'}->{'Setup'} . " ("
        . sprintf(
        "%.2f",
        (     ( $all_ownerwise_result_data{$owner}->{'Fail'}->{'Setup'} || 0 )
            / ( $all_ownerwise_result_data{$owner}->{'grand_total'} || 0 )
                * 100
        )
        )
        . "%)" . "</a>" if ( $all_ownerwise_result_data{$owner}->{'Fail'}->{'Setup'} || 0 );
        print "</td><td align=\"center\">";
        print "<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search=skipped-"
        . lc($owner)
        . " target=_blank>"
        . $all_ownerwise_result_data{$owner}->{'Fail'}->{'Skip'} . " ("
        . sprintf(
        "%.2f",
        (     ( $all_ownerwise_result_data{$owner}->{'Fail'}->{'Skip'} || 0 )
            / ( $all_ownerwise_result_data{$owner}->{'grand_total'} || 0 )
                * 100
        )
        )
        . "%)" . "</a>" if ( $all_ownerwise_result_data{$owner}->{'Fail'}->{'Skip'} || 0 );
        print "</td><td align=\"center\">";
        print "<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search=unknown-"
        . lc($owner)
        . " target=_blank>"
        . $all_ownerwise_result_data{$owner}->{'Fail'}->{'Unknown'} . " ("
        . sprintf(
        "%.2f",
        (     ( $all_ownerwise_result_data{$owner}->{'Fail'}->{'Unknown'} || 0 )
            / ( $all_ownerwise_result_data{$owner}->{'grand_total'} || 0 )
                * 100
        )
        )
        . "%)" . "</a>" if ( $all_ownerwise_result_data{$owner}->{'Fail'}->{'Unknown'} || 0 );
        print "</td></tr>\n";
}

#print OUTFILE
print
    "<tr><td><b>Total</b></td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun target=_blank>$grand_total_cnt</a></td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search=total-passed target=_blank style=\"color:green\">$total_pass_cnt (".sprintf("%.2f",($total_pass_cnt/$grand_total_cnt) *100) ."%)</a></td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search=fail target=_blank style=\"color:red\">$total_fail_cnt (".sprintf("%.2f",($total_fail_cnt/$grand_total_cnt) *100) ."%)</a></td><td align = \"center\">";
print "<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search=config target=_blank style=\"color:red\">$total_config_cnt (".sprintf("%.2f",($total_config_cnt/$grand_total_cnt) *100) ."%)</a>" if ($total_config_cnt);
print "</td><td align = \"center\">";
print "<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search=script target=_blank style=\"color:red\">$total_script_cnt (".sprintf("%.2f",($total_script_cnt/$grand_total_cnt) *100) ."%)</a>" if ($total_script_cnt);
print "</td><td align = \"center\">";
print "<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search=bug target=_blank style=\"color:red\">$total_bug_cnt (".sprintf("%.2f",($total_bug_cnt/$grand_total_cnt) *100) ."%)</a>" if ($total_bug_cnt);
print "</td><td align = \"center\">";
print "<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search=setup target=_blank style=\"color:red\">$total_setup_cnt (".sprintf("%.2f",($total_setup_cnt/$grand_total_cnt) *100) ."%)</a>" if ($total_setup_cnt);
print "</td><td align = \"center\">";
print "<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search=skip target=_blank style=\"color:red\">$total_skip_cnt (".sprintf("%.2f",($total_skip_cnt/$grand_total_cnt) *100) ."%)</a>" if ($total_skip_cnt);
print "</td><td align = \"center\">";
print "<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search=unknown target=_blank style=\"color:red\">$total_unknown_cnt (".sprintf("%.2f",($total_unknown_cnt/$grand_total_cnt) *100) ."%)</a>" if ($total_unknown_cnt);
print "</td></tr>";

=head
print
    "<tr><td colspan=\"2\"><b>%Total</b></td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search=total-passed target=_blank style=\"color:green\">"
    . sprintf( "%.2f", ( $total_pass_cnt / $grand_total_cnt ) * 100 )
    . "%</a></td><td align = \"center\">";
    print "<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search=fail target=_blank style=\"color:red\">"
    . sprintf( "%.2f", ( $total_fail_cnt / $grand_total_cnt ) * 100 )
    . "%</a>" if ($total_fail_cnt);
    print "</td><td align = \"center\">";
    print "<a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search=config target=_blank style=\"color:red\">"
    . sprintf( "%.2f", ( $total_config_cnt / $grand_total_cnt ) * 100 )
    . "%</a>" if ($total_config_cnt || 0);
    print "</td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search=script target=_blank style=\"color:red\">"
    . sprintf( "%.2f", ( $total_script_cnt / $grand_total_cnt ) * 100 )
    . "%</a></td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search=bug target=_blank style=\"color:red\">"
    . sprintf( "%.2f", ( $total_bug_cnt / $grand_total_cnt ) * 100 )
    . "%</a></td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search=setup target=_blank style=\"color:red\">"
    . sprintf( "%.2f", ( $total_setup_cnt / $grand_total_cnt ) * 100 )
    . "%</a></td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search=skip target=_blank style=\"color:red\">"
    . sprintf( "%.2f", ( $total_skip_cnt / $grand_total_cnt ) * 100 )
    . "%</a></td><td align = \"center\"><a href=https://zarms.corp.zscaler.com:8080/zarms-50/reporting.html?id=$runid&tab=testrun&search=unknown target=_blank style=\"color:red\">"
    . sprintf( "%.2f", ( $total_unknown_cnt / $grand_total_cnt ) * 100 )
    . "%</a></td></tr>";
=cut
#print OUTFILE
print "</table></body></html>";
print end_html;

#print "please open this link on your browser: $blue https://zarms.corp.zscaler.com:8080/zarms-50/zarms50logs/ownerwiseresult-$runid.html$normal\n";

