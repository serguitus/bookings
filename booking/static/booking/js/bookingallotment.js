//Entry Points to get amounts
var bookingallotment_amounts_url = base_url + 'booking/bookingallotment-amounts/';

$(document).ready(function(){

  var computedCost = $('#bookingallotment_form div.field-cost_amount div.readonly');
  if (computedCost.length == 0) {
    $('#bookingallotment_form #id_cost_amount').after("<button class='btn btn-success btn-copy btn-copy-cost'><<</button><span class='computed-value'>Calculated: <b data-computed=cost>N/A</b></span>");
    computedCost = $('b[data-computed=cost]');
  } else {
    $('div.field-box.field-manual_cost').hide();
  }

  var computedPrice = $('#bookingallotment_form div.field-price_amount div.readonly');
  if (computedPrice.length == 0) {
    $('#bookingallotment_form #id_price_amount').after("<button class='btn btn-success btn-copy btn-copy-price'><<</button><span class='computed-value'>Calculated: <b data-computed=price>N/A</b></span>");
    computedPrice = $('b[data-computed=price]');
  } else {
    $('div.field-manual_price').hide();
  }

  var manualCost = $('#id_manual_cost')[0];
  var manualPrice = $('#id_manual_price')[0];

  var costInput = $('#id_cost_amount')[0];
  var priceInput = $('#id_price_amount')[0];

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
        if (manualCost && !manualCost.checked) {
          costInput.value = '';
        }
      }else{
        computedCost.html(data['cost']);
        if (manualCost && !manualCost.checked) {
          costInput.value = Number(data['cost']);
        }
      }
      if(data['price_message']){
        computedPrice.html(data['price_message']);
        if (manualPrice && !manualPrice.checked) {
          priceInput.value = '';
        }
      }else{
        computedPrice.html(data['price']);
        if (manualPrice && !manualPrice.checked) {
          priceInput.value = Number(data['price']);
        }
      }
      compare_numbers();
    }).fail(function(){
      computedCost.html('N/A');
      computedPrice.html('N/A');
      compare_numbers();
    })
  }

  data = $('#bookingallotment_form').serialize();
  get_computed_amounts(bookingallotment_amounts_url, data);

  $('#bookingallotment_form input, #bookingallotment_form select').on('change', function(){
    data = $('#bookingallotment_form').serialize();
    get_computed_amounts(bookingallotment_amounts_url, data);
  });

  function changed_manual_cost(){
    if(manualCost.checked){
      $('.btn-copy-cost').show()
      costInput.readOnly = false;
    } else {
      $('.btn-copy-cost').hide()
      costInput.readOnly = true;
      data = $('#bookingallotment_form').serialize();
      get_computed_amounts(bookingallotment_amounts_url, data);
    }
    compare_numbers()
  }

  $('#id_manual_cost').on('change', function(e){
    e.preventDefault();
    changed_manual_cost();
  })
  changed_manual_cost();

  function changed_manual_price(){
    if(manualPrice.checked){
      $('.btn-copy-price').show()
      priceInput.readOnly = false;
    } else {
      $('.btn-copy-price').hide()
      priceInput.readOnly = true;
      data = $('#bookingallotment_form').serialize();
      get_computed_amounts(bookingallotment_amounts_url, data);
    }
    compare_numbers()
  }

  $('#id_manual_price').on('change', function(e){
    e.preventDefault();
    changed_manual_price();
  })
  changed_manual_price();

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
