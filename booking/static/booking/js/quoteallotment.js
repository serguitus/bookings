var quoteservice_amounts_url = base_url + 'booking/quoteallotment-amounts/';
var service_form_selector = '#quoteallotment_form';
var providers_costs_url = base_url + 'booking/quoteallotment-providers-costs/';

$(document).ready(function(){
  var nights_selector = $('#id_nights');
  var start_selector = $('#id_datetime_from');
  var end_selector = $('#id_datetime_to');

  update_nights();
  nights_selector.on('change', function(){
    update_end_date();
  });
  end_selector.on('change', function(){
    update_nights();
  });
  start_selector.on('change', function(){
    update_end_date();
  });
})


/*
This function converts string with format DDMMYY or format DD-MM-YY
 to valid Date objects. Returns nothing on other formats
*/
/****** TODO unify this methods from bookingservice and quoteservices to avoid duplicates****/
function get_date_from_string(date_str){
  var parts =date_str.split('-');
  if(parts[0].length == 6){
    // working with date format DDMMYY
    var date_list = parts[0].match(/.{1,2}/g);
    var result_date = new Date(date_list[2].padStart(4, '20'), date_list[1]-1, date_list[0])
    return result_date;
  }else if(parts[0].length == 2){
    var result_date = new Date(parts[2].padStart(4, '20'), parts[1]-1, parts[0]);
    return result_date;
  }else{
    // unknown format. Do nothing
    return
  }
}


function update_end_date(){
  var nights = $('#id_nights');
  var start_selector = $('#id_datetime_from');
  var end_selector = $('#id_datetime_to');
  if(start_selector.val() && nights.val()){
    var start_date = get_date_from_string(start_selector.val());
    var computed_end = addDays(start_date, Number(nights.val()));
    var curr_date = computed_end.getDate().toString().padStart(2, '0');
    var curr_month = (computed_end.getMonth() + 1).toString().padStart(2, '0'); //Months are zero based
    var curr_year = computed_end.getFullYear();
    end_selector.val(curr_date + '-' + curr_month + '-' + curr_year)
  }
}

function update_nights(){
  var nights_selector = $('#id_nights');
  var start_selector = $('#id_datetime_from');
  var end_selector = $('#id_datetime_to');
  if(start_selector.val() && end_selector.val()){
    var parts =start_selector.val().split('-');
    var start_date = new Date(parts[2], parts[1] - 1, parts[0]);
    var parts2 =end_selector.val().split('-');
    var end_date = new Date(parts2[2], parts2[1] - 1, parts2[0]);
    var nights = days_diff(start_date, end_date);
    nights_selector.val(nights);
  }
}

function addDays(date, days) {
    var result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
}

function days_diff(date1, date2) {
    dt1 = new Date(date1);
    dt2 = new Date(date2);
    return Math.floor((Date.UTC(dt2.getFullYear(), dt2.getMonth(), dt2.getDate()) - Date.UTC(dt1.getFullYear(), dt1.getMonth(), dt1.getDate()) ) /(1000 * 60 * 60 * 24));
}
