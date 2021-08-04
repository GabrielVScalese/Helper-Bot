import datetime
import pytz

class Schedules:

  @staticmethod
  def verifyNow (helperId):
    tz = pytz.timezone('America/Sao_Paulo')
    nowDate = datetime.datetime.now(tz)

    channels = []
    for channel in channels:
      if channel['id'] == helperId:
        for day in channel['days']:
          if nowDate.strftime("%A") == day['day']:
            for schedule in day['schedules']:
              startHour = int(schedule['start'].split(':')[0])
              startMinute = int(schedule['start'].split(':')[1])

              startTime = nowDate.replace(hour=startHour, minute=startMinute, second = 0, microsecond = 0)

              endHour = int(schedule['end'].split(':')[0])
              endMinute = int(schedule['end'].split(':')[1])
        
              endTime = nowDate.replace(hour=endHour, minute=endMinute, second = 0, microsecond = 0)

              if (nowDate >= startTime):
                if (nowDate <= endTime):
                  return True
              
              return False
        
    return False