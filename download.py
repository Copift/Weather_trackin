import datetime
import urllib.request
s='https://archive.sensor.community/2024-04-24/2024-04-24_bme280_sensor_3122.csv'
date= datetime.datetime.now() - datetime.timedelta(days=2)
for i in range (0,365):
    e=(date-datetime.timedelta(days=i)).strftime("%Y-%m-%d")
    print(e)
    urllib.request.urlretrieve(f'https://archive.sensor.community/{e}/{e}_bme280_sensor_8140.csv', f"data_year/{e}.csv")

