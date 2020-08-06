(function($){
$(document).ready(function(){

  $('div.field-box.field-provider>div.related-widget-wrapper').after('<a id="btn-costs" title="Costs" data-toggle="modal" data-target="#popup-costs" class="btn btn-costs fa fa-dollar" href="#"></a>');

  $('#btn-costs').on('click', function (e) {
    get_providers_costs();
  });

  label = $('div.field-booking div label.required');
  label.html(label.html() + '<a id="btn-booking-services-summary" title="Booking Services Summary" data-toggle="modal" data-target="#booking_services_summary" class="btn btn-booking-services-summary fa fa-eye" href="#"></a>');
  label = $('div.field-booking_package div label.required');
  label.html(label.html() + '<a id="btn-bookingpackage-services-summary" title="Booking Package Services Summary" data-toggle="modal" data-target="#bookingpackage_services_summary" class="btn btn-bookingpackage-services-summary fa fa-eye" href="#"></a>');

  // check if there are notes on bookingServices to Expand collapsed notes
  if($('#id_v_notes').val() || $('#id_p_notes').val() || $('#id_provider_notes').val()){
    $('#fieldsetcollapser0.collapse-toggle').click();
  }

  function get_computed_amounts(){
    // sending a request to get computed numbers
    $.ajax({
      'url': bookingservice_amounts_url,
      'async': true,
      'datatype': 'json',
      'type': 'POST',
      'data': $(service_form_selector).serialize(),
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
    if (target == undefined) {
      isManualCost = false;
    } else {
      isManualCost = target.checked;
    }
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

  /* THIS IS FOR HANDLING NIGHTS LOGIC IN BOOKING SERVICES */
  /* ***** IMPORTANT THIS MUST GO BEFORE CALLING COMPUTED AMOUNTS EVENT *********/
  var nights_selector = $('#id_nights');
  var start_selector = $('#id_datetime_from');
  var end_selector = $('#id_datetime_to');

  update_nights();

  nights_selector.on('change', function(){
    update_end_date();
  });
  end_selector.on('change', function(){
    update_nights();
  });
  start_selector.on('change', function(){
    update_end_date();
  });
  /* END OF NIGHTS LOGIC SCRIPT */

  $(service_form_selector + ' input, ' + service_form_selector + ' select').on('change', function(e){
    // following fields trigger a service Status change to 'PENDING
    var fields = ['id_room_type', 'id_board_type', 'id_service', 'id_provider',
      'id_time', 'id_service_addon', 'id_nights', 'id_datetime_from', 'id_datetime_to',
      'id_quantity', 'id_parameter', 'id_location_from', 'id_location_to',
      'id_pickup', 'id_dropoff', 'id_place_from', 'id_place_to',
      'id_schedule_from', 'id_schedule_to', 'id_schedule_time_from',
      'id_schedule_time_to'];
    if (fields.includes(this.id)){
      e.preventDefault();
      $('#id_status').val('PD').trigger('change');
    }
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
    $('#id_location_from').val(null).trigger('change');
    $('#id_location_to').val(null).trigger('change');
    $('#id_addon').val(null).trigger('change');
    $('#id_pickup_office').val(null).trigger('change');
    $('#id_dropoff_office').val(null).trigger('change');
  });

  // for location from changed
  $('#id_location_from').change(function (e) {
    e.preventDefault();
    // clear data
    $('#id_pickup').val(null).trigger('change');
    $('#id_place_from').val(null).trigger('change');
    $('#id_schedule_from').val(null).trigger('change');
  });

  // for location to changed
  $('#id_location_to').change(function (e) {
    e.preventDefault();
    // clear data
    $('#id_dropoff').val(null).trigger('change');
    $('#id_place_to').val(null).trigger('change');
    $('#id_schedule_to').val(null).trigger('change');
  });

  // for conf_number changed
  $('#id_conf_number').change(function (e) {
    e.preventDefault();
    // verify not empty to set confirmed status
    if ($('#id_conf_number').val()) {
      $('#id_status').val('OK').trigger('change');
    }
  });

});

/* HELPER METHODS FOR HANDLING NIGHTS LOGIC IN BOOKING SERVICES */
function update_end_date(){
  var nights = $('#id_nights');
  var start_selector = $('#id_datetime_from');
  var end_selector = $('#id_datetime_to');
  if(start_selector.val() && nights.val()){
    var start_date = get_date_from_string(start_selector.val());
    var computed_end = addDays(start_date, Number(nights.val()));
    var curr_date = computed_end.getDate().toString().padStart(2, '0');
    var curr_month = (computed_end.getMonth() + 1).toString().padStart(2, '0'); //Months are zero based
    var curr_year = computed_end.getFullYear();
    end_selector.val(curr_date + '-' + curr_month + '-' + curr_year)
  }
}

function update_nights(){
  var nights_selector = $('#id_nights');
  var start_selector = $('#id_datetime_from');
  var end_selector = $('#id_datetime_to');
  if(start_selector.val() && end_selector.val()){
    start_date = get_date_from_string(start_selector.val());
    end_date = get_date_from_string(end_selector.val());
    if(start_date && end_date){
      var nights = days_diff(start_date, end_date);
      nights_selector.val(nights);
    }
  }
  return
}

/*
This function converts string with format DDMMYY or format DD-MM-YY
 to valid Date objects. Returns nothing on other formats
*/
function get_date_from_string(date_str){
  var parts =date_str.split('-');
  if(parts[0].length == 6){
    // working with date format DDMMYY
    var date_list = parts[0].match(/.{1,2}/g);
    var result_date = new Date(date_list[2].padStart(4, '20'), date_list[1]-1, date_list[0])
    return result_date;
  }else if(parts[0].length == 2){
    var result_date = new Date(parts[2].padStart(4, '20'), parts[1]-1, parts[0]);
    return result_date;
  }else{
    // unknown format. Do nothing
    return
  }
}

function addDays(date, days) {
    var result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
}

function days_diff(date1, date2) {
    dt1 = new Date(date1);
    dt2 = new Date(date2);
    return Math.floor((Date.UTC(dt2.getFullYear(), dt2.getMonth(), dt2.getDate()) - Date.UTC(dt1.getFullYear(), dt1.getMonth(), dt1.getDate()) ) /(1000 * 60 * 60 * 24));
}
/* END OF HELPER METHODS FOR NIGHTS HANDLING LOGIC */
})(django.jQuery);
