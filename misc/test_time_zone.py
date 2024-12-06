import datetime
from zoneinfo import ZoneInfo

now = datetime.datetime.now().astimezone(tz=ZoneInfo("Australia/Sydney"))

for dayNo in range(0, 365):
    now = now + datetime.timedelta(days=1)
    print(str(now.hour) + ":" + str(now.minute) + " ")
    print("--" + str(now.dst()))