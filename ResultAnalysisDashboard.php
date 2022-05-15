<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
.dropbtn {
  background-color: #82CAFF;
  color: white;
  padding: 5px;
  font-size: 15px;
  border: inline-block;
  cursor: pointer;
  border-radius: 4px;
  margin: 4px 2px;

}

.dropbtn:hover, .dropbtn:focus {
  background-color: #56A5EC;
}

#myInput {
  border-box: box-sizing;
  background-image: url('searchicon.png');
  background-position: 14px 12px;
  background-repeat: no-repeat;
  font-size: 16px;
  padding: 14px 20px 12px 45px;
  border: none;
  border-bottom: 1px solid #ddd;
}

#myInput:focus {outline: 3px solid #ddd;}

.dropdown a:hover {background-color: #ddd;}

.show {display: block;}

</style>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
</head>

<body>

 <p style="float: left;"><img src="images/zscaler-squarelogo.png" alt="Zscaler logo" width="120" height="100"></p>
<center>
 <p><h2>Result Analysis Dashboard</h2></p>
<div>
<input type="radio" name="radio_btn_class" id="get_result_data_summary_radio" value="get_ownerwise_data_chkbx" onchange="change_runid_test_property()" checked onclick="ShowHideDiv()"> Ownerwise Result Summary
<input type="radio" name="radio_btn_class" id="get_skipped_data_summary_radio" value="get_skipped_data_chkbx" onchange="change_runid_test_property()" onclick="ShowHideDiv()"> Skipped Scripts Summary
<input type="radio" name="radio_btn_class" id="get_abrt_script_summary_radio" value="get_Abrt_script_chkbx" onchange="change_runid_test_property()" onclick="ShowHideDiv()"> Aborted/Timedout Script Summary
<input type="radio" name="radio_btn_class" id="get_failure_analysis_summary_radio" value="get_failure_analysis_chkbx" onchange="change_runid_test_property()" onclick="ShowHideDiv()"> Failure Analysis Report
<input type="radio" name="radio_btn_class" id="get_failure_by_subpkg_type_radio" value="get_failure_analysis_by_subpkg_type_chkbx" onchange="change_runid_test_property()" onclick="ShowHideDiv()"> Subpkg-wise Failure Analysis Report
<input type="radio" name="radio_btn_class" id="get_alltestcase_time_by_subpkg_type_radio" value="get_alltestcase_time_by_subpkg_type_chkbx" onchange="change_runid_test_property()" onclick="ShowHideDiv()"> Subpkg-wise Total Testcase/Time Report
<input type="radio" name="radio_btn_class" id="get_time_taking_scripts_trend_radio" value="get_time_taking_scripts_trend_chkbx" onchange="change_runid_test_property()" onclick="ShowHideDiv()"> Time taking scripts trend Report<br>
</div>

<br>
<div class="holds-the-input-field" id="holds-the-input-field" style="align=center">
Run Id: <input type="text" id="runIdTxt" name="runIdTxt" maxlength="1000" size=8 width="10" value="<?php echo $_GET['run_ids']; ?>" onkeypress="return IsNumeric(event);">
</div>

<div class="holds-the-input-subpackage_drpdwn" id="holds-the-input-subpackage-drpdwn" style="align:center;display:none">

        <!--select name="owner"-->
<?php
include "config.php";

            $sql =<<<EOF
      select distinct p.pkgid,p.pkgname from packages p, subpackages sp, pkg_subpkg_map psm where p.isdeleted ='f' and p.pkgid=psm.pkgid and sp.subpkgid=psm.subpkgid and sp.custom='f' and sp.isdeleted='f' order by p.pkgname;
EOF;

   $ret = pg_query($con, $sql);
   
   if(!$ret) {
      echo pg_last_error($con);
      exit;
   }
   echo "Package: <select id=\"select_drpdwn_package\"><option value=\"none\">Select</option>";
   while($row = pg_fetch_row($ret)) {
           echo "<option value=$row[0]>$row[1]</option>";
   }
   echo "</select>";

   echo "&nbspSubpackage: <select id=\"select_drpdwn_subpackage\"><option value=\"none\">Select</option>";
   echo "</select>";

   pg_close($con);
?>
        Build support: <select id="select_drpdwn_build"><option value="none">Select</option><option value="5.6">5.6</option><option value="5.7r">5.7r</option><option value="5.7">5.7</option><option value="6.0">6.0</option><option value="5.5">5.5</option><option value="6.0r">6.0r</option><option value="6.1r">6.1r</option><option value="6.1">6.1</option></select>
        Testbed: <select id="select_drpdwn_testbed"><option value="all">All</option><option value="17">Aquila</option><option value="3">Golden Setup-2</option><option value="181">Consolidated-VQA</option><option value="186">Consolidatd-VQA- System</option><option value="14">Consolidated-3</option><option value="7">Consolidated-4</option><option value="41">ZSCM Setup - 5.7r</option><option value="170">ZSCM Setup - 6.0</option><option value="11">FCC_SMBA_Setup -1</option></select>
Threshold Timeout(mins): <input type="text" id="timeoutTxt" name="timeoutTxt" maxlength="1000" size=8 width="10" value=30 onkeypress="return IsNumeric(event);">

</div>

<button onclick="myFunction()" class="dropbtn" id="dropbtn">Submit</button>

</center>

<div class="holds-the-iframe" id="holds-the-iframe-id" style="align=center">
<iframe height="800px" width="100%" src="welcome_iframe_bes.html" id="demo" name="iframe_b" align="top"></iframe>
</div>

<script type="text/javascript">
//document.getElementById('runidTxt').onkeypress=

var input = document.getElementById("runIdTxt");
input.addEventListener("keyup", function(event) {
  if (event.keyCode === 13) {
   event.preventDefault();
   document.getElementById("dropbtn").click();
  }
});

function ShowHideDiv() {
        var chkYes = document.getElementById("get_result_data_summary_radio").checked || document.getElementById("get_abrt_script_summary_radio").checked || document.getElementById("get_failure_analysis_summary_radio").checked || document.getElementById("get_failure_by_subpkg_type_radio").checked || document.getElementById("get_alltestcase_time_by_subpkg_type_radio").checked || document.getElementById("get_skipped_data_summary_radio").checked;
        var input_field_div = document.getElementById("holds-the-input-field");
        var input_drpdwn_field_div = document.getElementById("holds-the-input-subpackage-drpdwn");

        input_field_div.style.display = chkYes ? "block" : "none";
        input_drpdwn_field_div.style.display = chkYes ? "none" : "block";

}

function IsNumeric (e) {
    var keyCode = e.which ? e.which : e.keyCode
    if(keyCode==13){
        //document.getElementById('runidShowbtn').click();
        return true;
    } else {
        var specialKeys = new Array();
        specialKeys.push(8); //Backspace
	specialKeys.push(44); //Backspace
        var ret = ((keyCode >= 48 && keyCode <= 57) || specialKeys.indexOf(keyCode) != -1);
        return ret;
    }
}

function change_runid_test_property() {
var get_result_data_summary_radio_selected = document.getElementById('get_result_data_summary_radio').checked;
var subpkg_wise_radio_selected = document.getElementById('get_failure_by_subpkg_type_radio').checked;
var abrt_script_summary_radio_selected = document.getElementById('get_abrt_script_summary_radio').checked;
var get_failure_analysis_summary_radio_selected = document.getElementById('get_failure_analysis_summary_radio').checked;
var get_alltestcase_time_by_subpkg_type_radio_selected = document.getElementById('get_alltestcase_time_by_subpkg_type_radio').checked;
var get_skipped_data_summary_radio_selected = document.getElementById('get_skipped_data_summary_radio').checked;

if (get_result_data_summary_radio_selected == true || subpkg_wise_radio_selected == true || abrt_script_summary_radio_selected == true || get_failure_analysis_summary_radio_selected == true || get_alltestcase_time_by_subpkg_type_radio_selected == true || get_skipped_data_summary_radio_selected == true) {
    document.getElementById('runIdTxt').size="8";
    document.getElementById('runIdTxt').maxLength="1000";
     //document.getElementById('runIdTxt').value="";
} else {
    document.getElementById('runIdTxt').size="8";
    document.getElementById('runIdTxt').maxLength="8";
    if (document.getElementById('runIdTxt').value.length > 8) {
	document.getElementById('runIdTxt').value="";
    }
}
}
/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function myFunction() {
  var run_id = document.getElementById('runIdTxt').value;
  var selected_subpkg = document.getElementById('select_drpdwn_subpackage').value;
  var selected_build =  document.getElementById('select_drpdwn_build').value;
  var selected_testbed_id =  document.getElementById('select_drpdwn_testbed').value;

  var get_result_data_summary_radio_selected = document.getElementById('get_result_data_summary_radio').checked;
  var get_abrt_script_summary_radio_selected = document.getElementById('get_abrt_script_summary_radio').checked;
  var get_failure_analysis_summary_radio_selected = document.getElementById('get_failure_analysis_summary_radio').checked;
  var get_failure_analysis_summary_by_subpkg_type_radio_selected = document.getElementById('get_failure_by_subpkg_type_radio').checked;
  var get_alltestcase_time_by_subpkg_type_radio_selected = document.getElementById('get_alltestcase_time_by_subpkg_type_radio').checked;
  var get_time_taking_scripts_trand_radio_selected = document.getElementById('get_time_taking_scripts_trend_radio').checked;
  var get_skipped_data_summary_radio_selected = document.getElementById('get_skipped_data_summary_radio').checked;

  if (get_result_data_summary_radio_selected == true) {
	URL = "http://localhost/ownerwise_result.py?run_id="+run_id;
  } else if (get_skipped_data_summary_radio_selected == true) {
        URL = "http://zarms.corp.zscaler.com:82/cgi-bin/TestBedMonitor/skipped_scripts_data.pl?run_ids="+run_id;
  } else if (get_abrt_script_summary_radio_selected == true) {
	URL = "http://localhost/ownerwise_result_abrt_script_data.py?run_id="+run_id;
  } else if (get_failure_analysis_summary_radio_selected == true) {
	URL = "http://zarms.corp.zscaler.com:82/cgi-bin/TestBedMonitor/IntelliJError_logs.pl?run_ids="+run_id;
  } else if (get_failure_analysis_summary_by_subpkg_type_radio_selected == true) {
	URL= "http://zarms.corp.zscaler.com:82/cgi-bin/TestBedMonitor/result_data_by_subpkg_type.pl?run_id="+run_id;
  } else if (get_alltestcase_time_by_subpkg_type_radio_selected == true) {
        URL= "http://zarms.corp.zscaler.com:82/cgi-bin/TestBedMonitor/result_time_data_by_subpkg.pl?run_id="+run_id;
  } else if (get_time_taking_scripts_trand_radio_selected == true) {
          if (selected_subpkg == 'none' || selected_build == 'none') {
          alert("Please select values from dropdown!");
                  URL = '';
          } else{
        URL = "http://zarms.corp.zscaler.com:82/cgi-bin/TestBedMonitor/GenerateExecutionTrend.pl?selected_build="+selected_build+"&selected_subpkg="+selected_subpkg+"&selected_testbed_id="+selected_testbed_id+"&timeout_val="+document.getElementById('timeoutTxt').value;
          }
  }

  load_iframe(URL);
}

function load_iframe(URL){
    var frame = document.getElementById("demo"),
    frameDoc = frame.contentDocument || frame.contentWindow.document;
    frameDoc.documentElement.innerHTML="";
    document.getElementById("demo").src = URL;
}

$(document).ready(function(){
    $("#select_drpdwn_package").change(function(){
            var pkgid = $(this).val();

$.ajax({
            url: 'http://localhost/getSubpkgnames.php',
            type: 'post',
            data: {packageid:pkgid},
            dataType: 'json',
            success:function(response){

                var len = response.length;
                $("#select_drpdwn_subpackage").empty();
                for( var i = 0; i<len; i++){
                    var subpkgid = response[i]['subpkgid'];
                    var subpkgname = response[i]['subpkgname'];

                    $("#select_drpdwn_subpackage").append("<option value='"+subpkgid+"'>"+subpkgname subpkgid+"</option>");

                }
            }
        });
    });

   });

</script>

</body>
</html>