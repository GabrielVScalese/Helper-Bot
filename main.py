import discord
from discord.ext import tasks, commands
import os
from dotenv import load_dotenv

# from keep_alive import keep_alive
from sender import Sender
from reader import Reader
from schedules import Schedules
from user_notice_controller import UserNoticeController
from users_channel_controller import UsersChannelController

load_dotenv()

prefix = '!'

client = commands.Bot(command_prefix=prefix)

on = True

def isHelper (id):
  channels = Reader.readJson('./channels.json')

  if id == 580902852101406720:
    return True

  for channel in channels:
    if channel['owner']['id'] == id:
      return True
  
  return False

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
async def status(ctx, message):
  global on

  if not isHelper(ctx.message.author.id):
    return

  description = ''
  if message == 'off':
    on = False
    description = f'Meu status agora é **off**'
  elif message == 'on':
    on = True
    description = f'Meu status agora é **on**'
  else:
    description = f'Meu status não foi modificado'

  embed = discord.Embed(title='Comunicado da Monitoria', description=description, color=discord.Color.blue())

  embed.set_author(name='WALL-E', icon_url=str(client.user.avatar_url))

  await ctx.send(embed=embed)

@client.command()
async def hoje (ctx):
  if on == True:
    nowSchedules = Schedules.nowSchedules()

    await ctx.send(f'```{nowSchedules}```')

@client.event
async def on_ready():
    print('Bot is running!')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{prefix}hoje"))

@tasks.loop(seconds=5)
async def called_once_a_day():
  if on == True:
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
# keep_alive() 
client.run(os.getenv('TOKEN'))
