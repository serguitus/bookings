$(document).ready(function(){

  $('select[name^="quoteservice_paxvariants-"][name$="-quote_pax_variant"]').attr('disabled', true);

  $('div.form-row.field-provider>div>div.related-widget-wrapper').after('<a id="btn-costs" title="Costs" data-toggle="modal" data-target="#popup-costs" class="btn btn-costs fa fa-dollar" href="#"></a>');

  $('#btn-costs').on('click', function (e) {
    get_providers_costs();
  });

  function get_computed_amounts() {
    if (typeof quoteservice_amounts_url == 'undefined') {
      return;
    }
    if($(service_form_selector).length){
      $('select[name^="quoteservice_paxvariants-"][name$="-quote_pax_variant"]').attr('disabled', false);
      data = $(service_form_selector).serialize();
      $('select[name^="quoteservice_paxvariants-"][name$="-quote_pax_variant"]').attr('disabled', true);
    }
    $.ajax({
      'url': quoteservice_amounts_url,
      'async': true,
      'datatype': 'json',
      'type': 'POST',
      'data': data,
    }).done(function(data){
      if(data['code'] == 0){
        values = data['results'];
        values.forEach(pax_data => {
          quote_pax_variant_id = pax_data.quote_pax_variant;
          // find variant index
          for (idx = 0; idx < 50; idx++) {
            quote_pax_variant_input = $('#id_quoteservice_paxvariants-' + idx + '-quote_pax_variant');
            quote_pax_variant_value = Number(quote_pax_variant_input.val());
            if (quote_pax_variant_value && quote_pax_variant_value == quote_pax_variant_id) {
              update_amounts(false, idx, 1, pax_data.total.cost_1, pax_data.total.cost_1_msg);
              update_amounts(false, idx, 2, pax_data.total.cost_2, pax_data.total.cost_2_msg);
              update_amounts(false, idx, 3, pax_data.total.cost_3, pax_data.total.cost_3_msg);
              update_amounts(false, idx, 4, pax_data.total.cost_4, pax_data.total.cost_4_msg);
              update_amounts(true, idx, 1, pax_data.total.price_1, pax_data.total.price_1_msg);
              update_amounts(true, idx, 2, pax_data.total.price_2, pax_data.total.price_2_msg);
              update_amounts(true, idx, 3, pax_data.total.price_3, pax_data.total.price_3_msg);
              update_amounts(true, idx, 4, pax_data.total.price_4, pax_data.total.price_4_msg);
            }
          }
        });
        compare_all_amounts();  
      }else{
        clear_values(data['message']);
      }
    }).fail(function(){
      clear_values('N/A');
    })
  }

  function update_amounts(for_price, idx, amount_idx, data_amount, data_amount_msg){
    if (for_price) {
      amount_letter = 'p';
      amount_text = 'price';
    } else {
      amount_letter = 'c';
      amount_text = 'cost';
    }
    sa = $('#' + idx + '-span-' + amount_letter + amount_idx);
    if (data_amount) {
      sa.html(data_amount);
    } else {
      sa.html(data_amount_msg);
    }
  }

  function changed_manual_costs(target){
    isManualCost = target.checked;
    // find index
    idx = target.name.substring(25, target.name.length - 13);
    if(isManualCost){
      $('#' + idx + '-btn-c1').show();
      $('#' + idx + '-btn-c2').show();
      $('#' + idx + '-btn-c3').show();
      $('#' + idx + '-btn-c4').show();
    } else {
      $('#' + idx + '-btn-c1').hide();
      $('#' + idx + '-btn-c2').hide();
      $('#' + idx + '-btn-c3').hide();
      $('#' + idx + '-btn-c4').hide();
    }
    $('#id_quoteservice_paxvariants-' + idx + '-cost_single_amount')[0].readOnly = !isManualCost;
    $('#id_quoteservice_paxvariants-' + idx + '-cost_double_amount')[0].readOnly = !isManualCost;
    $('#id_quoteservice_paxvariants-' + idx + '-cost_triple_amount')[0].readOnly = !isManualCost;
    $('#id_quoteservice_paxvariants-' + idx + '-cost_qdrple_amount')[0].readOnly = !isManualCost;
    get_computed_amounts();
  }

  function changed_manual_prices(target){
    isManualPrice = target.checked;
    idx = target.name.substring(25, target.name.length - 14);
    if(isManualPrice){
      $('#' + idx + '-btn-p1').show();
      $('#' + idx + '-btn-p2').show();
      $('#' + idx + '-btn-p3').show();
      $('#' + idx + '-btn-p4').show();
    } else {
      $('#' + idx + '-btn-p1').hide();
      $('#' + idx + '-btn-p2').hide();
      $('#' + idx + '-btn-p3').hide();
      $('#' + idx + '-btn-p4').hide();
    }
    $('#id_quoteservice_paxvariants-' + idx + '-price_single_amount')[0].readOnly = !isManualPrice;
    $('#id_quoteservice_paxvariants-' + idx + '-price_double_amount')[0].readOnly = !isManualPrice;
    $('#id_quoteservice_paxvariants-' + idx + '-price_triple_amount')[0].readOnly = !isManualPrice;
    $('#id_quoteservice_paxvariants-' + idx + '-price_qdrple_amount')[0].readOnly = !isManualPrice;
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
    for (idx = 0; idx < 50; idx++) {
      ic1 = $('#id_quoteservice_paxvariants-' + idx + '-cost_single_amount');
      sc1 = $('#' + idx + '-span-c1');
      bc1 = $('#' + idx + '-btn-c1');
      compare_amounts(ic1, sc1, bc1);
      ic2 = $('#id_quoteservice_paxvariants-' + idx + '-cost_double_amount');
      sc2 = $('#' + idx + '-span-c2');
      bc2 = $('#' + idx + '-btn-c2');
      compare_amounts(ic2, sc2, bc2);
      ic3 = $('#id_quoteservice_paxvariants-' + idx + '-cost_triple_amount');
      sc3 = $('#' + idx + '-span-c3');
      bc3 = $('#' + idx + '-btn-c3');
      compare_amounts(ic3, sc3, bc3);
      ic4 = $('#id_quoteservice_paxvariants-' + idx + '-cost_qdrple_amount');
      sc4 = $('#' + idx + '-span-c4');
      bc4 = $('#' + idx + '-btn-c4');
      compare_amounts(ic4, sc4, bc4);
      ip1 = $('#id_quoteservice_paxvariants-' + idx + '-price_single_amount');
      sp1 = $('#' + idx + '-span-p1');
      bp1 = $('#' + idx + '-btn-p1');
      compare_amounts(ip1, sp1, bp1);
      ip2 = $('#id_quoteservice_paxvariants-' + idx + '-price_double_amount');
      sp2 = $('#' + idx + '-span-p2');
      bp2 = $('#' + idx + '-btn-p2');
      compare_amounts(ip2, sp2, bp2);
      ip3 = $('#id_quoteservice_paxvariants-' + idx + '-price_triple_amount');
      sp3 = $('#' + idx + '-span-p3');
      bp3 = $('#' + idx + '-btn-p3');
      compare_amounts(ip3, sp3, bp3);
      ip4 = $('#id_quoteservice_paxvariants-' + idx + '-price_qdrple_amount');
      sp4 = $('#' + idx + '-span-p4');
      bp4 = $('#' + idx + '-btn-p4');
      compare_amounts(ip4, sp4, bp4);
    }
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
    for (idx = 0; idx < 50; idx++) {
      $('#' + idx + '-btn-c1').detach();
      $('#' + idx + '-span-c1').detach();
      $('#' + idx + '-btn-c2').detach();
      $('#' + idx + '-span-c2').detach();
      $('#' + idx + '-btn-c3').detach();
      $('#' + idx + '-span-c3').detach();
      $('#' + idx + '-btn-c4').detach();
      $('#' + idx + '-span-c4').detach();
      $('#' + idx + '-btn-p1').detach();
      $('#' + idx + '-span-p1').detach();
      $('#' + idx + '-btn-p2').detach();
      $('#' + idx + '-span-p2').detach();
      $('#' + idx + '-btn-p3').detach();
      $('#' + idx + '-span-p3').detach();
      $('#' + idx + '-btn-p4').detach();
      $('#' + idx + '-span-p4').detach();
      field = $('#id_quoteservice_paxvariants-' + idx + '-cost_single_amount');
      if (field[0] != undefined) {
        $('#id_quoteservice_paxvariants-' + idx + '-cost_single_amount').after('<button id="' + idx + '-btn-c1" class="btn btn-copy-cost"><<</button><span id="' + idx + '-span-c1" class="computed-value">N/A</span>');
        $('#id_quoteservice_paxvariants-' + idx + '-cost_double_amount').after('<button id="' + idx + '-btn-c2" class="btn btn-copy-cost"><<</button><span id="' + idx + '-span-c2" class="computed-value">N/A</span>');
        $('#id_quoteservice_paxvariants-' + idx + '-cost_triple_amount').after('<button id="' + idx + '-btn-c3" class="btn btn-copy-cost"><<</button><span id="' + idx + '-span-c3" class="computed-value">N/A</span>');
        $('#id_quoteservice_paxvariants-' + idx + '-cost_qdrple_amount').after('<button id="' + idx + '-btn-c4" class="btn btn-copy-cost"><<</button><span id="' + idx + '-span-c4" class="computed-value">N/A</span>');
        $('#id_quoteservice_paxvariants-' + idx + '-price_single_amount').after('<button id="' + idx + '-btn-p1" class="btn btn-copy-price"><<</button><span id="' + idx + '-span-p1" class="computed-value">N/A</span>');
        $('#id_quoteservice_paxvariants-' + idx + '-price_double_amount').after('<button id="' + idx + '-btn-p2" class="btn btn-copy-price"><<</button><span id="' + idx + '-span-p2" class="computed-value">N/A</span>');
        $('#id_quoteservice_paxvariants-' + idx + '-price_triple_amount').after('<button id="' + idx + '-btn-p3" class="btn btn-copy-price"><<</button><span id="' + idx + '-span-p3" class="computed-value">N/A</span>');
        $('#id_quoteservice_paxvariants-' + idx + '-price_qdrple_amount').after('<button id="' + idx + '-btn-p4" class="btn btn-copy-price"><<</button><span id="' + idx + '-span-p4" class="computed-value">N/A</span>');
        changed_manual_costs($('#id_quoteservice_paxvariants-' + idx + '-manual_costs')[0]);
        changed_manual_prices($('#id_quoteservice_paxvariants-' + idx + '-manual_prices')[0]);
      } else {
        field = $('#quoteservice_paxvariants-' + idx + ' div.field-cost_single_amount div.field-cost_single_amount div.readonly');
        if (field[0] != undefined) {
          $('#quoteservice_paxvariants-' + idx + ' div.field-cost_single_amount div.field-cost_single_amount div.readonly').after('<span id="' + idx + '-span-c1" class="computed-value">N/A</span>');
          $('#quoteservice_paxvariants-' + idx + ' div.field-cost_double_amount div.field-cost_double_amount div.readonly').after('<span id="' + idx + '-span-c2" class="computed-value">N/A</span>');
          $('#quoteservice_paxvariants-' + idx + ' div.field-cost_triple_amount div.field-cost_triple_amount div.readonly').after('<span id="' + idx + '-span-c3" class="computed-value">N/A</span>');
          $('#quoteservice_paxvariants-' + idx + ' div.field-cost_qdrple_amount div.field-cost_qdrple_amount div.readonly').after('<span id="' + idx + '-span-c4" class="computed-value">N/A</span>');
          $('#quoteservice_paxvariants-' + idx + ' div.field-price_single_amount div.field-price_single_amount div.readonly').after('<span id="' + idx + '-span-p1" class="computed-value">N/A</span>');
          $('#quoteservice_paxvariants-' + idx + ' div.field-price_double_amount div.field-price_double_amount div.readonly').after('<span id="' + idx + '-span-p2" class="computed-value">N/A</span>');
          $('#quoteservice_paxvariants-' + idx + ' div.field-price_triple_amount div.field-price_triple_amount div.readonly').after('<span id="' + idx + '-span-p3" class="computed-value">N/A</span>');
          $('#quoteservice_paxvariants-' + idx + ' div.field-price_qdrple_amount div.field-price_qdrple_amount div.readonly').after('<span id="' + idx + '-span-p4" class="computed-value">N/A</span>');
        } else {
          break;
        }
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

  $(service_form_selector).submit(function () {
    $('select[name^="quoteservice_paxvariants-"][name$="-quote_pax_variant"]').attr('disabled', false);
  });

  $(service_form_selector).change(function (e) {
    e.preventDefault();
    get_computed_amounts();
  });
  // for dates changed by calendar
  $(service_form_selector + ' input[name*="date"]').focusout(function (e) {
    e.preventDefault();
    get_computed_amounts();
  });
  // for times changed by calendar
  $(service_form_selector + ' input[name*="time"]').focusout(function (e) {
    e.preventDefault();
    get_computed_amounts();
  });

  $('input[name^="quoteservice_paxvariants-"][name$="-manual_costs"][type="checkbox"]').on('change', function(e){
    e.preventDefault();
    changed_manual_costs(e.target);
  });

  $('input[name^="quoteservice_paxvariants-"][name$="-manual_prices"][type="checkbox"]').on('change', function(e){
    e.preventDefault();
    changed_manual_prices(e.target);
  });

  // for service changed
  $('#id_service').change(function (e) {
    e.preventDefault();
    // clear data
    $('#id_room_type option').prop("selected", false);
    $('#id_room_type').select();
    $('#id_board option').prop("selected", false);
    $('#id_board_type').select();

    $('#id_location_from').select();
    $('#id_location_to').select();

    $('#id_addon').select();

    get_computed_amounts();
  });

});
