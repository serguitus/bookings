$(document).ready(function () {

  $('input[name^="form-"][name$="-is_selected"][type="checkbox"]').on('change', function (e) {
    e.preventDefault();
    update_amount_paid();
  });

  $('input[name^="form-"][name$="-amount_paid"][type="number"]').on('change', function (e) {
    e.preventDefault();
    changed_amount(e.target);
    update_amount_paid();
  });

  function changed_amount(input) {
    input_id = input.id;
    idx = input_id.substring(8, input_id.length - 12);
    div_t = $('#id_form-' + idx + '-service_amount_to_pay');
    div_p = $('#id_form-' + idx + '-service_amount_paid');
    compare_amounts(div_t, div_p, $(input));
  }

  function compare_amounts(div_t, div_p, id) {
    div_tv = Number(div_t.html());
    div_pv = Number(div_p.html());
    idv = Number(id.val());
    if (div_tv - div_pv == idv) {
      id.removeClass('btn-danger');
    } else {
      id.addClass('btn-danger');
    }
  }

  function update_amount_paid() {
    total_amount = 0.00;
    $('input[name^="form-"][name$="-is_selected"][type="checkbox"]:checked').each(function() {
      checkbox = $(this)[0];
      idx = checkbox.id.substring(8, checkbox.id.length - 12);
      amount = Number($('#id_form-' + idx + '-amount_paid').val());
      total_amount += amount;
    });
    $('div.field-box.field-amount div.readonly').html(total_amount.toFixed(2));
  }

});
