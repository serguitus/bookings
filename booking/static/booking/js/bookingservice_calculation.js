//Entry Points to get amounts for each booking_service
var bookingservice_amounts_url = base_url + 'booking/bookingservice-amounts/';
//Entry Points to get time for booking transfer
var bookingtransfer_time_url = base_url + 'booking/bookingtransfer-time/';
var time_autofilled = false;

$(document).ready(function(){
  $('#bookingallotment_form #id_cost_amount').after("<button class='btn btn-success btn-copy btn-copy-cost'><<</button><span class='computed-value'>Calculated: <b data-computed=cost>N/A</b></span>");
  $('#bookingallotment_form #id_price_amount').after("<button class='btn btn-success btn-copy btn-copy-price'><<</button><span class='computed-value'>Calculated: <b data-computed=price>N/A</b></span>");
  $('#bookingtransfer_form #id_cost_amount').after("<button class='btn btn-success btn-copy btn-copy-cost'><<</button><span class='computed-value'>Calculated: <b data-computed=cost>N/A</b></span>");
  $('#bookingtransfer_form #id_price_amount').after("<button class='btn btn-success btn-copy btn-copy-price'><<</button><span class='computed-value'>Calculated: <b data-computed=price>N/A</b></span>");
  $('#bookingextra_form #id_cost_amount').after("<button class='btn btn-success btn-copy btn-copy-cost'><<</button><span class='computed-value'>Calculated: <b data-computed=cost>N/A</b></span>");
  $('#bookingextra_form #id_price_amount').after("<button class='btn btn-success btn-copy btn-copy-price'><<</button><span class='computed-value'>Calculated: <b data-computed=price>N/A</b></span>");

  $('#bookingtransfer_form #id_time').after("<button class='btn btn-success btn-copy btn-copy-time'><<</button><span class='computed-value'>Calculated: <b data-computed=time>N/A</b></span>");

  var computedCost = $('b[data-computed=cost]');
  var computedPrice = $('b[data-computed=price]');
  var computedTime = $('b[data-computed=time]');

  var costInput = $('#id_cost_amount')[0];
  var priceInput = $('#id_price_amount')[0];
  var timeInput = $('#id_time')[0];

  var calcCost = $('div.field-box.field-calculated_cost').children()[1];
  var calcPrice = $('div.field-box.field-calculated_price').children()[1];
  var calcTime = $('div.field-box.field-calculated_time').children()[1];

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

  function compare_time(evt) {
    // a function to check if computed values differ from set values
    // it highlights different values
    if (timeInput.value == '') {
      if (is_time(computedTime.html())) {
        timeInput.value = computedTime.html();
        time_autofilled = true;
        $('.btn-copy-time').removeClass('btn-danger');
        $('.btn-copy-time').removeClass('btn-warning');
        $('.btn-copy-time').addClass('btn-success');
        return 0;
      }
      time_autofilled = false;
      $('.btn-copy-time').removeClass('btn-danger');
      $('.btn-copy-time').removeClass('btn-warning');
      $('.btn-copy-time').removeClass('btn-success');
      return 0;
    }
    if (time_autofilled) {
      if (evt.target.id != 'id_time') {
        if (is_time(computedTime.html())) {
          timeInput.value = computedTime.html();
          $('.btn-copy-time').removeClass('btn-danger');
          $('.btn-copy-time').removeClass('btn-warning');
          $('.btn-copy-time').addClass('btn-success');
          return 0;
        }
        timeInput.value = '';
        $('.btn-copy-time').removeClass('btn-danger');
        $('.btn-copy-time').removeClass('btn-warning');
        $('.btn-copy-time').removeClass('btn-success');
        return 0;
      }
      time_autofilled = false;
    }
    return compare_time_values();
  }
    
  function compare_time_values() {
    if (is_time(timeInput.value) && is_time(computedTime.html())) {
      iseconds = seconds(timeInput.value);
      cseconds = seconds(computedTime.html());
      if (iseconds == cseconds){
        $('.btn-copy-time').removeClass('btn-danger');
        $('.btn-copy-time').removeClass('btn-warning');
        $('.btn-copy-time').addClass('btn-success');
        return 0;
      }
      if (iseconds < cseconds) {
          if (cseconds - iseconds < 6 * 3600) {
            $('.btn-copy-time').removeClass('btn-danger');
            $('.btn-copy-time').removeClass('btn-success');
            $('.btn-copy-time').addClass('btn-warning');
            return 0;
          }
          $('.btn-copy-time').removeClass('btn-success');
          $('.btn-copy-time').removeClass('btn-warning');
          $('.btn-copy-time').addClass('btn-danger');
          return 0;
      }
      if (iseconds - cseconds > 18 * 3600) {
        $('.btn-copy-time').removeClass('btn-danger');
        $('.btn-copy-time').removeClass('btn-success');
        $('.btn-copy-time').addClass('btn-warning');
        return 0;
      }
      $('.btn-copy-time').removeClass('btn-success');
      $('.btn-copy-time').removeClass('btn-warning');
      $('.btn-copy-time').addClass('btn-danger');
      return 0;
    }
    $('.btn-copy-time').removeClass('btn-danger');
    $('.btn-copy-time').removeClass('btn-warning');
    $('.btn-copy-time').removeClass('btn-success');
    return 0;
  }

  function is_time(str){
    if (str == '') {
      return true
    }
    var parts = str.split(':');
    for (let index = 0; index < parts.length; index++) {
      if (parts[index] && isNaN(parts[index])) {
        return false;
      }
    }
    return true;
  }

  function seconds(str){
    if (str == '') {
      return 0
    }
    var parts = str.split(':');
    result = 0;
    for (let index = 0; index < parts.length; index++) {
      n = Number(parts[index]);
      m = 1;
      if (index == 0) {
        m = 3600;
      } else if (index == 1) {
        m = 60;
      }
      if (isNaN(n)) {
        return 0;
      } else {
        result += m * n; 
      }
    }
    return result;
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
  function get_computed_time(url, form_dict, evt){
    computedTime.html('Loading...');
    // sending a request to get computed value
    $.ajax({
      'url': url,
      'async': true,
      'datatype': 'json',
      'type': 'POST',
      'data': form_dict,
    }).done(function(data){
      if(data['time']){
        computedTime.html(data['time']);
      } else {
        computedTime.html(data['time_message']);
      }
      compare_time(evt);
    }).fail(function(){
      computedTime.html('N/A');
      compare_time(evt);
    })
  }

  if($('#bookingallotment_form').length){
    data = $('#bookingallotment_form').serialize();
  } else if ($('#bookingtransfer_form').length){
    data = $('#bookingtransfer_form').serialize();
    get_computed_time(bookingtransfer_time_url, data);
  } else if ($('#bookingextra_form').length){
    data = $('#bookingextra_form').serialize();
  }
  get_computed_amounts(bookingservice_amounts_url, data);

  $('#bookingallotment_form input, #bookingallotment_form select').on('change', function(){
    data = $('#bookingallotment_form').serialize();
    get_computed_amounts(bookingservice_amounts_url, data);
  });

  $('#bookingtransfer_form input, #bookingtransfer_form select').on('change', function(evt){
    data = $('#bookingtransfer_form').serialize();
    get_computed_amounts(bookingservice_amounts_url, data);
    get_computed_time(bookingtransfer_time_url, data, evt);
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

  $('.btn-copy-time').on('click', function(e){
    e.preventDefault();
    if(is_time(computedTime.html())){
      timeInput.value = computedTime.html();
    }
    compare_time(e)
  })

});
