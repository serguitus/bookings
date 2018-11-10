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
    get_computed_amounts(quote_url);
  });

  $('.btn-copy').on('click', function(e){
    e.preventDefault();

    // find left control and right control
    //amount = input.val();
    //calculated = calculated_element.html();
    //if(Number(calculated)){
    //  amount_input.value = Number(calculated);
    //}
    //compare_amounts(amount_input.value, claculated, this);

    return false;
  })

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
        
        $('#id_quote_paxvariants-' + idx + '-cost_single_amount').after("<button id='" + idx + "-cost-sgl' class='btn btn-success btn-copy'><<</button>");
        $('#id_quote_paxvariants-' + idx + '-cost_double_amount').after("<button id='" + idx + "-cost-dbl' class='btn btn-success btn-copy'><<</button>");
        $('#id_quote_paxvariants-' + idx + '-cost_triple_amount').after("<button id='" + idx + "-cost-tpl' class='btn btn-success btn-copy'><<</button>");
        $('#id_quote_paxvariants-' + idx + '-price_single_amount').after("<button id='" + idx + "-price-sgl' class='btn btn-success btn-copy'><<</button>");
        $('#id_quote_paxvariants-' + idx + '-price_double_amount').after("<button id='" + idx + "-price-dbl' class='btn btn-success btn-copy'><<</button>");
        $('#id_quote_paxvariants-' + idx + '-price_triple_amount').after("<button id='" + idx + "-price-tpl' class='btn btn-success btn-copy'><<</button>");
      }
    }
  }

  function compare_amounts(amount, calculated, btn) {
    if(input.value != Number(div.html())){
      btn.removeClass('btn-success');
      btn.addClass('btn-danger');
    } else{
      btn.removeClass('btn-danger');
      btn.addClass('btn-success');
    }
  }

  function get_computed_amounts(url) {
    show_buttons();
    if($('#quote_form').length){
      data = $('#quote_form').serialize();
    }
    $.ajax({
      'url': url,
      'async': true,
      'datatype': 'json',
      'type': 'POST',
      'data': data,
    }).done(function(data){

      if(data['cost']){
        computedCost.html(data['cost']);
      }
      else{
        computedCost.html('N/A');
      }
      if(data['price']){
        computedPrice.html(data['price']);
      }
      else{
        computedPrice.html('N/A');
      }
      compare_numbers();
    }).fail(function(){
      $('.btn-copy').each(function(index) {
        $( this ).removeClass('btn-success');
        $( this ).addClass('btn-danger');
      });
    })
  }

  get_computed_amounts(quote_url);

});
