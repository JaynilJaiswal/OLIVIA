from datetime import datetime
import pytz
def getTime(timezone):
    tz = pytz.timezone(timezone)
    time_tz = datetime.now(tz)
    mm = time_tz.strftime("%M")
    if int(mm)==0:
        output_time =  "Sir, the time right now is "+time_tz.strftime("%I %p.")
        return output_time.replace("AM","A.M.").replace("PM","P.M.")
    else:
        output_time =  "Sir, the time right now is "+time_tz.strftime("%I %M %p.")
        return output_time.replace("AM","A.M.").replace("PM","P.M.")
