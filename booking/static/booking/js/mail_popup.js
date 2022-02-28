$(document).ready(function(){

  $('#send_btn').on('click', function() {
    submit_form();
  });

  function submit_form() {
    $('#id_submit_action').val('_send_mail');
    $('#id_mail_from').val($('#m_from').val());
    $('#id_mail_to').val($('#m_to').val());
    $('#id_mail_cc').val($('#m_cc').val());
    $('#id_mail_bcc').val($('#m_bcc').val());
    $('#id_mail_subject').val($('#m_subject').val());
    $('#id_mail_body').val($('#m_body').val());
    $('form[id^=booking], form[id^=quote, form[id^=providerbookingpayment]').submit();
  }

});
