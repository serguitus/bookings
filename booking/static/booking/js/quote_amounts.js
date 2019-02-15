//Entry Points to get prices for each booking_service
var quote_url = base_url + 'booking/quote-amounts/';

$(document).ready(function(){

  $("#quote_form").change(function () {
    get_computed_amounts();
  });

  function show_buttons() {
    for (idx = 0; idx < 50; idx++) {
      field = $('#id_quote_paxvariants-' + idx + '-cost_single_amount');
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
        
        $('#id_quote_paxvariants-' + idx + '-cost_single_amount').after('<button id="' + idx + '-btn-c1" class="btn btn-copy"><<</button><span id="' + idx + '-span-c1" class="computed-value">N/A</span>');
        $('#id_quote_paxvariants-' + idx + '-cost_double_amount').after('<button id="' + idx + '-btn-c2" class="btn btn-copy"><<</button><span id="' + idx + '-span-c2" class="computed-value">N/A</span>');
        $('#id_quote_paxvariants-' + idx + '-cost_triple_amount').after('<button id="' + idx + '-btn-c3" class="btn btn-copy"><<</button><span id="' + idx + '-span-c3" class="computed-value">N/A</span>');
        $('#id_quote_paxvariants-' + idx + '-price_single_amount').after('<button id="' + idx + '-btn-p1" class="btn btn-copy"><<</button><span id="' + idx + '-span-p1" class="computed-value">N/A</span>');
        $('#id_quote_paxvariants-' + idx + '-price_double_amount').after('<button id="' + idx + '-btn-p2" class="btn btn-copy"><<</button><span id="' + idx + '-span-p2" class="computed-value">N/A</span>');
        $('#id_quote_paxvariants-' + idx + '-price_triple_amount').after('<button id="' + idx + '-btn-p3" class="btn btn-copy"><<</button><span id="' + idx + '-span-p3" class="computed-value">N/A</span>');
      }
    }
    $('.btn-copy').on('click', function(e){
      e.preventDefault();
      button = $(this); 
      input = button.prev();
      span = button.next();
      number = Number(span.html());
      if (number) {
        input.val(number);
        compare_amounts(input, span, button);
      }
      return false;
    })
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
      ic1 = $('#id_quote_paxvariants-' + idx + '-cost_single_amount');
      sc1 = $('#' + idx + '-span-c1');
      bc1 = $('#' + idx + '-btn-c1');
      compare_amounts(ic1, sc1, bc1);
      ic2 = $('#id_quote_paxvariants-' + idx + '-cost_double_amount');
      sc2 = $('#' + idx + '-span-c2');
      bc2 = $('#' + idx + '-btn-c2');
      compare_amounts(ic2, sc2, bc2);
      ic3 = $('#id_quote_paxvariants-' + idx + '-cost_triple_amount');
      sc3 = $('#' + idx + '-span-c3');
      bc3 = $('#' + idx + '-btn-c3');
      compare_amounts(ic3, sc3, bc3);
      ip1 = $('#id_quote_paxvariants-' + idx + '-price_single_amount');
      sp1 = $('#' + idx + '-span-p1');
      bp1 = $('#' + idx + '-btn-p1');
      compare_amounts(ip1, sp1, bp1);
      ip2 = $('#id_quote_paxvariants-' + idx + '-price_double_amount');
      sp2 = $('#' + idx + '-span-p2');
      bp2 = $('#' + idx + '-btn-p2');
      compare_amounts(ip2, sp2, bp2);
      ip3 = $('#id_quote_paxvariants-' + idx + '-price_triple_amount');
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

  function get_computed_amounts() {
    show_buttons();
    if($('#quote_form').length){
      data = $('#quote_form').serialize();
    }
    $.ajax({
      'url': quote_url,
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
              ic1 = $('#id_quote_paxvariants-' + idx + '-cost_single_amount');
              sc1 = $('#' + idx + '-span-c1');
              if (pax_data.total.cost_1) {
                sc1.html(pax_data.total.cost_1);
              } else {
                sc1.html(pax_data.total.cost_1_msg);
              }

              ic2 = $('#id_quote_paxvariants-' + idx + '-cost_double_amount');
              sc2 = $('#' + idx + '-span-c2');
              if (pax_data.total.cost_2) {
                sc2.html(pax_data.total.cost_2);
              } else {
                sc2.html(pax_data.total.cost_2_msg);
              }

              ic3 = $('#id_quote_paxvariants-' + idx + '-cost_triple_amount');
              sc3 = $('#' + idx + '-span-c3');
              if (pax_data.total.cost_3) {
                sc3.html(pax_data.total.cost_3);
              } else {
                sc3.html(pax_data.total.cost_3_msg);
              }

              ip1 = $('#id_quote_paxvariants-' + idx + '-price_single_amount');
              sp1 = $('#' + idx + '-span-p1');
              if (pax_data.total.price_1) {
                sp1.html(pax_data.total.price_1);
              } else {
                sp1.html(pax_data.total.price_1_msg);
              }

              ip2 = $('#id_quote_paxvariants-' + idx + '-price_double_amount');
              sp2 = $('#' + idx + '-span-p2');
              if (pax_data.total.price_2) {
                sp2.html(pax_data.total.price_2);
              } else {
                sp2.html(pax_data.total.price_2_msg);
              }

              ip3 = $('#id_quote_paxvariants-' + idx + '-price_triple_amount');
              sp3 = $('#' + idx + '-span-p3');
              if (pax_data.total.price_3) {
                sp3.html(pax_data.total.price_3);
              } else {
                sp3.html(pax_data.total.price_3_msg);
              }
            }
          }
          fill_subtotal(paxes, pax_data);
        });
        compare_all_amounts();  
      }else{
        clear_values(data['message']);
      }
    }).fail(function(){
      clear_values();
    })
  }

  function fill_subtotal(pax_variant, data){
    // This fills all service subtotal for specified pax_variant
    for(var service in data){
      if(service != 'total' && service != 'paxes'){
        // just iterate over subtotals
        $('.subtotal-quote_services-'+ service + '-pax-' + data.paxes).remove();
        $('.subtotal-quote_services-'+ service).append(
          sub_total_line(service, data.paxes, data[service].cost_1,
                         data[service].cost_2, data[service].cost_3,
                         data[service].price_1, data[service].price_2,
                         data[service].price_3));
        //console.log(data[service].cost_1);
      }
    }
  }

  get_computed_amounts();

});

function sub_total_line(id, pax, sc, dc, tc, sp, dp, tp){
  // this is the line that prints each sub-total line
  return "<div class='subtotal-quote_services-" + id + "-pax-" + pax +
    "'><span class='subprice-pax-limit'>pax Limit: " + pax +
    "</span><span class='sub-costs'><span class='sub_cost_1'> SGL:" + sc +
    "</span><span class='sub_cost_2'> DBL:" + dc +
    "</span><span class='sub_cost_3'> TPL:" + tc +
    "</span></span><span class='sub-prices'><span class='sub_price_1'>  SGL" + sp +
    "</span><span class='sub_price_2'> DBL:" + dp +
    "</span><span class='sub_price_3'> TPL:" + tp +
    "</span></span></div>"
}
