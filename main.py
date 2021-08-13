import discord
from discord.ext import tasks
import os

from keep_alive import keep_alive
from sender import Sender
from reader import Reader
from schedules import Schedules
from user_notice_controller import UserNoticeController
from users_channel_controller import UsersChannelController

client = discord.Client()

# Channels and Controllers
channels = Reader.readJson('./channels.json')
userNoticeController = UserNoticeController()
usersChannelController = UsersChannelController()

def existsInChannel (userId, currentUsers):
  for user in currentUsers:
    if userId == user.id:
      return True

  return False

@client.event
async def on_ready():
    print('Bot is running!')

@tasks.loop(seconds=1)
async def called_once_a_day():
  try:
    for channel in channels:
      vc = client.get_channel(id=channel['id'])
      currentUsers = vc.members

      userNoticeController.updateNotices(channel['id'], currentUsers)

      if len(currentUsers) == 0:
        continue

      if Schedules.verifyNow(channel['owner']['id']):
        if not existsInChannel(channel['owner']['id'], currentUsers):
          for user in currentUsers:
            if not userNoticeController.existsUser(user.id, channel['id']):
              # helper = await client.fetch_user(channel['owner']['id'])
              helper = await client.fetch_user(580902852101406720)

              await Sender.sendEmbedToHelper(client, helper, 'Comunicado da Monitoria', f'Olá **{helper.display_name}**! Novos alunos estão em seu canal.', currentUsers)
        
              await Sender.sendEmbedToUser(client, user, 'Comunicado da Monitoria', f'Olá **{user.display_name}**! Já entrei em contato com o **monitor {helper.display_name}** e logo ele estará aqui.', helper.avatar_url)

              userNoticeController.addNotice(user.id, channel['id'])

        else:
          if usersChannelController.lenUsersChannel(channel['id']) != len(currentUsers):
            usersChannelController.addUsersChannel(channel['id'], currentUsers)

            helper = await client.fetch_user(channel['owner']['id'])
            usersChannel = usersChannelController.findUsersChannel(channel['id'])
            
            await Sender.sendEmbedToHelper(client, helper, 'Comunicado da Monitoria', f'Olá **{helper.display_name}**! A lista de alunos foi atualizada.', usersChannel)

      else:
        for user in currentUsers:
          if not userNoticeController.existsUser(user.id, channel['id']):
            if user.id != channel['owner']['id']:
              # helper = await client.fetch_user(channel['owner']['id'])
              helper = await client.fetch_user(580902852101406720)
              schedulesGroup = Schedules.findByHelper(helper, toString = True)

              await Sender.sendEmbedToUser(client, user, 'Comunicado da Monitoria', f'Infelizmente, o monitor {helper.display_name} não atende monitoria neste momento. Confira abaixo todos horários desse monitor:')

              await Sender.sendMessageToUser(client, user, f'```{schedulesGroup}```')

              userNoticeController.addNotice(user.id, channel['id'])

  except Exception as e:
    print(e)
    
@called_once_a_day.before_loop
async def before():
    await client.wait_until_ready()

called_once_a_day.start()
keep_alive() 
client.run(os.getenv('TOKEN'))