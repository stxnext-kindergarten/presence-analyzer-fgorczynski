google.load("visualization", "1", {packages:["corechart", "timeline"], 'language': 'pl'});

(function($) {
    $(document).ready(function(){
        var loading = $('#loading');
        $.getJSON("/api/v1/users", function(result) {
            var dropdown = $("#user_id");
            $.each(result, function(item) {
                dropdown.append($("<option />").val(this.user_id).text(this.name));
            });
            dropdown.show();
            loading.hide();
        });
        $('#user_id').change(function() {
            var selected_user = $("#user_id").val();
            var chart_div = $('#chart_div');
            if(selected_user) {
                loading.show();
                chart_div.hide();
                
                $.getJSON("/api/v1/presence_start_end/" + selected_user, function(result) {
                    $.each(result, function(index, value) {
                        // convert returned datetime strings to valid JavaScript Date object
                        var start_time = value[1].split(" ")[1].split(':'),
                            end_time = value[2].split(" ")[1].split(':');
                        value[1] = new Date(1, 1, 1, start_time[0], start_time[1], start_time[2]);
                        value[2] = new Date(1, 1, 1, end_time[0], end_time[1], end_time[2]);
                    });
                    var data = new google.visualization.DataTable();
                    data.addColumn('string', 'Weekday');
                    data.addColumn({ type: 'datetime', id: 'Start' });
                    data.addColumn({ type: 'datetime', id: 'End' });
                    data.addRows(result);
                    var options = {
                        hAxis: {title: 'Weekday'}
                    };
                    var formatter = new google.visualization.DateFormat({pattern: 'HH:mm:ss'});
                    formatter.format(data, 1);
                    formatter.format(data, 2);
    
                    chart_div.show();
                    loading.hide();
                    var chart = new google.visualization.Timeline(chart_div[0]);
                    chart.draw(data, options);
                });
                
                

            }
        });
    });
})(jQuery);
