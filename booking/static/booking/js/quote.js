var add_service_url = base_url + 'booking/quote_add_service/';
var quote_amounts_url = base_url + 'booking/quote-amounts/';
var quote_form_selector = '#quote_form';

$(document).ready(function(){

  function get_computed_amounts() {
    show_buttons();
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

  function clear_values(msg) {
    $('span.computed-value').each(function(index) {
      $( this ).html(msg);
    });
  }

  function show_buttons() {
    for (idx = 0; idx < 50; idx++) {
      field = $('#quote_paxvariants-' + idx + ' div.field-cost_single_amount div.field-cost_single_amount div.readonly');
      if (field[0] != undefined) {
        $('#' + idx + '-span-c1').detach();
        $('#' + idx + '-span-c2').detach();
        $('#' + idx + '-span-c3').detach();
        $('#' + idx + '-span-c4').detach();
        $('#' + idx + '-span-p1').detach();
        $('#' + idx + '-span-p2').detach();
        $('#' + idx + '-span-p3').detach();
        $('#' + idx + '-span-p4').detach();

        $('#quote_paxvariants-' + idx + ' div.field-cost_single_amount div.field-cost_single_amount div.readonly').after('<span id="' + idx + '-span-c1" class="computed-value">N/A</span>');
        $('#quote_paxvariants-' + idx + ' div.field-cost_double_amount div.field-cost_double_amount div.readonly').after('<span id="' + idx + '-span-c2" class="computed-value">N/A</span>');
        $('#quote_paxvariants-' + idx + ' div.field-cost_triple_amount div.field-cost_triple_amount div.readonly').after('<span id="' + idx + '-span-c3" class="computed-value">N/A</span>');
        $('#quote_paxvariants-' + idx + ' div.field-cost_qdrple_amount div.field-cost_qdrple_amount div.readonly').after('<span id="' + idx + '-span-c4" class="computed-value">N/A</span>');
        $('#quote_paxvariants-' + idx + ' div.field-price_single_amount div.field-price_single_amount div.readonly').after('<span id="' + idx + '-span-p1" class="computed-value">N/A</span>');
        $('#quote_paxvariants-' + idx + ' div.field-price_double_amount div.field-price_double_amount div.readonly').after('<span id="' + idx + '-span-p2" class="computed-value">N/A</span>');
        $('#quote_paxvariants-' + idx + ' div.field-price_triple_amount div.field-price_triple_amount div.readonly').after('<span id="' + idx + '-span-p3" class="computed-value">N/A</span>');
        $('#quote_paxvariants-' + idx + ' div.field-price_qdrple_amount div.field-price_qdrple_amount div.readonly').after('<span id="' + idx + '-span-p4" class="computed-value">N/A</span>');
      } else {
        break;
      }
    }
  }

  get_computed_amounts();

  $(quote_form_selector).change(function () {
    get_computed_amounts();
  });

  // check if there is description on the quote to Expand collapsed description
  if ($('#id_description').val()) {
    document.getElementById('fieldsetcollapser0').dispatchEvent(clickEvent);
    $('#fieldsetcollapser0.collapse-toggle').click()
  }
});
