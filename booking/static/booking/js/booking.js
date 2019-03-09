$(document).ready(function(){

  function show_package_amounts() {
    if ($('#id_is_package_price')[0].checked) {
      $('.form-row.field-package_sgl_price_amount')[0].hidden = false;
    } else {
      $('.form-row.field-package_sgl_price_amount')[0].hidden = true;
    }
  }

  $('.field-is_package_price').on('click', function(e) {
    show_package_amounts();
  })

  show_package_amounts();

});
