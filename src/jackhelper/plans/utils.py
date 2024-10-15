import datetime

def daysUntilNextMonth(start_date):
    if start_date.month == 12:
        next_month = datetime.datetime(start_date.year + 1, 1, 1)
    else:
        next_month = datetime.datetime(start_date.year, start_date.month + 1, 1)
    
    delta = next_month - start_date
    return delta.days