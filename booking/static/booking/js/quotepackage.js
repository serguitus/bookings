var quoteservice_amounts_url = base_url + 'booking/quotepackage-amounts/';
var quoteservice_form_selector = '#quotepackage_form';

$(document).ready(function(){

  $('select[name^="quoteservice_paxvariants-"][name$="-quote_pax_variant"]').attr('disabled', true);
  
  function get_computed_amounts() {
    if($(quoteservice_form_selector).length){
      $('select[name^="quoteservice_paxvariants-"][name$="-quote_pax_variant"]').attr('disabled', false);
      data = $(quoteservice_form_selector).serialize();
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
  
              update_amounts(true, idx, 1, pax_data.total.price_1, pax_data.total.price_1_msg);
              update_amounts(true, idx, 2, pax_data.total.price_2, pax_data.total.price_2_msg);
              update_amounts(true, idx, 3, pax_data.total.price_3, pax_data.total.price_3_msg);
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
    if (amount_idx == 1) {
      ia = $('#quoteservice_paxvariants-' + idx + ' div.field-' + amount_text + '_single_amount div.field-' + amount_text + '_single_amount div.readonly');
    } else if (amount_idx == 2) {
      ia = $('#quoteservice_paxvariants-' + idx + ' div.field-' + amount_text + '_double_amount div.field-' + amount_text + '_double_amount div.readonly');
    } else {
      ia = $('#quoteservice_paxvariants-' + idx + ' div.field-' + amount_text + '_triple_amount div.field-' + amount_text + '_triple_amount div.readonly');
    }
    if (data_amount) {
      sa.html(data_amount);
      ia.html(Number(data_amount));
    } else {
      sa.html(data_amount_msg);
      ia.html('');
    }
  }

  function clear_values(msg) {
    $('span.computed-value').each(function(index) {
      $( this ).html(msg);
    });
  }

  function show_buttons() {
    for (idx = 0; idx < 50; idx++) {
      field = $('#id_quoteservice_paxvariants-' + idx + '-cost_single_amount');
      if (field[0] != undefined) {
        $('#' + idx + '-span-c1').detach();
        $('#' + idx + '-span-c2').detach();
        $('#' + idx + '-span-c3').detach();
        $('#' + idx + '-span-p1').detach();
        $('#' + idx + '-span-p2').detach();
        $('#' + idx + '-span-p3').detach();
        
        $('#id_quoteservice_paxvariants-' + idx + '-cost_single_amount').after('<span id="' + idx + '-span-c1" class="computed-value">N/A</span>');
        $('#id_quoteservice_paxvariants-' + idx + '-cost_double_amount').after('<span id="' + idx + '-span-c2" class="computed-value">N/A</span>');
        $('#id_quoteservice_paxvariants-' + idx + '-cost_triple_amount').after('<span id="' + idx + '-span-c3" class="computed-value">N/A</span>');
        $('#id_quoteservice_paxvariants-' + idx + '-price_single_amount').after('<span id="' + idx + '-span-p1" class="computed-value">N/A</span>');
        $('#id_quoteservice_paxvariants-' + idx + '-price_double_amount').after('<span id="' + idx + '-span-p2" class="computed-value">N/A</span>');
        $('#id_quoteservice_paxvariants-' + idx + '-price_triple_amount').after('<span id="' + idx + '-span-p3" class="computed-value">N/A</span>');
      } else {
        break;
      }
    }
  }

  show_buttons();
  get_computed_amounts();

  $(quoteservice_form_selector).submit(function () {
    $('select[name^="quoteservice_paxvariants-"][name$="-quote_pax_variant"]').attr('disabled', false);
  });

  $(quoteservice_form_selector).change(function () {
    get_computed_amounts();
  });

});
  