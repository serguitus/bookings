//Entry Points to get amounts for each booking_service
var bookingservice_amounts_url = base_url + 'booking/bookingservice-amounts/';
//Entry Points to get times for booking transfer
var bookingtransfer_times_url = base_url + 'booking/bookingtransfer-times/';

$(document).ready(function(){
  $('#bookingallotment_form #id_cost_amount').after("<button class='btn btn-success btn-copy btn-copy-cost'><<</button><span class='computed-value'>Calculated: <b data-computed=cost>N/A</b></span>");
  $('#bookingallotment_form #id_price_amount').after("<button class='btn btn-success btn-copy btn-copy-price'><<</button><span class='computed-value'>Calculated: <b data-computed=price>N/A</b></span>");
  $('#bookingtransfer_form #id_cost_amount').after("<button class='btn btn-success btn-copy btn-copy-cost'><<</button><span class='computed-value'>Calculated: <b data-computed=cost>N/A</b></span>");
  $('#bookingtransfer_form #id_price_amount').after("<button class='btn btn-success btn-copy btn-copy-price'><<</button><span class='computed-value'>Calculated: <b data-computed=price>N/A</b></span>");
  $('#bookingextra_form #id_cost_amount').after("<button class='btn btn-success btn-copy btn-copy-cost'><<</button><span class='computed-value'>Calculated: <b data-computed=cost>N/A</b></span>");
  $('#bookingextra_form #id_price_amount').after("<button class='btn btn-success btn-copy btn-copy-price'><<</button><span class='computed-value'>Calculated: <b data-computed=price>N/A</b></span>");

  $('#bookingtransfer_form #id_pickup_time').after("<button class='btn btn-success btn-copy btn-copy-pickup-time'><<</button><span class='computed-value'>Calculated: <b data-computed=pickup-time>N/A</b></span>");
  $('#bookingtransfer_form #id_dropoff_time').after("<button class='btn btn-success btn-copy btn-copy-dropoff-time'><<</button><span class='computed-value'>Calculated: <b data-computed=dropoff-time>N/A</b></span>");

  var computedCost = $('b[data-computed=cost]');
  var computedPrice = $('b[data-computed=price]');
  var computedPickupTime = $('b[data-computed=pickup-time]');
  var computedDropoffTime = $('b[data-computed=dropoff-time]');

  var costInput = $('#id_cost_amount')[0];
  var priceInput = $('#id_price_amount')[0];
  var pickupTimeInput = $('#id_pickup_time')[0];
  var dropoffTimeInput = $('#id_dropoff_time')[0];

  var calcCost = $('div.field-box.field-calculated_cost').children()[1];
  var calcPrice = $('div.field-box.field-calculated_price').children()[1];
  var calcPickupTime = $('div.field-box.field-calculated_pickup_time').children()[1];
  var calcDropoffTime = $('div.field-box.field-calculated_dropoff_time').children()[1];

  function compare_numbers() {
    // a function to check if computed prices differ from set prices
    // it highlights different numbers
    if(costInput.value != Number(computedCost.html())){
      $('.btn-copy-cost').removeClass('btn-success');
      $('.btn-copy-cost').addClass('btn-danger');
    } else{
      $('.btn-copy-cost').removeClass('btn-danger');
      $('.btn-copy-cost').addClass('btn-success');
    }
    if(priceInput.value != Number(computedPrice.html())){
      $('.btn-copy-price').removeClass('btn-success');
      $('.btn-copy-price').addClass('btn-danger');
    } else{
      $('.btn-copy-price').removeClass('btn-danger');
      $('.btn-copy-price').addClass('btn-success');
    }
    return 0
  }

  function compare_times() {
    // a function to check if computed values differ from set values
    // it highlights different values
    if(pickupTimeInput.value != Number(computedPickupTime.html())){
      $('.btn-copy-pickup-time').removeClass('btn-success');
      $('.btn-copy-pickup-time').addClass('btn-danger');
    } else{
      $('.btn-copy-pickup-time').removeClass('btn-danger');
      $('.btn-copy-pickup-time').addClass('btn-success');
    }
    if(dropoffTimeInput.value != Number(computedDropoffTime.html())){
      $('.btn-copy-dropoff-time').removeClass('btn-success');
      $('.btn-copy-dropoff-time').addClass('btn-danger');
    } else{
      $('.btn-copy-dropoff-time').removeClass('btn-danger');
      $('.btn-copy-dropoff-time').addClass('btn-success');
    }
    return 0
  }

  function get_computed_amounts(url, form_dict){
    computedCost.html('Loading...');
    computedPrice.html('Loading...');
    // sending a request to get computed numbers
    $.ajax({
      'url': url,
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
      compare_numbers();
    }).fail(function(){
      computedCost.html('N/A');
      computedPrice.html('N/A');
      compare_numbers();
    })
  }
  function get_computed_times(url, form_dict){
    computedPickupTime.html('Loading...');
    computedDropoffTime.html('Loading...');
    // sending a request to get computed values
    $.ajax({
      'url': url,
      'async': true,
      'datatype': 'json',
      'type': 'POST',
      'data': form_dict,
    }).done(function(data){
      if(data['pickup_time']){
        computedPickupTime.html(data['pickup_time']);
      } else {
        computedPickupTime.html(data['pickup_time_message']);
      }
      if(data['dropoff_time']){
        computedDropoffTime.html(data['dropoff_time']);
      } else {
        computedDropoffTime.html(data['dropoff_time_message']);
      }
      compare_times();
    }).fail(function(){
      computedPickupTime.html('N/A');
      computedDropoffTime.html('N/A');
      compare_times();
    })
  }

  if($('#bookingallotment_form').length){
    data = $('#bookingallotment_form').serialize();
  } else if ($('#bookingtransfer_form').length){
    data = $('#bookingtransfer_form').serialize();
    get_computed_times(bookingtransfer_times_url, data);
  } else if ($('#bookingextra_form').length){
    data = $('#bookingextra_form').serialize();
  }
  get_computed_amounts(bookingservice_amounts_url, data);

  $('#bookingallotment_form input, #bookingallotment_form select').on('change', function(){
    data = $('#bookingallotment_form').serialize();
    get_computed_amounts(bookingservice_amounts_url, data);
  });

  $('#bookingtransfer_form input, #bookingtransfer_form select').on('change', function(){
    data = $('#bookingtransfer_form').serialize();
    get_computed_amounts(bookingservice_amounts_url, data);
    get_computed_times(bookingtransfer_times_url, data);
  });

  $('#bookingextra_form input, #bookingextra_form select').on('change', function(){
    data = $('#bookingextra_form').serialize();
    get_computed_amounts(bookingservice_amounts_url, data);
  });

  $('.btn-copy-cost').on('click', function(e){
    e.preventDefault();
    if(Number(computedCost.html())){
      costInput.value = Number(computedCost.html());
    }
    compare_numbers()
  })

  $('.btn-copy-price').on('click', function(e){
    e.preventDefault();
    if(Number(computedPrice.html())){
      priceInput.value = Number(computedPrice.html());
    }
    compare_numbers()
  })

  $('.btn-copy-pickup-time').on('click', function(e){
    e.preventDefault();
    if(Number(computedPickupTime.html())){
      pickupTimeInput.value = Number(computedPickupTime.html());
    }
    compare_times()
  })

  $('.btn-copy-dropoff-time').on('click', function(e){
    e.preventDefault();
    if(Number(computedDropoffTime.html())){
      dropoffTimeInput.value = Number(computedDropoffTime.html());
    }
    compare_times()
  })

});
