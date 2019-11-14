$(document).ready(function(){

  $('#id_amount').change(function (e) {
    e.preventDefault();

    booking_amount = Number($('div.field-box.field-booking_amount div.readonly').html());
    amount = Number($('#id_amount').val());
    if (booking_amount && amount) {
      $('div.field-box.field-currency_rate div.readonly').html(Number(amount / booking_amount).toFixed(4));
    }
  });

});
