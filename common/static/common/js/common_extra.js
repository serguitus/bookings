//Entry Points to get prices for each booking_service
var bookingallotment_url = '/bookings/booking/amounts/';
var bookingtransfer_url = '/';
var bookingextra_url = '/';

$(document).ready(function(){
  $('#bookingallotment_form #id_cost_amount').after("<span class='computed-value'>Calculated: <b data-computed=cost>N/A</b></span>");
  $('#bookingallotment_form #id_price_amount').after("<span class='computed-value'>Calculated: <b data-computed=price>N/A</b></span>");

  var computedCost = $('b[data-computed=cost]');
  var computedPrice = $('b[data-computed=price]');
  var costInputContainer = $('div.field-cost_amount');

  function get_computed_amounts(url, form_dict){
    console.log('cambió!!');
    computedCost.html('Loading...');
    computedPrice.html('Loading...');
    // sending a request to get computed numbers
    $.ajax({
      'url': bookingallotment_url,
      'async': true,
      'datatype': 'json',
      'type': 'POST',
      'data': $('#bookingallotment_form').serialize()
    }).done(function(data){
      computedCost.html(data['cost']);
      computedPrice.html(data['price']);
      console.log('llego dato valido');
    }).fail(function(){
      computedCost.html('N/A');
      computedPrice.html('N/A');
    })
  }

  $('#bookingallotment_form input, #bookingallotment_form select').on('change', function(){
    data = $('#bookingallotment_form').serialize();
    get_computed_amounts(bookingallotment_url, data)
  });

  $('#bookingtransfer_form input, #bookingtransfer_form select').on('change', function(){
    data = $('#bookingtransfer_form').serialize();
    get_computed_amounts(bookingtransfer_url, data)
  });

  $('#bookingextra_form input, #bookingextra_form select').on('change', function(){
    data = $('#bookingextra_form').serialize();
    get_computed_amounts(bookingextra_url, data)
  });


});
