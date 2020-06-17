$(document).ready(function(){

  $('#searchServiceModal').on('show.bs.modal', function (event) {
  let button = $(event.relatedTarget) // Button that triggered the modal
  let parent_id = button.data('service_id') // Extract info from data-service_id attribute
  let form_obj = $('form.search_service')
  form_obj.attr('action', add_service_url)
  $('#id_parent_id').val(parent_id)
  });

});

