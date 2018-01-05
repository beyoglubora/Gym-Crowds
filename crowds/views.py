from django.shortcuts import render
import datetime
import pytz
import pickle
import numpy as np
import matplotlib.pyplot as plt
try:
    import cStringIO
except ImportError:
    import io


def index(request):
    tz = pytz.timezone('America/Chicago')
    current_timestamp = datetime.datetime.now(tz)
    midnight = current_timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
    date_info = {'hour': int(current_timestamp.hour-1), 'day_of_week': int(current_timestamp.weekday()),
                 'is_weekend': int(current_timestamp.weekday() == 5 or current_timestamp.weekday() == 6),
                 'is_start_of_semester': int(((current_timestamp.month == 8 and current_timestamp.day >= 26) or
                                             (current_timestamp.month == 9 and current_timestamp.day <= 8)) or
                                             (current_timestamp.month == 1 and current_timestamp.day >= 17)
                                             ),
                 'is_holiday': 0, 'is_during_semester': 1, 'month': int(current_timestamp.month),
                 'timestamp': int((current_timestamp - midnight).seconds)
                 }

    crowded = predict(date_info, True)
    plot_chart(date_info)
    activities = get_daily_activites(date_info['day_of_week'])
    print(activities)
    return render(request, 'crowds/index.html', {'gym_status': crowded, 'activities': activities})


def get_daily_activites(day):
    activity_info = {'Dark Room Cycling': [('0,2,4,6', '5:30-6:20pm', 'https://maxcdn.icons8.com/Share/icon/Transport//bicycle1600.png', '110', '110', '-30', '50'), ('3', '7:00-7:50pm', 'https://maxcdn.icons8.com/Share/icon/Transport//bicycle1600.png', '110', '110', '-30', '50'), ('5', '2:00-2:50pm', 'https://maxcdn.icons8.com/Share/icon/Transport//bicycle1600.png', '110', '110', '-30', '50')],
                     'Vinyasa Yoga': [('0', '7:00-7:50pm', 'https://i.pinimg.com/originals/c8/8f/74/c88f740b0af1c215f37206c32f869648.png', '110', '60', '-35', '78'), ('4', '6:30-7:20pm', 'https://i.pinimg.com/originals/c8/8f/74/c88f740b0af1c215f37206c32f869648.png', '110', '60', '-35', '78'), ('6', '10:00-10:50am', 'https://i.pinimg.com/originals/c8/8f/74/c88f740b0af1c215f37206c32f869648.png', '110', '60', '-35', '78')],
                     # 'Power Yoga': [('1', '6:30-7:20am'), ('2', '8:00-8:50pm'), ('3', '6:30-7:20am')],
                     # 'Restorative Yoga': [('1', '8:00-8:50pm'), ('3', '8:00-8:50pm')],
                     'Zumba': [('0,4', '5:30-6:20pm', 'http://zumbatimmins.com/wp-content/uploads/2016/06/dance1.png', '160', '110', '-60', '55'), ('2,3', '7:00-7:50', 'http://zumbatimmins.com/wp-content/uploads/2016/06/dance1.png', '160', '110', '-60', '55'), ('6', '6:00-6:50pm', 'http://zumbatimmins.com/wp-content/uploads/2016/06/dance1.png', '160', '110', '-60', '55')],
                     # 'Cycling': [('0', '7:30-8:20pm'), ('1', '7:00-7:50pm'), ('5', '10:00-10:50am')],
                     # 'Weekend Warrior Workout': [('5', '11:00-11:50am')],
                     'Intermediate Yoga': [('6', '5:00-6:20pm', 'https://www.yogaalliance.org/portals/0/img/YA-Flower.png', '100', '100', '-30', '60')],
                     'HIIT':[('0', '4:00-4:30pm', 'https://cdn2.iconfinder.com/data/icons/medical-line-5/512/cardiology_heart_organ-512.png', '100', '100', '-30', '60')],
                     'Cardio Barre': [('0', '4:30-5:20pm', 'https://i.pinimg.com/originals/81/18/9e/81189e7deec9fdb988e493465ab18236.png', '110', '100', '-40', '60')]
                     }

    todays_activities = []
    for activity in activity_info:
        activity_data = activity_info[activity]
        for j in activity_data:
            if str(day) in j[0]:
                todays_activities.append((activity, j[1], j[2], j[3], j[4], j[5], j[6]))
                break
    print(todays_activities)
    return todays_activities


def plot_chart(date_info):
    x, y = get_data(date_info)
    fig, ax = plt.subplots()
    ax.bar(x, y)
    fig.patch.set_visible(False)
    ax.axis('off')
    ax.axis('on')
    ax.set_axis_bgcolor('None')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.savefig('/Users/Bora/PycharmProjects/first_app/crowds/static/images/testplot.png', format="png",
                facecolor=(0.95, 0.95, 0.95))
    plt.clf()


def get_data(date_info):
    x, y = [], []
    counter = 0
    date_info_temp = date_info
    while counter < 5:
        x.append(date_info_temp['hour'])
        y.append(predict(date_info_temp, False) + 1)
        date_info_temp['hour'] += 1
        date_info_temp['timestamp'] += 3600
        counter += 1
    return x, y


def predict(date_info, classification):
    if date_info['day_of_week'] >= 0 and date_info['day_of_week'] <=3 and (date_info['hour'] <= 5 or date_info['hour'] >= 22):
        return -1
    if date_info['day_of_week'] == 4 and (date_info['hour'] < 5 or date_info['hour'] >= 20):
        return -1
    if date_info['day_of_week'] == 5 and (date_info['hour'] < 8 or date_info['hour'] >= 20):
        return -1
    if date_info['day_of_week'] == 6 and (date_info['hour'] < 8 or date_info['hour'] >= 22):
        return -1
    classification_model = pickle.load(open('/Users/Bora/Desktop/Computer Science Projects/Data Science Projects/'
                                    'Gym Crowdedness/classification_model.sav', 'rb'))
    regression_model = pickle.load(open('/Users/Bora/Desktop/Computer Science Projects/Data Science Projects/'
                                    'Gym Crowdedness/regression_model.sav', 'rb'))
    min_max = pickle.load(open('/Users/Bora/Desktop/Computer Science Projects/Data Science Projects/'
                               'Gym Crowdedness/min_max.sav', 'rb'))
    x = np.array([date_info['timestamp'], date_info['day_of_week'], date_info['is_weekend'], date_info['is_holiday'],
                 date_info['is_start_of_semester'], date_info['is_during_semester'], date_info['month'],
                 date_info['hour']])
    x_scaled = min_max.transform(x.reshape(1, -1))
    if classification:
        return classification_model.predict(x_scaled)[0]
    else:
        return regression_model.predict(x_scaled)[0]
