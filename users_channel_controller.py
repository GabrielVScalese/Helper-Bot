class UsersChannelController:

  def __init__(self):
    self.usersChannels = []

  def addUsersChannel (self, channelId, users):
    try:
      for usersChannel in self.usersChannels:
        if usersChannel['channelId'] == channelId:
          usersChannel['users'] = users
          return
      
      self.usersChannels.append({'channelId': channelId, 'users': users})
    except:
      self.usersChannels = []
      self.usersChannels.append({'channelId': channelId, 'users': users})
  
  def findUsersChannel (self, channelId):
    for usersChannel in self.usersChannels:
      if usersChannel['channelId'] == channelId:
        return usersChannel['users']

    return []

  def lenUsersChannel(self, channelId): 
    return len(self.findUsersChannel(channelId))