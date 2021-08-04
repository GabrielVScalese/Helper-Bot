import discord
from discord.ext import tasks
import os

from keep_alive import keep_alive
from sender import Sender
from reader import Reader
from user_notice_controller import UserNoticeController
from users_channel_controller import UsersChannelController

client = discord.Client()

# Canais e Controladores
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

      if not existsInChannel(channel['owner']['id'], currentUsers):
        for user in vc.members:
          if not userNoticeController.existsUser(user.id, channel['id']):
            # helper = await client.fetch_user(channel['owner']['id'])
            helper = await client.fetch_user(580902852101406720)

            await Sender.sendToHelper(client, helper, 'Comunicado da Monitoria', f'Olá **{helper.name}**! Novos alunos estão em seu canal.', currentUsers)
      
            await Sender.sendToUser(client, user, 'Comunicado da Monitoria', f'Olá **{user.display_name}**! Já entrei em contato com o **monitor {helper.display_name}** e logo ele estará aqui.', helper.avatar_url)

            userNoticeController.addNotice(user.id, channel['id'])

      else:
        if usersChannelController.lenUsersChannel(channel['id']) != len(currentUsers):
          if currentUsers[len(currentUsers) - 1].id != channel['owner']['id']:
            usersChannelController.addUsersChannel(channel['id'], currentUsers)

            helper = await client.fetch_user(channel['owner']['id'])
            usersChannel = usersChannelController.findUsersChannel(channel['id'])
            
            await Sender.sendToHelper(client, helper, 'Comunicado da Monitoria', f'Olá **{helper.display_name}**! A lista de alunos foi atualizada.', usersChannel)

  except Exception as e:
    print(e)
    
@called_once_a_day.before_loop
async def before():
    await client.wait_until_ready()

called_once_a_day.start()
keep_alive() 
client.run(os.getenv('TOKEN'))