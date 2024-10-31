import datetime


def daysInYear():
    year = datetime.datetime.now().year
    if year % 4 == 0:
        if str(year)[-2:] != '00' or year % 400 == 0:
            return 366
    return 365


def ifNoneGetDefaultValues(city, start_date, end_date) -> tuple:
    if city is None: city = 'VLG'
    
    if start_date is None: start_date = datetime.date.today()
    else: start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()

    if end_date is None: end_date = start_date
    else: end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

    return city, start_date, end_date