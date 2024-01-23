import os

def get_workdir():
    """
    return project abs path string
    """
    if os.environ.get('PYTHONPATH') == "'/var/task'":
        return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    return os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), os.pardir), os.pardir))
