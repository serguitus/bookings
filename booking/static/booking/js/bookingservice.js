$(document).ready(function(){

  function get_computed_amounts(){
    // sending a request to get computed numbers
    $.ajax({
      'url': bookingservice_amounts_url,
      'async': true,
      'datatype': 'json',
      'type': 'POST',
      'data': $(bookingservice_form_selector).serialize(),
    }).done(function(data){
      update_amounts(false, data['cost'], data['cost_message']);
      update_amounts(true, data['price'], data['price_message']);
      compare_all_amounts();
    }).fail(function(){
      clear_values('N/A');
    })
  }

  function update_amounts(for_price, data_amount, data_amount_msg){
    if (for_price) {
      amount_text = 'price';
    } else {
      amount_text = 'cost';
    }
    sa = $('#span-' + amount_text);
    if (data_amount) {
      sa.html(data_amount);
    } else {
      sa.html(data_amount_msg);
    }
  }

  function changed_manual_cost(target){
    isManualCost = target.checked;
    if(isManualCost){
      $('.btn-copy-cost').show()
    } else {
      $('.btn-copy-cost').hide()
    }
    $('#id_cost_amount')[0].readOnly = !isManualCost;
    get_computed_amounts();
  }

  function changed_manual_price(target){
    isManualPrice = target.checked;
    if (isManualPrice){
      $('.btn-copy-price').show()
    } else {
      $('.btn-copy-price').hide()
    }
    $('#id_price_amount')[0].readOnly = !isManualPrice;
    get_computed_amounts();
  }

  function clear_values(msg) {
    $('span.computed-value').each(function(index) {
      $( this ).html(msg);
    });
    $('button.btn-copy').each(function(index) {
      $( this ).removeClass('btn-success');
      $( this ).addClass('btn-danger');
    });
  }

  function compare_all_amounts() {
    ic = $('#id_cost_amount');
    sc = $('#span-cost');
    bc = $('#btn-cost');
    compare_amounts(ic, sc, bc);
    ip = $('#id_price_amount');
    sp = $('#span-price');
    bp = $('#btn-price');
    compare_amounts(ip, sp, bp);
  }

  function compare_amounts(input, span, btn) {
    iv = Number(input.val());
    sv = Number(span.html());
    if(sv && iv && sv == iv){
      btn.removeClass('btn-danger');
      btn.addClass('btn-success');
    } else{
      btn.removeClass('btn-success');
      btn.addClass('btn-danger');
    }
  }

  function show_buttons() {
    $('.btn-copy-cost').detach();
    $('.btn-copy-price').detach();
    field = $('#id_cost_amount');
    if (field[0] != undefined) {
      $('#id_cost_amount').after('<button id="btn-cost" class="btn btn-copy-cost"><<</button><span id="span-cost" class="computed-value">N/A</span>');
      $('#id_price_amount').after('<button id="btn-price" class="btn btn-copy-price"><<</button><span id="span-price" class="computed-value">N/A</span>');
      changed_manual_cost($('#id_manual_cost')[0]);
      changed_manual_price($('#id_manual_price')[0]);
    } else {
      field = $('div.field-cost_amount div.readonly');
      if (field[0] != undefined) {
        $('div.field-cost_amount div.readonly').after('<span id="span-cost" class="computed-value">N/A</span>');
        $('div.field-price_amount div.readonly').after('<span id="span-price" class="computed-value">N/A</span>');
      }
    }

    $('.btn-copy-cost').on('click', function(e){
      e.preventDefault();
      button = $(this);
      input = button.prev();
      span = button.next();
      number = Number(span.html());
      if (number) {
        input.val(number);
        compare_amounts(input, span, button);
        get_computed_amounts();
      }
      return false;
    });

    $('.btn-copy-price').on('click', function(e){
      e.preventDefault();
      button = $(this);
      input = button.prev();
      span = button.next();
      number = Number(span.html());
      if (number) {
        input.val(number);
        compare_amounts(input, span, button);
        get_computed_amounts();
      }
      return false;
    });
  }

  show_buttons();
  get_computed_amounts();

  $(bookingservice_form_selector + ' input, ' + bookingservice_form_selector + ' select').on('change', function(){
    get_computed_amounts();
  });

  // for dates changed by calendar
  $(bookingservice_form_selector + ' input[name*="date"]').focusout(function (e) {
    e.preventDefault();
    get_computed_amounts();
  });
  // for times changed by calendar
  $(bookingservice_form_selector + ' input[name*="time"]').focusout(function (e) {
    e.preventDefault();
    get_computed_amounts();
  });

  $('#id_manual_cost').on('change', function(e){
    e.preventDefault();
    changed_manual_cost(e.target);
  })

  $('#id_manual_price').on('change', function(e){
    e.preventDefault();
    changed_manual_price(e.target);
  })

  // for service changed
  $('#id_service').change(function (e) {
    e.preventDefault();
    // clear data
    $('#id_room_type').val(null).trigger('change');
    $('#id_board_type').val(null).trigger('change');
    $('#id_provider').val(null).trigger('change');
    //$('#id_board option').prop("selected", false);
    //$('#id_board_type').select();

    $('#id_location_from').select();
    $('#id_location_to').select();

    $('#id_addon').select();

    //$('#id_provider').select();
    get_computed_amounts();
  });

});
