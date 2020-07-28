(function ($){
$(document).ready(function(){

  var make_package_check = $('#div_id_make_package')
  jQuery('#searchServiceModal').on('show.bs.modal', function (event) {
  let button = jQuery(event.relatedTarget) // Button that triggered the modal
  let parent_id = button.data('service_id') // Extract info from data-service_id attribute
  let form_obj = $('form.search_service')
  form_obj.attr('action', add_service_url)
  jQuery('#id_parent_id').val(parent_id)
  });

  $('#id_search_service').on('select2:select', function (e) {
    let data = e.params.data;
    let make_package_input = $('input#id_make_package')
    if(data['service_type'] == 'E'){
      // this is an Extra service. show checkbox
      make_package_check.show()
      if(data['default_as_package']){
        make_package_input.prop('checked', true)
      }else
        make_package_input.prop('checked', false)
    }
    else
      make_package_check.hide()
  });
  // at the very beginning, hide the checkbox. nothing selected
  make_package_check.hide()
});

})(django.jQuery);
