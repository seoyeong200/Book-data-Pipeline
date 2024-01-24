def get_workdir():
    import os
    """
    return project abs path string
    """
    if os.environ.get('PYTHONPATH') == '/var/task':
        return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    return os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), os.pardir), os.pardir))

def get_date():
    from datetime import date
    return str(date.today())


def is_same_week(dateString):
    import datetime
    d1 = datetime.datetime.strptime(dateString,'%Y-%m-%d')
    d2 = datetime.datetime.today()
    return d1.isocalendar()[1] == d2.isocalendar()[1] \
              and d1.year == d2.year