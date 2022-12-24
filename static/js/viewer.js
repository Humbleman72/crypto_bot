var socket = io.connect('ws://' + document.domain + ':' + location.port);

socket.on('update_records', function(data) {
     data_table = document.getElementById('data_table')
     new_html_data = "";
     for (const crypto_data of data) {
         console.log(crypto_data);
         console.log(crypto_data['symbol']);
         console.log(crypto_data['buy_price']);

         new_html_data += "<div class=\"ui centered card\">\n";
         new_html_data += "<div class=\"content\">\n";
         new_html_data += "<div class=\"header\">\n";
         new_html_data += crypto_data['symbol'] + " | $" + crypto_data['price'].toFixed(5) + " | ";
         if (crypto_data['percent_change'] >= 0.0) {
            new_html_data += "<span style=\"color:#0dd94e\">"
         }
         else {
            new_html_data += "<span style=\"color:red\">"
         }
         new_html_data += crypto_data['percent_change'].toFixed(2)  + "</span>"
         new_html_data += "</div>\n";
         new_html_data += "<div class=\"meta\">\n";
         new_html_data += "Added: " + crypto_data['date_added'] + " ago";
         new_html_data += "<br>Purchased: $" + crypto_data['buy_price'].toFixed(5) + " (" + crypto_data['buy_time'] + " ago)";
         new_html_data += "</div>\n";
         new_html_data += "<div class=\"description\">\n";
         if (crypto_data['min_percent'] <= -0.05) {
            new_html_data += "<p><span style=\"color:red\">";
         }
         else {
            new_html_data += "<p><span>";
         }
         new_html_data += "Min: " + crypto_data['min_percent'].toFixed(4)  + "</span>  (" + crypto_data['min_percent_time'] + " ago)</p>";
         if (crypto_data['max_percent'] >= 0.10) {
            new_html_data += "<p><span style=\"color:#0dd94e\">";
         }
         else {
            new_html_data += "<p><span>";
         }
         new_html_data += "Max: " + crypto_data['max_percent'].toFixed(4)  + "</span>  (" + crypto_data['max_percent_time'] + " ago)</p>";
         new_html_data += "</div>\n";  // description
         new_html_data += "</div>\n";  // content
         if (crypto_data['status'] == 1) {
            new_html_data += "<div class=\"extra content\"><i class=\"times icon\"></i>Min limit reached in ";
            new_html_data += crypto_data['status_update_time'] + "</div>\n";
         }
         if (crypto_data['status'] == 2) {
            new_html_data += "<div class=\"extra content\"><i class=\"star icon\"></i>Max limit reached in ";
            new_html_data += crypto_data['status_update_time'] + "</div>\n";
         }
         new_html_data += "</div>\n";  // card
         new_html_data += "</div>\n";



     }
     data_table.innerHTML = new_html_data;

});

socket.on('last_update', function(last_update_str) {
     document.getElementById('last_update').innerHTML = last_update_str
});


