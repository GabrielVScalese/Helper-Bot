def existsInChannel (userId, currentUsers):
  for user in currentUsers:
    if userId == user.id:
      return True

  return False

class UserNoticeController:

  def __init__(self):
    self.notices = []

  def addNotice(self, userId, channelId):
    try:
      notice = {'userId': userId, 'channelId': channelId}

      self.notices.append(notice)
    except:
      self.notices = []

  def updateNotices (self, channelId, currentUsers):
    for notice in self.notices:
        if notice['channelId'] == channelId:
          if not existsInChannel(notice['userId'], currentUsers):
            self.notices.remove(notice)

  def existsUser(self, userId, channelId):
    for notice in self.notices:
      if userId == notice['userId']:
        return True
  
    return False

