(function($){
function get_book_details(){
  if (typeof book_details_url !== 'undefined') {
    $.ajax({
      'url': book_details_url,
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
  if (data && data.has_place_from) {
    $('div.field-box.field-place_from').show();
  } else {
    $('div.field-box.field-place_from').hide();
  }
  if (data && data.has_place_to) {
    $('div.field-box.field-place_to').show();
  } else {
    $('div.field-box.field-place_to').hide();
  }
}

$(document).ready(function(){
  $('#id_service').change(function (e) {
    e.preventDefault();
    get_book_details();
  });
  $('#id_location_from').change(function (e) {
    e.preventDefault();
    get_book_details();
  });
  $('#id_location_to').change(function (e) {
    e.preventDefault();
    get_book_details();
  });
  get_book_details();
});

})(django.jQuery)
