$(document).ready(function(){

  function get_computed_amounts(){
    // sending a request to get computed numbers
    $.ajax({
      'url': base_url + 'booking/booking-amounts/',
      'async': true,
      'datatype': 'json',
      'type': 'POST',
      'data': $('#booking_form').serialize(),
    }).done(function(data){
      update_amounts(false, data['cost'], data['cost_message']);
      update_amounts(true, data['price'], data['price_message']);
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

  function clear_values(msg) {
    $('span.computed-value').each(function(index) {
      $( this ).html(msg);
    });
    $('button.btn-copy').each(function(index) {
      $( this ).removeClass('btn-success');
      $( this ).addClass('btn-danger');
    });
  }

  function show_calculated_amounts() {
    $('div.field-cost_amount div.field-cost_amount div.readonly').after('<span id="span-cost" class="computed-value">N/A</span>');
    $('div.field-price_amount div.field-price_amount div.readonly').after('<span id="span-price" class="computed-value">N/A</span>');
  }

  show_calculated_amounts();
  get_computed_amounts();

  $('#booking_form input, #booking_form select').on('change', function(){
    get_computed_amounts();
  });

  function show_package_amounts() {
    if ($('#id_is_package_price')[0].checked) {
      $('.form-row.field-package_sgl_price_amount')[0].hidden = false;
      $('.form-row.field-package_tpl_price_amount')[0].hidden = false;
    } else {
      $('.form-row.field-package_sgl_price_amount')[0].hidden = true;
      $('.form-row.field-package_tpl_price_amount')[0].hidden = true;
    }
  }

  $('.field-is_package_price').on('click', function(e) {
    show_package_amounts();
  })

  show_package_amounts();

  // check if there are general notes on the booking to Expand collapsed notes
  if($('#id_p_notes').val()){
    $('#fieldsetcollapser0.collapse-toggle').click()
  }

  // for agency changed
  $('#id_agency').change(function (e) {
    e.preventDefault();
    // clear data
    $('#id_agency_contact').val(null).trigger('change');
  });

});
