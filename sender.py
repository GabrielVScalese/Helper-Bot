import discord

class Sender:

  @staticmethod
  async def sendEmbedToUser(client, user, title, content, thumbnail = ''):
    await user.create_dm()

    embed = discord.Embed(title=title, description=content, color=discord.Color.blue())

    embed.set_author(name='Bot da Monitoria', icon_url=str(client.user.avatar_url))

    embed.set_thumbnail(url=thumbnail)

    await user.send(embed=embed)
  
  @staticmethod
  async def sendMessageToUser (user, content):
    await user.create_dm()

    await user.send(content)

  @staticmethod
  async def sendEmbedToHelper(client, helper, title, content, users):
    stringUsers = ''
    lenMembers = 0
    
    for user in users:
      if user.id == helper.id:
        continue

      stringUsers += f'**{user.display_name}**, '
      lenMembers = lenMembers + 1

    stringUsers = stringUsers[:-1]
    stringUsers = stringUsers[:-1] + '.'
    
    embed=discord.Embed(title=title, description=content, color=discord.Color.blue())

    embed.set_author(name='Bot da Monitoria', icon_url=str(client.user.avatar_url))

    embed.add_field(name='Número de alunos', value=lenMembers, inline=True)

    embed.add_field(name="Alunos", value=stringUsers)

    await helper.create_dm()
    await helper.send(embed=embed)