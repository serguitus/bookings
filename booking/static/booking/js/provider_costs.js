
function get_providers_costs(){
  if (providers_costs_url) {
    $.ajax({
      'url': providers_costs_url,
      'async': true,
      'datatype': 'json',
      'type': 'POST',
      'data': $(service_form_selector).serialize(),
    }).done(function(data){
      update_providers_costs(data);
    }).fail(function(){
      update_providers_costs(null);
    })
  }
}

function update_providers_costs(data){
  content = $('#providers-costs-content');
  has_costs = false;
  if (data && data.costs) {
    html = "<table>";
    html += "<tr>";
    html += "<th>Provider</th>";
    html += "<th style='padding-left: 20px; text-align: center;'>From</th>";
    html += "<th style='padding-left: 20px; text-align: center;'>To</th>";
    html += "<th style='padding-left: 20px; text-align: center;'>Pax Min</th>";
    html += "<th style='padding-left: 20px; text-align: center;'>Pax Max</th>";
    html += "<th style='padding-left: 20px; text-align: right;'>SGL</th>";
    html += "<th style='padding-left: 20px; text-align: right;'>DBL</th>";
    html += "<th style='padding-left: 20px; text-align: right;'>TPL</th>";
    html += "</tr>";
    for (let index = 0; index < data.costs.length; index++) {
      has_costs = true;
      const line = data.costs[index];
      html += "<tr>";
      html += "<td>" + line.provider_name + "</td>";
      html += "<td style='padding-left: 20px; text-align: center;'>" + line.date_from + "</td>";
      html += "<td style='padding-left: 20px; text-align: center;'>" + line.date_to + "</td>";
      html += "<td style='padding-left: 20px; text-align: center;'>" + line.pax_range_min + "</td>";
      html += "<td style='padding-left: 20px; text-align: center;'>" + line.pax_range_max + "</td>";
      html += "<td style='padding-left: 20px; text-align: right;'>" + (line.sgl_cost ? line.sgl_cost : '') + "</td>";
      html += "<td style='padding-left: 20px; text-align: right;'>" + (line.dbl_cost ? line.dbl_cost : '') + "</td>";
      html += "<td style='padding-left: 20px; text-align: right;'>" + (line.tpl_cost ? line.tpl_cost : '') + "</td>";
      html += "</tr>";
    }
    html += "</table>";
  }
  if (has_costs) {
    content.html(html);
  } else {
    content.html('No Providres Costs Are Available');
  }
}
