
function get_service_details(){
  if (service_details_url) {
    $.ajax({
      'url': service_details_url,
      'async': true,
      'datatype': 'json',
      'type': 'POST',
      'data': $(service_form_selector).serialize(),
    }).done(function(data){
      update_service_details(data);
    }).fail(function(){
    })
  }
}

function update_service_details(data){
  if (data && data.car_rental) {
    $('div.form-row.field-pickup_office.field-dropoff_office').show();
  } else {
    $('div.form-row.field-pickup_office.field-dropoff_office').hide();
  }
}

$(document).ready(function(){
  $('#id_service').change(function (e) {
    e.preventDefault();
    get_service_details();
  });
  get_service_details();
});