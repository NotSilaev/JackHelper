import datetime


def daysInYear():
    year = datetime.datetime.now().year
    if year % 4 == 0:
        if str(year)[-2:] != '00' or year % 400 == 0:
            return 366
    return 365
