var add_service_url = base_url + 'booking/quote_book_detail_url/';

$(document).ready(function(){

  $('button.btn-quote_book_detail_add').click(function() {
    row = $(this).parents('tr.details');
    if (row[0] != undefined) {
      row_id = row[0].id;
      if (row_id.startsWith('div_')) {
        showSearchServiceModal(row_id.substring(4));
      }
    }
  });

});
