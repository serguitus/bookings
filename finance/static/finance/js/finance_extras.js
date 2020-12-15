$(document).ready(function(){
  /* the place to set the computed total of selected rows*/
  let total_count = $('.fieldBox.field-selected_amount .readonly')
  let max_amount = $('.fieldBox.field-amount .readonly')
  let submit_btn = $('input[name="_save"]')

  function check_total(){
    if(parseFloat(max_amount.html())<parseFloat(total_count.html())){
      // you excedded max posible amount to match
      total_count.siblings('label').addClass('overflow-value')
      total_count.addClass('overflow-value')
      max_amount.siblings('label').addClass('overflow-value')
      max_amount.addClass('overflow-value')
      submit_btn.prop('disabled', true)
    }else{
      total_count.siblings('label').removeClass('overflow-value')
      total_count.removeClass('overflow-value')
      max_amount.siblings('label').removeClass('overflow-value')
      max_amount.removeClass('overflow-value')
      submit_btn.prop('disabled', false)
    }
  }

  $('input').on('change', () => {
    let counter = 0
    $('#result_list tbody tr').each(function(index){
      if($(this).find('input[id*="included"]').prop("checked")){
        counter += parseFloat($(this).find('input[id*="match_amount"]').val())
      }
    })
    total_count.html(counter)
    check_total()
  })
})
