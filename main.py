import discord
from discord.ext import tasks, commands
import os

from keep_alive import keep_alive
from sender import Sender
from reader import Reader
from schedules import Schedules
from user_notice_controller import UserNoticeController
from users_channel_controller import UsersChannelController

client = commands.Bot(command_prefix='!')

on = True

# Channels and Controllers
channels = Reader.readJson('./channels.json')
userNoticeController = UserNoticeController()
usersChannelController = UsersChannelController()

def existsInChannel (userId, currentUsers):
  for user in currentUsers:
    if userId == user.id:
      return True

  return False

teacherId = 692501687310483517

@client.command()
async def status(ctx):
  global on

  embed = discord.Embed(title='Comunicado da Monitoria', description='Defina meu status', color=discord.Color.blue())

  embed.set_author(name='Eve', icon_url=str(client.user.avatar_url))
  
  await ctx.send(embed=embed)

  msg = await client.wait_for("message", check=lambda message: message.author == ctx.author)

  if msg == 'off':
    on = False
  else:
    on = True

  await ctx.send('Status modificado  ✅')

@client.command()
async def hoje (ctx):
  nowSchedules = Schedules.nowSchedules()

  await ctx.send(f'```{nowSchedules}```')

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

      helper = await client.fetch_user(channel['owner']['id'])
      helperName = channel['owner']['name']

      if Schedules.verifyNow(channel['owner']['id']):
        if not existsInChannel(channel['owner']['id'], currentUsers):
          for user in currentUsers:
            if user.id != teacherId:
              if not userNoticeController.existsUser(user.id, channel['id']):
                await Sender.sendEmbedToHelper(client, helper, 'Comunicado da Monitoria', f'Olá **{helperName}**! Novos alunos estão em seu canal.', currentUsers)
          
                await Sender.sendEmbedToUser(client, user, 'Comunicado da Monitoria', f'Olá **{user.display_name}**! Já entrei em contato com o **monitor {helperName}** e logo ele estará aqui.', helper.avatar_url)

                userNoticeController.addNotice(user.id, channel['id'])

        else:
          if usersChannelController.lenUsersChannel(channel['id']) != len(currentUsers):
            usersChannelController.addUsersChannel(channel['id'], currentUsers)

            usersChannel = usersChannelController.findUsersChannel(channel['id'])
            
            await Sender.sendEmbedToHelper(client, helper, 'Comunicado da Monitoria', f'Olá **{helperName}**! A lista de alunos foi atualizada.', usersChannel)

      else:
        for user in currentUsers:
          if user.id != teacherId:
            if not userNoticeController.existsUser(user.id, channel['id']):
              if user.id != channel['owner']['id']:
                schedulesGroup = Schedules.findByHelper(helper)

                await Sender.sendEmbedToUser(client, user, 'Comunicado da Monitoria', f'Infelizmente, o **monitor {helperName}** não atende monitoria neste momento. Confira abaixo todos **horários** desse monitor:', thumbnail = helper.avatar_url)

                await Sender.sendMessageToUser(user, f'```{schedulesGroup}```')

                userNoticeController.addNotice(user.id, channel['id'])

  except Exception as e:
    print(e)
    
@called_once_a_day.before_loop
async def before():
    await client.wait_until_ready()

called_once_a_day.start()
keep_alive() 
client.run(os.getenv('TOKEN'))