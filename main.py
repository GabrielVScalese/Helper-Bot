import discord
import os
from keep_alive import keep_alive
from discord.ext import tasks
import json

client = discord.Client()

# Listas para controle de envio de aviso
sentNotices = []
sentNoticesOwner = []

# Verifica se o usuario esta no canal atual
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
  # Lista atingiu o maximo
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

# Envia dm para o monitor ou aluno
async def sendToUser(user, title, content, thumbnail=''):
  await user.create_dm()

  embed=discord.Embed(title=title, description=content, color=discord.Color.blue())

  embed.set_author(name='Bot da Monitoria', icon_url=str(client.user.avatar_url))
  embed.set_thumbnail(url=thumbnail)
  embed.set_footer(text="Em caso de ausência ou demora, peça ajuda para outro monitor")

  await user.send(embed=embed)

# Verifica se o canal tem monitor
def callContainsHelper(helperId, members):
  for member in members:
    if helperId == member.id:
      return True

  return False

# Avisa monitor sobre algum aluno com duvida
async def sendToHelper(helper, members):
  content = f'Olá **{helper.name}**! Novos alunos estão em sua monitoria.'

  string_members = ''
  for i in range(0, len(members)):
    if i != len(members) - 1:
      string_members += f'**{members[i].name}**, '
    else:
      string_members += f'**{members[i].name}**.'

    i = i + 1

  embed=discord.Embed(title='Comunicado da Monitoria', description=content, color=discord.Color.blue())

  embed.set_author(name='Bot da Monitoria', icon_url=str(client.user.avatar_url))

  embed.add_field(name='Número de alunos', value=len(members), inline=True)

  embed.add_field(name="Alunos", value=string_members)

  await helper.create_dm()
  await helper.send(embed=embed)

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
        if not existsOwnerIdInNotices(channel['owner']['id'], channel['id']):
          helper = await client.fetch_user(580902852101406720) # Provisorio
          # helper = await client.fetch_user(channel['owner']['id']) -> Original
          await sendToHelper(helper, vc.members)
          
          addSentNoticeOwner(channel['owner']['id'], channel['id'])

        for member in vc.members:
          if not existsUserIdInNotices(member.id, channel['id']):
            await sendToUser(member, 'Comunicado da Monitoria', f'Olá **{member.name}**! Já entrei em contato com o **monitor {helper.name}** e logo ele estará aqui.', helper.avatar_url)

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