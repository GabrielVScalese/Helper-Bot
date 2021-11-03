import discord
from discord.ext import tasks, commands
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import pytz

from sender import Sender
from reader import Reader
from schedules import Schedules
from user_notice_controller import UserNoticeController
from users_channel_controller import UsersChannelController

load_dotenv()

prefix = '!'

client = commands.Bot(command_prefix=prefix)

on = True

def isHelper(guild, user_roles, id):
  if id == '580902852101406720' or id == '547861798846464004':
    return True

  roles = Reader.readJson('./data/roles.json')
  helper_role_id = roles[guild]
  
  for user_role in user_roles:
    if str(user_role.id) == helper_role_id:
      return True

  return False

def isHelpTime():
  utc_date = datetime.now(timezone.utc)
  BRT = pytz.timezone('Brazil/East')
  brt_time = utc_date.astimezone(BRT).isoformat()

  hour, minute = map(int, brt_time[11:16].split(':'))

  if hour > 10 and minute > 25 or hour < 22 and minute < 35:
    return True

  return False

# Channels and Controllers
channels = Reader.readJson('./data/channels.json')
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

  description = ''
  color = None
  if not isHelper(str(ctx.message.guild.id), ctx.message.author.roles, str(ctx.message.author.id)):
    description = 'Você não tem permissão para definir o status do bot!'
    color = discord.Color.red()

  else:
    if message == 'off':
      on = False
      description = f'Meu status agora é **off**'
      color = discord.Color.orange()
    elif message == 'on':
      on = True
      description = f'Meu status agora é **on**'
      color = discord.Color.green()
    else:
      description = f'Meu status não foi modificado'

  embed = discord.Embed(title='Comunicado da Monitoria', description=description, color=color)

  embed.set_author(name='WALL-E', icon_url=str(client.user.avatar_url))

  await ctx.send(embed=embed)

@client.command()
async def hoje(ctx):
  if on == True:
    nowSchedules = Schedules.nowSchedules()

    await ctx.send(f'```{nowSchedules}```')

@client.event
async def on_ready():
    print('Bot is running!')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"a monitoria com {prefix}hoje"))

@tasks.loop(seconds=5)
async def called_once_a_day():
  if on == True and isHelpTime() == True:
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
client.run(os.getenv('TOKEN'))
