var add_service_url = base_url + 'booking/quoteservice_book_detail_url/';

$(document).ready(function(){

  $('button.btn-quoteservice_book_detail_add').click(function() {
    if (service_id) {
      showSearchServiceModal(service_id);
    }
  });

});
