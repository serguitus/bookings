var bookingservice_amounts_url = base_url + 'booking/bookingextra-amounts/';
var service_form_selector = '#bookingextra_form';
var providers_costs_url = base_url + 'booking/bookingextra-providers-costs/';
var service_details_url = base_url + 'booking/extra-service-details/';

$(document).ready(function(){
    function get_component_computed_amounts() {
        if($(service_form_selector).length){
          $('select[name^="bookingextracomponent_set-"][name$="-component"]').attr('disabled', false);
          data = $(service_form_selector).serialize();
          $('select[name^="bookingextracomponent_set-"][name$="-component"]').attr('disabled', true);
        }
        $.ajax({
          'url': base_url + 'booking/bookingextracomponent-amounts/',
          'async': true,
          'datatype': 'json',
          'type': 'POST',
          'data': data,
        }).done(function(data){
          if(data['code'] == 0){
            values = data['results'];
            values.forEach(component_data => {
              quote_pax_variant_id = pax_data.quote_pax_variant;
              // find variant index
              for (idx = 0; idx < 50; idx++) {
                quote_component_input = $('#id_bookingextracomponent_set-' + idx + '-component');
                component_value = Number(quote_pax_variant_input.val());
                if (quote_pax_variant_value && quote_pax_variant_value == quote_pax_variant_id) {
                  update_component_amounts(false, idx, 1, pax_data.total.cost_1, pax_data.total.cost_1_msg);
                  update_component_amounts(true, idx, 1, pax_data.total.price_1, pax_data.total.price_1_msg);
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
    
    function changed_component_manual_costs(target){
        isManualCost = target.checked;
        // find index
        idx = target.name.substring(25, target.name.length - 13);
        if(isManualCost){
          $('#' + idx + '-btn-cost').show();
        } else {
          $('#' + idx + '-btn-cost').hide();
        }
        $('#id_bookingextracomponent_set-' + idx + '-cost_amount')[0].readOnly = !isManualCost;
        get_component_computed_amounts();
    }
    
    function changed_component_manual_prices(target){
        isManualPrice = target.checked;
        idx = target.name.substring(25, target.name.length - 14);
        if(isManualPrice){
          $('#' + idx + '-btn-price').show();
        } else {
          $('#' + idx + '-btn-price').hide();
        }
        $('#id_bookingextracomponent_set-' + idx + '-price_amount')[0].readOnly = !isManualPrice;
        get_component_computed_amounts();
    }
    
    function show_component_buttons() {
        for (idx = 0; idx < 50; idx++) {
          $('#' + idx + '-btn-cost').detach();
          $('#' + idx + '-span-cost').detach();
          $('#' + idx + '-btn-price').detach();
          $('#' + idx + '-span-price').detach();
          field = $('#id_bookingextracomponent_set-' + idx + '-cost_amount');
          if (field[0] != undefined) {
            $('#id_bookingextracomponent_set-' + idx + '-cost_amount').after('<button id="' + idx + '-btn-cost" class="btn btn-copy-cost"><<</button><span id="' + idx + '-span-cost" class="computed-value">N/A</span>');
            $('#id_bookingextracomponent_set-' + idx + '-price_amount').after('<button id="' + idx + '-btn-price" class="btn btn-copy-price"><<</button><span id="' + idx + '-span-price" class="computed-value">N/A</span>');
            changed_component_manual_costs($('#id_bookingextracomponent_set-' + idx + '-manual_costs')[0]);
            changed_component_manual_prices($('#id_bookingextracomponent_set-' + idx + '-manual_prices')[0]);
          } else {
            field = $('#bookingextracomponent_set-' + idx + ' div.field-cost_amount div.field-cost_amount div.readonly');
            if (field[0] != undefined) {
              $('#bookingextracomponent_set-' + idx + ' div.field-cost_amount div.field-cost_amount div.readonly').after('<span id="' + idx + '-span-cost" class="computed-value">N/A</span>');
              $('#bookingextracomponent_set-' + idx + ' div.field-price_amount div.field-price_amount div.readonly').after('<span id="' + idx + '-span-price" class="computed-value">N/A</span>');
            } else {
              break;
            }
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
              compare_component_amounts(input, span, button);
              get_computed_component_amounts();
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
              compare_component_amounts(input, span, button);
              get_computed_component_amounts();
            }
            return false;
        });
    }

    show_component_buttons();
    get_component_computed_amounts();

});
