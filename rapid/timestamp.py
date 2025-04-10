from datetime import datetime

def date_str(datetime_obj=None) -> str:
    if not datetime_obj:
        datetime_obj = datetime.now()
    return datetime_obj.strftime("%Y-%m-%d")

def datetime_str(datetime_obj=None) -> str:
    """
    Timestamp to measure see long Elasticsearch takes
    """
    if not datetime_obj:
        datetime_obj = datetime.now()
    return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")

def diff_seconds(start_time: datetime, stop_time: datetime):
    delta = stop_time - start_time
    return abs(delta.total_seconds())
