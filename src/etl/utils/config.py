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
    return date.today()