import os
import mysql.connector
cnx=mysql.connector.connect(host='10.8.0.1',user='adm',password='1qaz@WSX12',database='weather_tracking_test')
cursor=cnx.cursor()
for file in  os.listdir("data_year"):
    if '.csv' in file:
        print(file)
        file =open("data_year/"+file,'r')
        sql="INSERT INTO weather_tracking_test.Weather_data (real_measurement_date, tracker_id, real_pressure, real_temperature) VALUES "
        for line in file.readlines():
            if not('pressure' in line):
                line=line.split(';')

                sql+=f' (STR_TO_DATE("{line[5]}", "%Y-%m-%dT%H:%i:%s"), {line[0]}, {line[6]}, {line[9]}), \n'
        print(sql[:-3]+';')
        cursor.execute(sql[:-3]+';')
        cnx.commit()
