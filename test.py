import datetime as dt

def add_hour_and_half(time):
    parsed_time = dt.datetime.strptime(time, "%H:%M").time()
    new_time = (dt.datetime.combine(dt.date.today(), parsed_time) + dt.timedelta(hours=1,minutes=00)).time()
    return new_time.strftime("%H:%M")

print(add_hour_and_half("10:00"))

