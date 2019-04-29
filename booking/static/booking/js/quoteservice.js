$(document).ready(function(){

  function get_computed_amounts() {
    show_buttons();
    if($(quoteservice_form_selector).length){
      data = $(quoteservice_form_selector).serialize();
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
              ic1 = $('#id_quoteservice_paxvariants-' + idx + '-cost_single_amount');
              sc1 = $('#' + idx + '-span-c1');
              if (pax_data.total.cost_1) {
                sc1.html(pax_data.total.cost_1);
              } else {
                sc1.html(pax_data.total.cost_1_msg);
              }

              ic2 = $('#id_quoteservice_paxvariants-' + idx + '-cost_double_amount');
              sc2 = $('#' + idx + '-span-c2');
              if (pax_data.total.cost_2) {
                sc2.html(pax_data.total.cost_2);
              } else {
                sc2.html(pax_data.total.cost_2_msg);
              }

              ic3 = $('#id_quoteservice_paxvariants-' + idx + '-cost_triple_amount');
              sc3 = $('#' + idx + '-span-c3');
              if (pax_data.total.cost_3) {
                sc3.html(pax_data.total.cost_3);
              } else {
                sc3.html(pax_data.total.cost_3_msg);
              }

              ipp = $('#id_quoteservice_paxvariants-' + idx + '-price_percent');
              if (ipp.val() != '' && !isNaN(ipp.val())) {
                var percent = Number(ipp.val());
                ip1 = $('#id_quoteservice_paxvariants-' + idx + '-price_single_amount');
                sp1 = $('#' + idx + '-span-p1');
                if (isNaN(ic1.val())) {
                  sp1.html('Cost for % is empty');
                } else {
                  price = Math.round(0.499999 + Number(ic1.val()) * (1.0 + percent / 100.0));
                  sp1.html(price);
                  if (ip1.val() == '') {
                    ip1.val(price);
                  }
                }
                ip2 = $('#id_quoteservice_paxvariants-' + idx + '-price_double_amount');
                sp2 = $('#' + idx + '-span-p2');
                if (isNaN(ic2.val())) {
                  sp2.html('Cost for % is empty');
                } else {
                  price = Math.round(0.499999 + Number(ic2.val()) * (1.0 + percent / 100.0));
                  sp2.html(price);
                  if (ip2.val() == '') {
                    ip2.val(price);
                  }
                }
                ip3 = $('#id_quoteservice_paxvariants-' + idx + '-price_triple_amount');
                sp3 = $('#' + idx + '-span-p3');
                if (isNaN(ic3.val())) {
                  sp3.html('Cost for % is empty');
                } else {
                  price = Math.round(0.499999 + Number(ic3.val()) * (1.0 + percent / 100.0));
                  sp3.html(price);
                  if (ip3.val() == '') {
                    ip3.val(price);
                  }
                }
              } else {
                ip1 = $('#id_quoteservice_paxvariants-' + idx + '-price_single_amount');
                sp1 = $('#' + idx + '-span-p1');
                if (pax_data.total.price_1) {
                  sp1.html(pax_data.total.price_1);
                } else {
                  sp1.html(pax_data.total.price_1_msg);
                }
  
                ip2 = $('#id_quoteservice_paxvariants-' + idx + '-price_double_amount');
                sp2 = $('#' + idx + '-span-p2');
                if (pax_data.total.price_2) {
                  sp2.html(pax_data.total.price_2);
                } else {
                  sp2.html(pax_data.total.price_2_msg);
                }
  
                ip3 = $('#id_quoteservice_paxvariants-' + idx + '-price_triple_amount');
                sp3 = $('#' + idx + '-span-p3');
                if (pax_data.total.price_3) {
                  sp3.html(pax_data.total.price_3);
                } else {
                  sp3.html(pax_data.total.price_3_msg);
                }
  
              }
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

  get_computed_amounts();

  $(quoteservice_form_selector).change(function () {
    get_computed_amounts();
  });

  function changed_manual_cost(checkbox, target){
    isManualCost = target,checked;
    if(isManualCost){
      checkbox.  $('.btn-copy-cost').show()
    } else {
      $('.btn-copy-cost').hide()
    }
    if (readonlyCost.length == 0) {
      costInput[0].readOnly = !manual;
    }
    get_computed_amounts();
  }

  $('input[name^="quoteservice_paxvariants-"][name*="-manual_cost_"][type="checkbox"]').on('change', function(e){
    e.preventDefault();
    changed_manual_cost($(this), e.target);
  })

  function changed_manual_price(checkbox, target){
    isManualPrice = target.checked;
    if(isManualPrice){
      button = 
      $('.btn-copy-price').show()
    } else {
      $('.btn-copy-price').hide()
    }
    if (readonlyPrice.length == 0) {
      priceInput[0].readOnly = !manual;
    }
    get_computed_amounts();
  }

  $('input[name^="quoteservice_paxvariants-"][name*="-manual_price_"][type="checkbox"]').on('change', function(e){
    e.preventDefault();
    changed_manual_price($(this), e.target);
  })

  $('.btn-copy').on('click', function(e){
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
  })

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
      field = $('#id_quoteservice_paxvariants-' + idx + '-cost_single_amount');
      if (field != undefined) {
        $('#' + idx + '-btn-c1').detach();
        $('#' + idx + '-span-c1').detach();
        $('#' + idx + '-btn-c2').detach();
        $('#' + idx + '-span-c2').detach();
        $('#' + idx + '-btn-c3').detach();
        $('#' + idx + '-span-c3').detach();
        $('#' + idx + '-btn-p1').detach();
        $('#' + idx + '-span-p1').detach();
        $('#' + idx + '-btn-p2').detach();
        $('#' + idx + '-span-p2').detach();
        $('#' + idx + '-btn-p3').detach();
        $('#' + idx + '-span-p3').detach();
        
        $('#id_quoteservice_paxvariants-' + idx + '-cost_single_amount').after('<button id="' + idx + '-btn-c1" class="btn btn-copy"><<</button><span id="' + idx + '-span-c1" class="computed-value">N/A</span>');
        $('#id_quoteservice_paxvariants-' + idx + '-cost_double_amount').after('<button id="' + idx + '-btn-c2" class="btn btn-copy"><<</button><span id="' + idx + '-span-c2" class="computed-value">N/A</span>');
        $('#id_quoteservice_paxvariants-' + idx + '-cost_triple_amount').after('<button id="' + idx + '-btn-c3" class="btn btn-copy"><<</button><span id="' + idx + '-span-c3" class="computed-value">N/A</span>');
        $('#id_quoteservice_paxvariants-' + idx + '-price_single_amount').after('<button id="' + idx + '-btn-p1" class="btn btn-copy"><<</button><span id="' + idx + '-span-p1" class="computed-value">N/A</span>');
        $('#id_quoteservice_paxvariants-' + idx + '-price_double_amount').after('<button id="' + idx + '-btn-p2" class="btn btn-copy"><<</button><span id="' + idx + '-span-p2" class="computed-value">N/A</span>');
        $('#id_quoteservice_paxvariants-' + idx + '-price_triple_amount').after('<button id="' + idx + '-btn-p3" class="btn btn-copy"><<</button><span id="' + idx + '-span-p3" class="computed-value">N/A</span>');
      } else {
        break;
      }
    }
  }

});
