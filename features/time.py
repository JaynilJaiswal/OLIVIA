from datetime import datetime
import pytz
def getTime(timezone):
    tz = pytz.timezone(timezone)
    time_tz = datetime.now(tz)
    mm = time_tz.strftime("%M")
    if int(mm)==0:
        return "Sir, the time right now is "+time_tz.strftime("%I %p.")
    else:
        return "Sir, the time right now is "+time_tz.strftime("%I %M %p.")
