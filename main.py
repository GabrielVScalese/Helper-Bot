import discord
import os
from keep_alive import keep_alive
from discord.ext import tasks
import json

client = discord.Client()

sentNotices = []
sentNoticesOwner = []

# Verifica se o usuario esta na call atual
def userExistsInCurrentUsers (userId, currentUsers):
  for user in currentUsers:
    if userId == user.id:
      return True

  return False

# Atualiza os avisos enviados, retirando um usuario dessa lista, se o mesmo estiver fora da call
def updateSentNotices (currentUsers, channelId):
  global sentNotices

  for sentNotice in sentNotices:
      if sentNotice['channelId'] == channelId:
        if not userExistsInCurrentUsers(sentNotice['userId'], currentUsers):
          sentNotices.remove(sentNotice)

# Verifica se o usuario existe dentre os avisos enviados
def existsUserIdInNotices(userId, channelId):
  for sentNotice in sentNotices:
    if userId == sentNotice['userId'] and channelId == sentNotice['channelId']:
      return True
  
  return False

def existsOwnerIdInNotices (ownerId, channelId):
  for sentNotice in sentNoticesOwner:
    if ownerId == sentNotice['ownerId']:
      return True
  
  return False

# Adiciona um aviso enviado a lista de avisos enviados
def addSentNotice(userId, channelId):
  global sentNotices

  try:
    sentNotice = {'userId': userId, 'channelId': channelId}
    sentNotices.append(sentNotice)
  # Lista atingiu o maximo
  except:
    sentNotices = []

def addSentNoticeOwner(ownerId, channelId):
  global sentNoticesOwner

  try:
    sentNoticeOwner = {'ownerId': ownerId, 'channelId': channelId}
    sentNoticesOwner.append(sentNoticeOwner)
  except:
    sentNoticeOwner = []

def removeSentNoticeOwner(ownerId, channelId):
  global sentNoticesOwner

  for sentNoticeOwner in sentNoticesOwner:
    if ownerId == sentNoticeOwner['ownerId'] and channelId == sentNoticeOwner['channelId']:
      sentNoticesOwner.remove(sentNoticeOwner)

def fromJson():
  file = open('./channels.json')
  channels = json.load(file)

  return channels

channels = fromJson()

# Envia dm para o monitor ou aluno
async def sendDm(user, title, content, thumbnail=''):
  await user.create_dm()

  embed=discord.Embed(title=title, description=content, color=discord.Color.blue())

  embed.set_author(name='Bot da Monitoria', icon_url=str(client.user.avatar_url))
  embed.set_thumbnail(url=thumbnail)

  await user.send(embed=embed)

# Verifica se a call tem monitor
def callContainsHelper(helperId, members):
  for member in members:
    if helperId == member.id:
      return True

  return False

# Avisa monitor sobre algum aluno com duvida
async def sendToHelper(helper, members):
  content = f'Olá **{helper.name}**! Existe(m) {len(members)} pessoa(s) esperando sua monitoria: '

  string_members = ''
  for i in range(0, len(members)):
    if i != len(members) - 1:
      string_members += f'**{members[i].name}**, '
    else:
      string_members += f'**{members[i].name}**'

    i = i + 1

  content += string_members
  await sendDm(helper, 'Comunicado da Monitoria', content)

@client.event
async def on_ready():
    print('Bot is running!')

@tasks.loop(seconds=1)
async def called_once_a_day():
  try:
    for channel in channels:
      vc = client.get_channel(id=channel['id'])

      updateSentNotices(vc.members, channel['id'])

      if len(vc.members) == 0:
        removeSentNoticeOwner(channel['owner']['id'], channel['id'])
        continue

      if not callContainsHelper(channel['owner']['id'], vc.members):
        # helper = await client.fetch_user(channel['owner']['id'])

        if not existsOwnerIdInNotices(channel['owner']['id'], channel['id']):
          addSentNoticeOwner(channel['owner']['id'], channel['id'])
          helper = await client.fetch_user(580902852101406720)
          await sendToHelper(helper, vc.members)

        for member in vc.members:
          if not existsUserIdInNotices(member.id, channel['id']):
            # await sendDm(member, 'Comunicado da Monitoria', f'Olá **{member.name}**! Já entrei em contato com o **monitor {helper.name}** e logo ele estará aqui.', helper.avatar_url)

            addSentNotice(member.id, channel['id'])

      else:
        removeSentNoticeOwner(channel['owner']['id'], channel['id'])
        print('Helper is on')

  except Exception as e:
    print(e)
    
@called_once_a_day.before_loop
async def before():
    await client.wait_until_ready()

called_once_a_day.start()
keep_alive() 
client.run(os.getenv('TOKEN'))