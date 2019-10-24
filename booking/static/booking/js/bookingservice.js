$(document).ready(function(){

  $('div.field-box.field-provider>div.related-widget-wrapper').after('<a id="btn-costs" data-toggle="modal" data-target="#popup-costs" class="btn btn-costs" href="#">Costs</a>');

  $('#btn-costs').on('click', function (e) {
    get_providers_costs();
  });
  // check if there are notes on bookingServices to Expand collapsed notes
  if($('#id_v_notes').val() || $('#id_p_notes').val() || $('#id_provider_notes').val()){
    $('#fieldsetcollapser0.collapse-toggle').click()
  }

  function get_providers_costs(){
    // sending a request to get computed numbers
    $.ajax({
      'url': bookingservice_providers_costs_url,
      'async': true,
      'datatype': 'json',
      'type': 'POST',
      'data': $(bookingservice_form_selector).serialize(),
    }).done(function(data){
      update_providers_costs(data);
    }).fail(function(){
      update_providers_costs(null);
    })
  }

  function update_providers_costs(data){
    content = $('#providers-costs-content');
    has_costs = false;
    if (data && data.costs) {
      html = "<table>";
      html += "<tr>";
      html += "<th>Provider</th>";
      html += "<th style='padding-left: 20px; text-align: center;'>From</th>";
      html += "<th style='padding-left: 20px; text-align: center;'>To</th>";
      html += "<th style='padding-left: 20px; text-align: right;'>SGL</th>";
      html += "<th style='padding-left: 20px; text-align: right;'>DBL</th>";
      html += "<th style='padding-left: 20px; text-align: right;'>TPL</th>";
      html += "</tr>";
      for (let index = 0; index < data.costs.length; index++) {
        has_costs = true;
        const line = data.costs[index];
        html += "<tr>";
        html += "<td>" + line.provider_name + "</td>";
        html += "<td style='padding-left: 20px; text-align: center;'>" + line.date_from + "</td>";
        html += "<td style='padding-left: 20px; text-align: center;'>" + line.date_to + "</td>";
        html += "<td style='padding-left: 20px; text-align: right;'>" + (line.sgl_cost ? line.sgl_cost : '') + "</td>";
        html += "<td style='padding-left: 20px; text-align: right;'>" + (line.dbl_cost ? line.dbl_cost : '') + "</td>";
        html += "<td style='padding-left: 20px; text-align: right;'>" + (line.tpl_cost ? line.tpl_cost : '') + "</td>";
        html += "</tr>";
      }
      html += "</table>";
    }
    if (has_costs) {
      content.html(html);
    } else {
      content.html('No Providres Costs Are Available');
    }
  }

  function get_computed_amounts(){
    // sending a request to get computed numbers
    $.ajax({
      'url': bookingservice_amounts_url,
      'async': true,
      'datatype': 'json',
      'type': 'POST',
      'data': $(bookingservice_form_selector).serialize(),
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

  $(bookingservice_form_selector + ' input, ' + bookingservice_form_selector + ' select').on('change', function(){
    get_computed_amounts();
  });

  // for dates changed by calendar
  $(bookingservice_form_selector + ' input[name*="datetime"]').focusout(function (e) {
    e.preventDefault();
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
    $('#id_provider').val(null).trigger('change');
    $('#id_location_from').val(null).trigger('change');
    $('#id_location_to').val(null).trigger('change');
    $('#id_addon').val(null).trigger('change');
    $('#id_provider').val(null).trigger('change');
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

  /* THIS IS FOR HANDLING NIGHTS LOGIC IN BOOKING SERVICES */
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
});

/* HELPER METHODS FOR HANDLING NIGHTS LOGIC IN BOOKING SERVICES */
function update_end_date(){
  var nights = $('#id_nights');
  var start_selector = $('#id_datetime_from');
  var end_selector = $('#id_datetime_to');
  if(start_selector.val() && nights.val()){
    var parts =start_selector.val().split('-');
    var start_date = new Date(parts[2].padStart(4, '20'), parts[1] - 1, parts[0]);
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
    var parts =start_selector.val().split('-');
    var start_date = new Date(parts[2], parts[1] - 1, parts[0]);
    var parts2 =end_selector.val().split('-');
    var end_date = new Date(parts2[2], parts2[1] - 1, parts2[0]);
    var nights = days_diff(start_date, end_date);
    nights_selector.val(nights);
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
