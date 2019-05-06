var quote_amounts_url = base_url + 'booking/quote-amounts/';
var quote_form_selector = '#quote_form';

$(document).ready(function(){

  function get_computed_amounts() {
    if($(quote_form_selector).length){
      data = $(quote_form_selector).serialize();
    }
    $.ajax({
      'url': quote_amounts_url,
      'async': true,
      'datatype': 'json',
      'type': 'POST',
      'data': data,
    }).done(function(data){
      if(data['code'] == 0){
        values = data['results'];
        values.forEach(pax_data => {
          paxes = pax_data.paxes;
          // find variant index
          for (idx = 0; idx < 50; idx++) {
            qtty_input = $('#id_quote_paxvariants-' + idx + '-pax_quantity');
            qtty = Number(qtty_input.val());
            if (qtty && qtty == paxes) {
              update_cost_amounts(idx, 1, pax_data.total.cost_1, pax_data.total.cost_1_msg);
              update_cost_amounts(idx, 2, pax_data.total.cost_2, pax_data.total.cost_2_msg);
              update_cost_amounts(idx, 3, pax_data.total.cost_3, pax_data.total.cost_3_msg);
  
              ipp = $('#id_quote_paxvariants-' + idx + '-price_percent');
              if (ipp.val() != '' && !isNaN(ipp.val())) {
                var percent = Number(ipp.val());
                update_price_amounts(percent, idx, 1, pax_data.total.price_1, pax_data.total.price_1_msg);
                update_price_amounts(percent, idx, 2, pax_data.total.price_2, pax_data.total.price_2_msg);
                update_price_amounts(percent, idx, 3, pax_data.total.price_3, pax_data.total.price_3_msg);
              } else {
                update_price_amounts(false, idx, 1, pax_data.total.price_1, pax_data.total.price_1_msg);
                update_price_amounts(false, idx, 2, pax_data.total.price_2, pax_data.total.price_2_msg);
                update_price_amounts(false, idx, 3, pax_data.total.price_3, pax_data.total.price_3_msg);
              }
            }
          }
        });
        compare_all_amounts();  
      }else{
        clear_values(data['message']);
      }
    }).fail(function(){
      clear_values();
    })
  }

  function update_cost_amounts(idx, amount_idx, data_amount, data_amount_msg){
    sc = $('#' + idx + '-span-c' + amount_idx);
    if (amount_idx == 1) {
      ic = $('#quote_paxvariants-' + idx + ' div.field-cost_single_amount div.field-cost_single_amount div.readonly');
    } else if (amount_idx == 2) {
      ic = $('#quote_paxvariants-' + idx + ' div.field-cost_double_amount div.field-cost_double_amount div.readonly');
    } else {
      ic = $('#quote_paxvariants-' + idx + ' div.field-cost_triple_amount div.field-cost_triple_amount div.readonly');
    }
    if (data_amount) {
      sc.html(data_amount);
      ic.html(Number(data_amount));
    } else {
      sc.html(data_amount_msg);
      ic.html('');
    }
  }

  function update_price_amounts(percent, idx, amount_idx, data_amount, data_amount_msg){
    sp = $('#' + idx + '-span-p' + amount_idx);
    if (amount_idx == 1) {
      ip = $('#quote_paxvariants-' + idx + ' div.field-price_single_amount div.field-price_single_amount div.readonly');
    } else if (amount_idx == 2) {
      ip = $('#quote_paxvariants-' + idx + ' div.field-price_double_amount div.field-price_double_amount div.readonly');
    } else {
      ip = $('#quote_paxvariants-' + idx + ' div.field-price_triple_amount div.field-price_triple_amount div.readonly');
    }
    if (!percent) {
      if (data_amount) {
        sp.html(data_amount);
        ip.html(Number(data_amount));
      } else {
        sp.html(data_amount_msg);
        ip.html('');
      }
    } else {
      if (amount_idx == 1) {
        ic = $('#quote_paxvariants-' + idx + ' div.field-cost_single_amount div.field-cost_single_amount div.readonly');
      } else if (amount_idx == 2) {
        ic = $('#quote_paxvariants-' + idx + ' div.field-cost_double_amount div.field-cost_double_amount div.readonly');
      } else {
        ic = $('#quote_paxvariants-' + idx + ' div.field-cost_triple_amount div.field-cost_triple_amount div.readonly');
      }
      if (isNaN(ic.val())) {
        sp.html('Cost for % is empty');
      } else {
        price = Math.round(0.499999 + Number(ic.val()) * (1.0 + percent / 100.0));
        sp.html(price);
        if (ip.val() == '') {
          ip.val(price);
        }
      }
    }
  }

  function clear_values(msg) {
    $('span.computed-value').each(function(index) {
      $( this ).html(msg);
    });
  }

  function show_buttons() {
    for (idx = 0; idx < 50; idx++) {
      field = $('#id_quote_paxvariants-' + idx + '-cost_single_amount');
      if (field[0] != undefined) {
        $('#' + idx + '-span-c1').detach();
        $('#' + idx + '-span-c2').detach();
        $('#' + idx + '-span-c3').detach();
        $('#' + idx + '-span-p1').detach();
        $('#' + idx + '-span-p2').detach();
        $('#' + idx + '-span-p3').detach();
        
        $('#id_quote_paxvariants-' + idx + '-cost_single_amount').after('<span id="' + idx + '-span-c1" class="computed-value">N/A</span>');
        $('#id_quote_paxvariants-' + idx + '-cost_double_amount').after('<span id="' + idx + '-span-c2" class="computed-value">N/A</span>');
        $('#id_quote_paxvariants-' + idx + '-cost_triple_amount').after('<span id="' + idx + '-span-c3" class="computed-value">N/A</span>');
        $('#id_quote_paxvariants-' + idx + '-price_single_amount').after('<span id="' + idx + '-span-p1" class="computed-value">N/A</span>');
        $('#id_quote_paxvariants-' + idx + '-price_double_amount').after('<span id="' + idx + '-span-p2" class="computed-value">N/A</span>');
        $('#id_quote_paxvariants-' + idx + '-price_triple_amount').after('<span id="' + idx + '-span-p3" class="computed-value">N/A</span>');
      } else {
        break;
      }
    }
  }

  show_buttons();
  get_computed_amounts();

  $(quote_form_selector).change(function () {
    get_computed_amounts();
  });

});
