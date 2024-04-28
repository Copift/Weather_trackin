from fastapi import FastAPI, Body, Request
from pydantic import BaseModel, json
import mysql.connector
from fastapi.responses import HTMLResponse

import datetime
from fastapi.middleware.cors import CORSMiddleware
config = {
            "host" : 'localhost',
            "user" : 'adm',
            "password" :'1qaz@WSX12',
            "database" :'weather_tracking_test',
        }


def get_weather():
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    print("successfully connected \n")
    # 100 последних замеров
    get_data = f"""select * from Weather_data wd 
        ORDER BY real_measurement_date DESC 
        limit 100; 
        """
    cursor.execute(get_data)
    res = cursor.fetchall()
    # самые новые замеры по каждому трекеру
    data = []
    trackers = []
    for i in res:
        if not(i[0] in trackers):
            trackers.append(i[0])
            data.append(i)
    # берём координаты трекеров
    get_data = f"""select tracker_id, tracker_coordinates  from Trackers_info ti; 
            """
    cursor.execute(get_data)
    cords = cursor.fetchall()
    cnx.close()








app = FastAPI()
origins = ["*"]

def save_data(data):
    #print(data)
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        print("successfully connected \n")

        add_data = f"""INSERT INTO `Weather_data`
                   (real_measurement_date, tracker_id, real_pressure, real_temperature)
                    VALUES
                   (NOW(), { int(data['esp8266id']) }, { float(data['sensordatavalues'][0]['value'])}, { float(data['sensordatavalues'][1]['value'])} );
                    """

        cursor.execute(add_data)
        cnx.commit()
        cnx.close()


    except Exception as ex:
        print("Connection refused...")
        print(ex)





@app.post("/data")
async def create_item(data=Body()):
    save_data(data)
    return data

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/station/{item_id}",response_class=HTMLResponse)
def read_root(item_id: str, request: Request):
    cnx = mysql.connector.connect(**config)
    answ="<html> <body> <style>table, th, td { \
  border: 1px solid black; \
  border-collapse: collapse;  \
  .body {  \
    display: inline-block;   \
} \
} .div { display: inline-block; \
  margin-right: 10px; \
</style>"

    cursor = cnx.cursor()
    cursor.execute(f'SELECT  real_measurement_date,  real_pressure, real_temperature \
  FROM weather_tracking_test.Weather_data  where tracker_id ={item_id} GROUP BY DATE_FORMAT(real_measurement_date, "%y-%m-%d-%H")  LIMIT 24;')
    data=cursor.fetchall()
    answ+='<div>last values<table> '
    answ += '<tr>'
    answ += '<td>' + "time" + '</td>'
    answ += '<td>' + "pressure" + '</td>'
    answ += '<td>' + "temp" + '</td>'
    answ += '</tr>'
    for dataold in data:
        answ+='<tr>'
        answ+='<td>'+str(dataold[0])+'</td>'
        answ+='<td>'+str(dataold[1])+'</td>'
        answ+='<td>'+str(dataold[2])+'</td>'
        answ+='</tr>'
    answ+='</table> </div>'
    cursor = cnx.cursor()
    cursor.execute(f"SELECT predicted_measurement_date, tracker_id, predicted_pressure, is_storm, predicted_temp \
FROM weather_tracking_test.Predicted_weather where tracker_id ={item_id} GROUP BY DATE_FORMAT(predicted_measurement_date, '%y-%m-%d-%H')  LIMIT 24;")
    data = cursor.fetchall()
    answ += 'forecast values<div><table> '
    answ += '<tr>'
    answ += '<td>' + "time" + '</td>'
    answ += '<td>' + "pressure change" + '</td>'
    answ += '<td>' + "temp" + '</td>'
    answ += '</tr>'
    for dataold in data:
        answ += '<tr>'
        answ += '<td>' + str(dataold[0]) + '</td>'
        answ += '<td>' + str(dataold[2]) + '</td>'
        answ += '<td>' + str(dataold[4]) + '</td>'
        answ += '</tr>'
    answ += '</table></div> '


    answ += "</body> </html>"
    return answ


@app.get("/weather")
def send_info():
    dataToSend=[]
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    cursor.execute('SELECT tracker_id, tracker_owner_id, tracker_coordinates \
FROM weather_tracking_test.Trackers_info ;')
    trackers=cursor.fetchall()
    for tracker in trackers:
        cursor.execute(f'SELECT real_measurement_date,  real_pressure, real_temperature \
FROM weather_tracking_test.Weather_data where tracker_id ={tracker[0]} ORDER BY  real_measurement_date LIMIT 1;')
        dataNow=list(cursor.fetchall())
        print(dataNow)
        i=0
        if len(dataNow)==0:
            dataToSend.append({"lat": tracker[2].split(';')[0], "lon": tracker[2].split(';')[1],
                               "last_value_temp":None, "last_value_pressure": None,
                               "station_id": tracker[0], "forecast_storm": None})
        else:
            for item in dataNow:
                print(item,i)
                i+=1
            #!!! LOGIC FOR FORECAST
            cursor.execute(f'SELECT predicted_measurement_date, tracker_id, predicted_pressure, is_storm \
    FROM weather_tracking_test.Predicted_weather where tracker_id = {tracker[0]} and is_storm is  true;')
            forecastdata=cursor.fetchall()
            if len(forecastdata)==0:
               forecast=None
            else:
                forecast=forecastdata[0][0]

            #forecast=datetime.datetime.now()
            dataToSend.append({"lat":tracker[2].split(';')[0],"lon":tracker[2].split(';')[1],
                               "last_value_temp":dataNow[0][2],"last_value_pressure":dataNow[0][1],
                               "station_id":tracker[0], "forecast_storm":forecast})


    return dataToSend
