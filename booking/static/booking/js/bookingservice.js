$(document).ready(function(){

  // find readonly cost
  var readonlyCost = $('div.field-cost_amount div.readonly');
  var costInput = $('#id_cost_amount');
  var manualCost = $('#id_manual_cost');
  var isManualCost;
  // verify readonly not found
  if (readonlyCost.length == 0) {
    // add button and text
    costInput.after("<button class='btn btn-success btn-copy btn-copy-cost'><<</button><span class='computed-value'>Calculated: <b data-computed=cost>N/A</b></span>");
    isManualCost = manualCost[0].checked;
  } else {
    // add text
    readonlyCost.after("<span class='computed-value'>Calculated: <b data-computed=cost>N/A</b></span>");
    costInput = readonlyCost;
    isManualCost = $('div.field-manual_cost div.readonly img').attr('src').includes('icon-yes');
  }
  computedCost = $('b[data-computed=cost]');

  var readonlyPrice = $('div.field-price_amount div.readonly');
  var priceInput = $('#id_price_amount');
  var manualPrice = $('#id_manual_price');
  var isManualPrice;
  if (readonlyPrice.length == 0) {
    priceInput.after("<button class='btn btn-success btn-copy btn-copy-price'><<</button><span class='computed-value'>Calculated: <b data-computed=price>N/A</b></span>");
    isManualPrice = manualPrice[0].checked;
  } else {
    readonlyPrice.after("<span class='computed-value'>Calculated: <b data-computed=price>N/A</b></span>");
    priceInput = readonlyPrice;
    isManualPrice = $('div.field-manual_price div.readonly img').attr('src').includes('icon-yes');
  }
  computedPrice = $('b[data-computed=price]');

  // define manual value
  changed_manual_cost(isManualCost);
  // define manual value
  changed_manual_price(isManualPrice);

  function compare_numbers() {
    // a function to check if computed prices differ from set prices
    // it highlights different numbers
    if(costInput[0].value != Number(computedCost.html())){
      $('.btn-copy-cost').removeClass('btn-success');
      $('.btn-copy-cost').addClass('btn-danger');
    } else{
      $('.btn-copy-cost').removeClass('btn-danger');
      $('.btn-copy-cost').addClass('btn-success');
    }
    if(priceInput[0].value != Number(computedPrice.html())){
      $('.btn-copy-price').removeClass('btn-success');
      $('.btn-copy-price').addClass('btn-danger');
    } else{
      $('.btn-copy-price').removeClass('btn-danger');
      $('.btn-copy-price').addClass('btn-success');
    }
    return 0
  }

  function get_computed_amounts(){
    computedCost.html('Loading...');
    computedPrice.html('Loading...');
    // sending a request to get computed numbers
    $.ajax({
      'url': bookingservice_amounts_url,
      'async': true,
      'datatype': 'json',
      'type': 'POST',
      'data': $(bookingservice_form_selector).serialize(),
    }).done(function(data){
      if(data['cost_message']){
        computedCost.html(data['cost_message']);
        if (!isManualCost) {
          if (readonlyCost.length == 0) {
            costInput[0].value = '';
          } else {
            costInput.html('');
          }
        }
      }else{
        computedCost.html(data['cost']);
        if (!isManualCost) {
          if (readonlyCost.length == 0) {
            costInput[0].value = Number(data['cost']);
          } else {
            costInput.html(data['cost']);
          }
        }
      }
      if(data['price_message']){
        computedPrice.html(data['price_message']);
        if (!isManualPrice) {
          if (readonlyPrice.length == 0) {
            priceInput[0].value = '';
          } else {
            priceInput.html('');
          }
        }
      }else{
        computedPrice.html(data['price']);
        if (!isManualPrice) {
          if (readonlyPrice.length == 0) {
            priceInput[0].value = Number(data['price']);
          } else {
            priceInput.html(data['price']);
          }
        }
      }
      compare_numbers();
    }).fail(function(){
      computedCost.html('N/A');
      computedPrice.html('N/A');
      compare_numbers();
    })
  }

  get_computed_amounts();

  $(bookingservice_form_selector + ' input, ' + bookingservice_form_selector + ' select').on('change', function(){
    get_computed_amounts();
  });

  function changed_manual_cost(manual){
    isManualCost = manual;
    if(isManualCost){
      $('.btn-copy-cost').show()
    } else {
      $('.btn-copy-cost').hide()
    }
    if (readonlyCost.length == 0) {
      costInput[0].readOnly = !manual;
    }
    get_computed_amounts();
  }

  manualCost.on('change', function(e){
    e.preventDefault();
    changed_manual_cost(manualCost[0].checked);
  })

  function changed_manual_price(manual){
    isManualPrice = manual;
    if(isManualPrice){
      $('.btn-copy-price').show()
    } else {
      $('.btn-copy-price').hide()
    }
    if (readonlyPrice.length == 0) {
      priceInput[0].readOnly = !manual;
    }
    get_computed_amounts();
  }

  $('#id_manual_price').on('change', function(e){
    e.preventDefault();
    changed_manual_price(manualPrice[0].checked);
  })

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
