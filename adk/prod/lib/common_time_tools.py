import datetime
import logging

def get_day_today() -> str:
    '''Gets today's date in YYYY-MM-DD format'''
    logging.warning(f"⏳🕜 get_day_today()")

    return str(datetime.date.today()) # Use date() for just the date part

