//Entry Points to get prices for each booking_service
var bookingallotment_url = '/bookings/booking/amounts/';
var bookingtransfer_url = '/';
var bookingextra_url = '/';

$(document).ready(function(){
  $('#bookingallotment_form #id_cost_amount').after("<span class='computed-value'>Calculated: <b data-computed=cost>N/A</b></span>");
  $('#bookingallotment_form #id_price_amount').after("<span class='computed-value'>Calculated: <b data-computed=price>N/A</b></span>");
  $('#bookingtransfer_form #id_cost_amount').after("<span class='computed-value'>Calculated: <b data-computed=cost>N/A</b></span>");
  $('#bookingtransfer_form #id_price_amount').after("<span class='computed-value'>Calculated: <b data-computed=price>N/A</b></span>");
    $('#bookingextra_form #id_cost_amount').after("<span class='computed-value'>Calculated: <b data-computed=cost>N/A</b></span>");
  $('#bookingextra_form #id_price_amount').after("<span class='computed-value'>Calculated: <b data-computed=price>N/A</b></span>");


  var computedCost = $('b[data-computed=cost]');
  var computedPrice = $('b[data-computed=price]');
  var costInputContainer = $('div.field-cost_amount');

  function get_computed_amounts(url, form_dict){
    computedCost.html('Loading...');
    computedPrice.html('Loading...');
    // sending a request to get computed numbers
    $.ajax({
      'url': bookingallotment_url,
      'async': true,
      'datatype': 'json',
      'type': 'POST',
      'data': form_dict,
    }).done(function(data){
      if(data['cost']){
        computedCost.html(data['cost']);
      }
      else{
        computedCost.html('N/A');
      }
      if(data['price']){
        computedPrice.html(data['price']);
      }
      else{
        computedPrice.html('N/A');
      }
    }).fail(function(){
      computedCost.html('N/A');
      computedPrice.html('N/A');
    })
  }

  $('#bookingallotment_form input, #bookingallotment_form select').on('change', function(){
    data = $('#bookingallotment_form').serialize();
    get_computed_amounts(bookingallotment_url, data);
  });

  $('#bookingtransfer_form input, #bookingtransfer_form select').on('change', function(){
    data = $('#bookingtransfer_form').serialize();
    get_computed_amounts(bookingtransfer_url, data);
  });

  $('#bookingextra_form input, #bookingextra_form select').on('change', function(){
    data = $('#bookingextra_form').serialize();
    get_computed_amounts(bookingextra_url, data);
  });


});
