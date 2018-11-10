//Entry Points to get prices for each booking_service
var quote_url = base_url + 'booking/quote-amounts/';

$(document).ready(function(){
  $('div.field-box.field-calc_c_s').each(function(index) {
    $( this ).children()[0].style = 'display: none;';
  });
  $('div.field-box.field-calc_c_d').each(function(index) {
    $( this ).children()[0].style = 'display: none;';
  });
  $('div.field-box.field-calc_c_t').each(function(index) {
    $( this ).children()[0].style = 'display: none;';
  });
  $('div.field-box.field-calc_p_s').each(function(index) {
    $( this ).children()[0].style = 'display: none;';
  });
  $('div.field-box.field-calc_p_d').each(function(index) {
    $( this ).children()[0].style = 'display: none;';
  });
  $('div.field-box.field-calc_p_t').each(function(index) {
    $( this ).children()[0].style = 'display: none;';
  });

  $('div.field-box.field-calc_c_s').each(function(index) {
    $( this ).children()[1].style = 'width: 170px; margin-left: 0px; margin-right:30px;';
  });
  $('div.field-box.field-calc_c_d').each(function(index) {
    $( this ).children()[1].style = 'width: 170px; margin-left: 0px; margin-right:30px;';
  });
  $('div.field-box.field-calc_c_t').each(function(index) {
    $( this ).children()[1].style = 'width: 170px; margin-left: 0px; margin-right:30px;';
  });
  $('div.field-box.field-calc_p_s').each(function(index) {
    $( this ).children()[1].style = 'width: 170px; margin-left: 0px; margin-right:30px;';
  });
  $('div.field-box.field-calc_p_d').each(function(index) {
    $( this ).children()[1].style = 'width: 170px; margin-left: 0px; margin-right:30px;';
  });
  $('div.field-box.field-calc_p_t').each(function(index) {
    $( this ).children()[1].style = 'width: 170px; margin-left: 0px; margin-right:30px;';
  });

  $("#quote_form").change(function () {
    get_computed_amounts();
  });

  function show_buttons() {
    for (idx = 0; idx < 50; idx++) {
      field = $('#id_quote_paxvariants-' + idx + '-cost_single_amount');
      if (field != undefined) {
        $('#' + idx + '-cost-sgl').detach();
        $('#' + idx + '-cost-dbl').detach();
        $('#' + idx + '-cost-tpl').detach();
        $('#' + idx + '-price-sgl').detach();
        $('#' + idx + '-price-dbl').detach();
        $('#' + idx + '-price-tpl').detach();
        
        $('#id_quote_paxvariants-' + idx + '-cost_single_amount').after("<button id='" + idx + "-cost-sgl' class='btn btn-copy'><<</button>");
        $('#id_quote_paxvariants-' + idx + '-cost_double_amount').after("<button id='" + idx + "-cost-dbl' class='btn btn-copy'><<</button>");
        $('#id_quote_paxvariants-' + idx + '-cost_triple_amount').after("<button id='" + idx + "-cost-tpl' class='btn btn-copy'><<</button>");
        $('#id_quote_paxvariants-' + idx + '-price_single_amount').after("<button id='" + idx + "-price-sgl' class='btn btn-copy'><<</button>");
        $('#id_quote_paxvariants-' + idx + '-price_double_amount').after("<button id='" + idx + "-price-dbl' class='btn btn-copy'><<</button>");
        $('#id_quote_paxvariants-' + idx + '-price_triple_amount').after("<button id='" + idx + "-price-tpl' class='btn btn-copy'><<</button>");
      }
    }
    $('.btn-copy').on('click', function(e){
      e.preventDefault();
      button = $(this); 
      input = button.prev();
      div = input.parent().next().children().last();
      number = Number(div.html());
      if (number) {
        input.val(number);
        compare_amounts(input, div, button);
      }
      return false;
    })
  }
  function clear_values(msg) {
    $('div.field-box.field-calc_c_s').each(function(index) {
      $( this ).children().last().html(msg);
    });
    $('div.field-box.field-calc_c_d').each(function(index) {
      $($( this ).children()[1]).html(msg);
    });
    $('div.field-box.field-calc_c_t').each(function(index) {
      $($( this ).children()[1]).html(msg);
    });
    $('div.field-box.field-calc_p_s').each(function(index) {
      $($( this ).children()[1]).html(msg);
    });
    $('div.field-box.field-calc_p_d').each(function(index) {
      $($( this ).children()[1]).html(msg);
    });
    $('div.field-box.field-calc_p_t').each(function(index) {
      $($( this ).children()[1]).html(msg);
    });
    $('.btn-copy').each(function(index) {
      $( this ).removeClass('btn-success');
      $( this ).addClass('btn-danger');
    });
  }
  function compare_all_amounts() {
    for (idx = 0; idx < 50; idx++) {
      ic1 = $('#id_quote_paxvariants-' + idx + '-cost_single_amount');
      dc1 = ic1.parent().next().children().last();
      bc1 = $('#' + idx + '-cost-sgl');
      compare_amounts(ic1, dc1, bc1);
      ic2 = $('#id_quote_paxvariants-' + idx + '-cost_single_amount');
      dc2 = ic2.parent().next().children().last();
      bc2 = $('#' + idx + '-cost-dbl');
      compare_amounts(ic2, dc2, bc2);
      ic3 = $('#id_quote_paxvariants-' + idx + '-cost_single_amount');
      dc3 = ic3.parent().next().children().last();
      bc3 = $('#' + idx + '-cost-tpl');
      compare_amounts(ic3, dc3, bc3);
      ip1 = $('#id_quote_paxvariants-' + idx + '-cost_single_amount');
      dp1 = ip1.parent().next().children().last();
      bp1 = $('#' + idx + '-price-sgl');
      compare_amounts(ip1, dp1, bp1);
      ip2 = $('#id_quote_paxvariants-' + idx + '-cost_single_amount');
      dp2 = ip2.parent().next().children().last();
      bp2 = $('#' + idx + '-price-dbl');
      compare_amounts(ip2, dp2, bp2);
      ip3 = $('#id_quote_paxvariants-' + idx + '-cost_single_amount');
      dp3 = ip3.parent().next().children().last();
      bp3 = $('#' + idx + '-price-tpl');
      compare_amounts(ip3, dp3, bp3);
    }
  }
  function compare_amounts(input, div, btn) {
    if(input.val() != Number(div.html())){
      btn.removeClass('btn-success');
      btn.addClass('btn-danger');
    } else{
      btn.removeClass('btn-danger');
      btn.addClass('btn-success');
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
              dc1 = ic1.parent().next().children().last();
              if (pax_data.cost_1) {
                dc1.html(pax_data.cost_1);
              } else {
                dc1.html(pax_data.cost_1_msg);
              }

              ic2 = $('#id_quote_paxvariants-' + idx + '-cost_double_amount');
              dc2 = ic2.parent().next().children().last();
              if (pax_data.cost_2) {
                dc2.html(pax_data.cost_2);
              } else {
                dc2.html(pax_data.cost_2_msg);
              }

              ic3 = $('#id_quote_paxvariants-' + idx + '-cost_triple_amount');
              dc3 = ic3.parent().next().children().last();
              if (pax_data.cost_3) {
                dc3.html(pax_data.cost_3);
              } else {
                dc3.html(pax_data.cost_3_msg);
              }

              ip1 = $('#id_quote_paxvariants-' + idx + '-price_single_amount');
              dp1 = ip1.parent().next().children().last();
              if (pax_data.price_1) {
                dp1.html(pax_data.price_1);
              } else {
                dp1.html(pax_data.price_1_msg);
              }

              ip2 = $('#id_quote_paxvariants-' + idx + '-price_double_amount');
              dp2 = ip2.parent().next().children().last();
              if (pax_data.price_2) {
                dp2.html(pax_data.price_2);
              } else {
                dp2.html(pax_data.price_2_msg);
              }

              ip3 = $('#id_quote_paxvariants-' + idx + '-price_triple_amount');
              dp3 = ip3.parent().next().children().last();
              if (pax_data.price_3) {
                dp3.html(pax_data.price_3);
              } else {
                dp3.html(pax_data.price_3_msg);
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

  get_computed_amounts();

});
