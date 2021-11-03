import datetime
import pytz
from reader import Reader

def convertToDate (timeString):
  tz = pytz.timezone('America/Sao_Paulo')
  hour = int(timeString.split(':')[0])
  minute = int(timeString.split(':')[1])
  
  nowDate = datetime.datetime.now(tz)
  newDate = nowDate.replace(hour=hour, minute=minute, second=0, microsecond=0)

  return newDate

def convertToString(schedulesGroup):
  toString = ''
  
  for day in schedulesGroup:
    toString += f'\n {day["day"]}:\n'
    for schedule in day['schedules']:
      toString += f'\tdas {schedule["start"]} até {schedule["end"]} \n'

  return toString

class Schedules:

  @staticmethod
  def verifyNow (helperId):
    tz = pytz.timezone('America/Sao_Paulo')
    nowDate = datetime.datetime.now(tz)
    
    channels = Reader.readJson('./data/channels.json')
    for channel in channels:
      if channel['owner']['id'] == helperId:
        for day in channel['owner']['days']:
          if nowDate.strftime("%A") == day['day']:
            for schedule in day['schedules']:
              startDate = convertToDate(schedule['start'])
              endDate = convertToDate(schedule['end'])

              if (nowDate >= startDate):
                if (nowDate <= endDate):
                  return True
                      
    return False
  
  @staticmethod
  def findByHelper (helper):
    schedulesGroup = []

    channels = Reader.readJson('./data/channels.json')
    for channel in channels:
      if channel['owner']['id'] == helper.id:
        for day in channel['owner']['days']:
          dayToAdd = {'day': day['day'], 'schedules': []}
          for schedule in day['schedules']:
            dayToAdd['schedules'].append({'start': schedule['start'], 'end': schedule['end']})
            
          schedulesGroup.append(dayToAdd)
    
  
    return convertToString(schedulesGroup)

  @staticmethod
  def nowSchedules ():
    tz = pytz.timezone('America/Sao_Paulo')
    nowDate = datetime.datetime.now(tz)

    toString = '+ Monitorias hoje: \n'
    channels = Reader.readJson('./data/channels.json')
    
    for channel in channels:
      for day in channel['owner']['days']:
        if day['day'] == nowDate.strftime("%A"):
          toString += f'\n{channel["owner"]["name"]}:\n'
          for schedule in day['schedules']:
            toString += f'\tdas {schedule["start"]} até {schedule["end"]}\n'
    
    if toString == '+ Monitorias hoje: \n':
      return 'Não há monitorias hoje'
    
    return toString
