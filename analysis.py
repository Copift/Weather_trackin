import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
import mysql.connector
import datetime


config = {
            "host": '10.8.0.1',
            "user": 'adm',
            "port": 3306,
            "password": '1qaz@WSX12',
            "database": 'weather_tracking_test',
        }


warnings.filterwarnings("ignore")

def stat_check(row):
    # проверяем стационарность тестом Дики-Фуллера
    result = adfuller(row)
    print('ADF Statistic: %f' % result[0])
    print('p-value: %f' % result[1])
    print('Critical Values:')
    for key, value in result[4].items():
        print('\t%s: %.3f' % (key, value))
    return result[1]

def raw_to_data(f):
    #собираем датасеты со средним значением для каждого часа
    f.readline()
    raw_data = f.readlines()
    day = raw_data[2].split(';')[5][0:11]
    data = {'Timestamp': [day+str(i)+":00:00" for i in range(24)], 'Param': []}
    Pressure = []
    for i in range(24):
        S = 0
        k = 0
        for j in range(len(raw_data)):
            if int(raw_data[j].split(';')[5][11:13]) == i:
                    S+=float(raw_data[j].split(';')[9])
                    k+=1
        Pressure.append(S/k)
    data.update({'Param': Pressure})
    return data

def data_add(data1, data2):
    #складываем два датасета в один
    for i in range(24):
        data1['Timestamp'].append(data2['Timestamp'][i])
        data1['Param'].append(data2['Param'][i])
    return data1

def print_graphic(df_part, legend, title, xlabel, ylabel):
    plt.plot(df_part)
    plt.legend(legend)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    #plt.show()


def get_weather():
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    print("successfully connected \n")

    get_data = f"""SELECT tracker_id, DATE_FORMAT(real_measurement_date,'%d-%m-%yT%H:00:00') as w_date, Avg(real_pressure), Avg(real_temperature)  
            FROM Weather_data wd 
            WHERE 
            real_measurement_date >= DATE_SUB(CURDATE(), INTERVAL 6 DAY) AND real_measurement_date <= CURDATE()
            GROUP BY w_date, tracker_id 
            ORDER BY tracker_id, w_date;
            """

    cursor.execute(get_data)
    data = cursor.fetchall()

    tracker = data[0][0]
    #print(tracker)

    tracker_num = 0
    trackers_data = [[]]

    for tracker_data in data:
        if tracker_data[0] == tracker:
            trackers_data[tracker_num].append(tracker_data)
        else:
            tracker = tracker_data[0]
            trackers_data.append([])
            tracker_num += 1

    cnx.close()
    return trackers_data


def send_predicted_weather(data):
    request = """INSERT INTO Predicted_weather 
        (tracker_id, predicted_measurement_date, predicted_pressure, predicted_temp, is_storm)
        values """

    for i in data:
        request += " " + str(i) + ","

    request = request[:-1] + ";"

    print(request)

    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    print("successfully connected \n")

    cursor.execute(request)
    cnx.commit()
    cnx.close()



#//////////////////////////////////////////////////////////////

def make_model(df, param):
    result = stat_check(df[param])
    df['Param_stationed'] = df[param]

    while (result > 0.05):  # данные нестационарны, так как вероятность ошибочных данных >5%
        # дифференцируем данные
        df['Param_without_trend'] = df[param] - df[param].rolling(window=2).mean()
        df['Param_stationed'] = df['Param_without_trend'].diff()  # удалили сезонность
        df.dropna(inplace=True)
        result = stat_check(df['Param_stationed'])
        print("RESULT = ", result)
    print_graphic(df['Param_stationed'], "", "Стационарные данные", "Время", "Параметр")

    # создаем модель для предсказания
    model = SARIMAX(df['Param_stationed'], order=(1, 0, 0), seasonal_order=(1, 1, 0, 24))
    results = model.fit()
    print(results.summary())

    # Предсказываем существующие данные
    #time_start = "2024-04-25T01:00:00"
    #st_pred = results.get_prediction(start=pd.to_datetime(time_start), dynamic=False)
    #forecast_values = st_pred.predicted_mean
    #actual_values = df[time_start:]['Param_stationed']
    #forecast_mse = ((forecast_values - actual_values) ** 2).mean()
    #print('Среднеквадратичная ошибка прогноза составляет {}'.format(round(forecast_mse, 2)))

    #plt.plot(actual_values.index, actual_values, label='Реальные значения', color='blue')
   # plt.plot(forecast_values.index, forecast_values, label='Спрогнозированные значения', color='red')
   # plt.title('Реальные и cпрогнозированные значения')
   # plt.xlabel('Дата')
   # plt.ylabel('Параметр')
   # plt.legend()
   # plt.show()

    pred_future = results.get_forecast(steps=72)

    print(f'Средние прогнозируемые значения:\n\n{pred_future.predicted_mean}')
    print(f'\nДоверительные интервалы:\n\n{pred_future.conf_int()}')

    fig = plt.figure()
    plt.plot(pred_future.predicted_mean, label='Средние прогнозируемые значения')
    plt.fill_between(pred_future.conf_int().index,
                     pred_future.conf_int().iloc[:, 0],
                     pred_future.conf_int().iloc[:, 1], color='k', alpha=.2)
    plt.legend()
    #plt.show()

    return pred_future


#достаем данные
#f = open("2024-04-23(2).csv")
#f2 = open("2024-04-24(2).csv")
#f3 = open("2024-04-25(2).csv")
#f4 = open("2024-04-26(2).csv")
#data = raw_to_data(f)
#data2 = raw_to_data(f2)
#data3 = raw_to_data(f3)
##data = data_add(data, data2)
#data = data_add(data, data3)
#data = data_add(data, data4)
#print(data)


#//////////////////////////////////////////////////////////////


# берём данные из таблицы
trackers_data = get_weather()


for tracker_data in trackers_data:

    print(tracker_data)

    Timestamp = []
    Pressure = []
    Temperature = []

    for t_data in tracker_data:
        Timestamp.append(t_data[1])
        Pressure.append(t_data[2])
        Temperature.append((t_data[3]))
    data = {'Timestamp': Timestamp, 'Pressure': Pressure, 'Temperature': Temperature}

    #print(data)



    # создаем датасет
    df = pd.DataFrame(data)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df.set_index('Timestamp', inplace=True)
    print_graphic(df['Pressure'], "", "Исходные данные", "Время", "Давление")
    print_graphic(df['Temperature'], "", "Исходные данные", "Время", "Температура")



    # приводим датасет к нужной форме
    df = df.fillna(df.mean())  # заполняем пропущенные ячейки на основе соседних значений

    t_prediction = make_model(df, 'Temperature')
    p_prediction = make_model(df, 'Pressure')

    final_result = [(tracker_data[0][0], str(t_prediction.conf_int().index[i]).replace(' ', 'T'), t_prediction.predicted_mean[i], p_prediction.predicted_mean[i],bool(abs(float(p_prediction.predicted_mean[i]))>15) ) for i in range(72)]
    print(final_result)

    send_predicted_weather(final_result)


