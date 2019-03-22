//Entry Points to get amounts
var bookingallotment_amounts_url = base_url + 'booking/bookingallotment-amounts/';

$(document).ready(function(){
  $('#bookingallotment_form #id_cost_amount').after("<button class='btn btn-success btn-copy btn-copy-cost'><<</button><span class='computed-value'>Calculated: <b data-computed=cost>N/A</b></span>");
  $('#bookingallotment_form #id_price_amount').after("<button class='btn btn-success btn-copy btn-copy-price'><<</button><span class='computed-value'>Calculated: <b data-computed=price>N/A</b></span>");

  var computedCost = $('b[data-computed=cost]');
  var computedPrice = $('b[data-computed=price]');

  var costInput = $('#id_cost_amount')[0];
  var priceInput = $('#id_price_amount')[0];

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
      if(data['cost_message']){
        computedCost.html(data['cost_message']);
      }
      else{
        computedCost.html(data['cost']);
      }
      if(data['price_message']){
        computedPrice.html(data['price_message']);
      }
      else{
        computedPrice.html(data['price']);
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

  data = $('#bookingallotment_form').serialize();
  get_computed_amounts(bookingallotment_amounts_url, data);

  $('#bookingallotment_form input, #bookingallotment_form select').on('change', function(){
    data = $('#bookingallotment_form').serialize();
    get_computed_amounts(bookingallotment_amounts_url, data);
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

});
