from datetime import datetime
import pytz
def getDate(timezone):
    tz = pytz.timezone(timezone)
    time_tz = datetime.now(tz)
    d = int(time_tz.strftime("%d"))
    if d==1:
        return "Sir, today is "+time_tz.strftime("%A")+" and "+time_tz.strftime("%dst of %B, %Y.")
    elif d==2:
        return "Sir, today is "+time_tz.strftime("%A")+" and "+time_tz.strftime("%dnd of %B, %Y.")
    elif d==3:
        return "Sir, today is "+time_tz.strftime("%A")+" and "+time_tz.strftime("%drd of %B, %Y.")
    else:
        return "Sir, today is "+time_tz.strftime("%A")+" and "+time_tz.strftime("%dth of %B, %Y.")