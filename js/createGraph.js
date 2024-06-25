var device_name = "device_name"
var hosturl = "API_URL"
var apiurl = hosturl + "/data/" + device_name

//-------------------------------------------
function createChart() {
    reqGet(device_name);
}
//-------------------------------------------
// QueryDyanmo()
//    execute query to DynamoDB
//-------------------------------------------
function reqGet(device_name) {
    console.log("reqGet() start");
    $.get(apiurl, function(data) {
        }).done(function(data) {
            // Ensure data is already parsed
            if (typeof data === "string") {
                data = JSON.parse(data);
            }
            var jsonData = data[device_name];
            console.log(jsonData);

            drawChart(jsonData);

        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            console.log(jqXHR.responseText);
        });
}
//-------------------------------------------
// drawChart()
//-------------------------------------------
function drawChart(vals) {
    console.log("drawChart() start");
    var val_list = [];
    for (var i = 0; i < vals.length; i++) {
        console.log(vals[i]);
        var item = { "label": vals[i].timestamp, "y": parseFloat(vals[i].value) };
        val_list.push(item);
    }
    //! DrawChart kick
    var chart = new CanvasJS.Chart("chart", {
        title: {
            text: "TEMPERATURE Chart"
        },
        data: [{
            type: "line",
            dataPoints: val_list
        }]
    });
    chart.render();
}

