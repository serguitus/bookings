function showSearchServiceModal(parent_id) {
  $('#id_parent_id').val(parent_id)
  $('#searchServiceModal').modal('show');
}

$(document).ready(function(){

  $('#add_service_dialog_btn').click(function() {
    // sending a request to get service detail url

    $.ajax({
      'url': add_service_url,
      'async': true,
      'datatype': 'json',
      'type': 'POST',
      'data': $('form.search_service').serialize(),
    }).done(function(data){
      if (data.url) {
        window.location.href = base_url + data.url;
      } else {
        console.error('ajax add service url returned with no data');
      }
    }).fail(function() {
      console.error('ajax add service url failed');
    })
  });


});

