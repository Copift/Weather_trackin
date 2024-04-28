ymaps.ready(init);
var HttpClient = function() {
    this.get = function(aUrl, aCallback) {
        var anHttpRequest = new XMLHttpRequest();
        anHttpRequest.onreadystatechange = function() {
            if (anHttpRequest.readyState == 4 && anHttpRequest.status == 200)
                aCallback(anHttpRequest.responseText);
        }

        anHttpRequest.open( "GET", aUrl, true );
        anHttpRequest.send( null );
    }
}
function init() {
    var myMap = new ymaps.Map("map", {
            center: [55.76, 37.64],
            zoom: 10
        }, {
            searchControlProvider: 'yandex#search'
        })

    var geolocation = ymaps.geolocation, myMap ;

    // Сравним положение, вычисленное по ip пользователя и
    // положение, вычисленное средствами браузера.


    geolocation.get({
        provider: 'browser',
        mapStateAutoApply: true
    }).then(function (result) {
        // Синим цветом пометим положение, полученное через браузер.
        // Если браузер не поддерживает эту функциональность, метка не будет добавлена на карту.
        result.geoObjects.options.set('preset', 'islands#blueCircleIcon');
        myMap.geoObjects.add(result.geoObjects);
    });
var client = new HttpClient();
client.get('http://localhost:8000/weather', function(response) {
          response=JSON.parse(response);
         for (var i = 0; i < response.length; i++) {



                  console.log(response[i])
                  var obj=response[i]
                  if (obj["last_value_temp"]!=null){

                  if (obj["last_value_temp"]>0){
                   color=`#${parseInt(obj["last_value_temp"]).toString(16)}${parseInt(obj["last_value_temp"]).toString(16)}aa00`
                  }
                         else {
                   var color=`#00aa${parseInt(obj["last_value_temp"]+parseInt(obj["last_value_temp"]*2)).toString(16)}${parseInt(obj["last_value_temp"]+parseInt(obj["last_value_temp"]*2)).toString(16)}`}
                    }
                    else
                    {
                    var color ='#FFFFFF'
                    }
                    console.log (color)
                  myMap.geoObjects.add(new ymaps.Placemark([obj["lat"], obj["lon"]], {


            iconCaption: `id ${obj["station_id"]}`,
            balloonContent: ` "station_id": ${obj["station_id"]}, \n
            "lat": "${obj["lat"]},\n
            "lon": ${obj["lon"]}, \n
            "last_value_temp": ${obj["last_value_temp"]}, \n
            "last_value_pressure": "${obj["last_value_pressure"]}, \n
            "forecast_storm": ${obj["forecast_storm"]} \n
            <p><a href="http://localhost:8000/station/${obj["station_id"]}">details</a></p>

            `

        }, {




        // The size of the placemark.
        iconImageSize: [3000, 42000],
        /**
         * The offset of the upper left corner of the icon relative
         * to its "tail" (the anchor point).
         */
        iconImageOffset: [-50000, -38000],
              iconColor: color,
        }))


          }

});


    // Создаем геообъект с типом геометрии "Точка".

}
