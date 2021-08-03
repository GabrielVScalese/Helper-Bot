import discord
import os
from keep_alive import keep_alive
from discord.ext import tasks
import json

client = discord.Client()

# Listas para controle de envio de aviso
sentNotices = []
sentNoticesOwner = []

# Lista para controle de usuarios num canal
usersDicts = []

# Verifica se o usuario esta no canal atual
def userExistsInCurrentUsers (userId, currentUsers):
  for user in currentUsers:
    if userId == user.id:
      return True

  return False

# Atualiza os avisos enviados, retirando um usuario dessa lista, se o mesmo estiver fora do canal
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

# Verifica se o monitor existe dentre os avisos enviados
def existsOwnerIdInNotices (ownerId, channelId):
  for sentNotice in sentNoticesOwner:
    if ownerId == sentNotice['ownerId']:
      return True
  
  return False

# Adiciona um aviso enviado a lista de avisos enviados de usuario
def addSentNotice(userId, channelId):
  global sentNotices

  try:
    sentNotice = {'userId': userId, 'channelId': channelId}
    sentNotices.append(sentNotice)
  except:
    sentNotices = []

# Adiciona um aviso enviado a lista de avisos enviados de monitor
def addSentNoticeOwner(ownerId, channelId):
  global sentNoticesOwner

  try:
    sentNoticeOwner = {'ownerId': ownerId, 'channelId': channelId}
    sentNoticesOwner.append(sentNoticeOwner)
  except:
    sentNoticeOwner = []

# Remove um aviso da lista de avisos enviados de monitor
def removeSentNoticeOwner(ownerId, channelId):
  global sentNoticesOwner

  for sentNoticeOwner in sentNoticesOwner:
    if ownerId == sentNoticeOwner['ownerId'] and channelId == sentNoticeOwner['channelId']:
      sentNoticesOwner.remove(sentNoticeOwner)

# Obter todos canais da monitoria
def fromJson():
  file = open('./channels.json')
  channels = json.load(file)

  return channels

channels = fromJson()

# Envia dm para aluno
async def sendToUser(user, title, content, thumbnail=''):
  await user.create_dm()

  embed=discord.Embed(title=title, description=content, color=discord.Color.blue())

  embed.set_author(name='Bot da Monitoria', icon_url=str(client.user.avatar_url))
  embed.set_thumbnail(url=thumbnail)
  embed.set_footer(text="Em caso de ausência ou demora, peça ajuda para outro monitor")

  await user.send(embed=embed)

# Avisa monitor sobre algum aluno com duvida
async def sendToHelper(helper, users):
  content = f'Olá **{helper.name}**! Novos alunos estão em sua monitoria.'

  stringUsers = ''
  lenMembers = 0
  for user in users:
    if user.id == helper.id:
      continue

    stringUsers += f'**{user.display_name}**, '
    lenMembers = lenMembers + 1

  stringUsers = stringUsers[:-1]
  stringUsers = stringUsers[:-1] + '.'
  
  embed=discord.Embed(title='Comunicado da Monitoria', description=content, color=discord.Color.blue())

  embed.set_author(name='Bot da Monitoria', icon_url=str(client.user.avatar_url))

  embed.add_field(name='Número de alunos', value=lenMembers, inline=True)

  embed.add_field(name="Alunos", value=stringUsers)

  await helper.create_dm()
  await helper.send(embed=embed)

@client.event
async def on_ready():
    print('Bot is running!')

## Teste

def addUsersDict (users, channelId):
  global usersDicts

  for usersDict in usersInChannel:
    if usersDict['channelId'] == channelId:
      usersDict['users'] = users
      return
  
  usersDicts.append({'channelId': channelId, 'users': users})

def findUsersDict (channelId):
  for usersDict in usersDicts:
    if usersDict['channelId'] == channelId:
      return usersDict

def lenUsersDict(channelId): 
  for usersDict in usersDicts:
    if usersDict['channelId'] == channelId:
      return len(usersDict['users'])
  
  return 0

@tasks.loop(seconds=1)
async def called_once_a_day():
  try:
    for channel in channels:
      vc = client.get_channel(id=channel['id'])

      updateSentNotices(vc.members, channel['id'])

      if len(vc.members) == 0:
        removeSentNoticeOwner(channel['owner']['id'], channel['id'])
        continue

      if not userExistsInCurrentUsers(channel['owner']['id'], vc.members):
        for user in vc.members:
          if not existsUserIdInNotices(user.id, channel['id']):
            helper = await client.fetch_user(channel['owner']['id'])
            await sendToHelper(helper, vc.members)
        
            addSentNoticeOwner(channel['owner']['id'], channel['id'])

            await sendToUser(user, 'Comunicado da Monitoria', f'Olá **{user.display_name}**! Já entrei em contato com o **monitor {helper.display_name}** e logo ele estará aqui.', helper.avatar_url)

            addSentNotice(user.id, channel['id'])

      else:
        if lenUsersDict(channel['id']) != len(vc.members):
          if vc.members[len(vc.members) - 1].id != channel['owner']['id']:
            addUsersDict(vc.members, channel['id'])
            helper = await client.fetch_user(channel['owner']['id'])
            usersDict = findUsersDict(channel['id'])
            await sendToHelper(helper, usersDict['users'])

        # removeSentNoticeOwner(channel['owner']['id'], channel['id'])

  except Exception as e:
    print(e)
    
@called_once_a_day.before_loop
async def before():
    await client.wait_until_ready()

called_once_a_day.start()
keep_alive() 
client.run(os.getenv('TOKEN'))