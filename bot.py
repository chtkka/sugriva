import discord
intents = discord.Intents.default()
intents.members = True
from discord.ext import commands
import json
from pathlib import Path
import platform
import logging
import asyncio
import sqlite3
from cogs import gamelist

cog_list=["cogs.bananas","cogs.commands"]

print(f'Initializing bananas.db')
conn=sqlite3.connect("bananas.db",detect_types=sqlite3.PARSE_DECLTYPES)
c=conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS bananas (UID integer PRIMARY KEY, name TEXT, balance INTEGER DEFAULT 0)")

cwd = Path(__file__).parents[0]
cwd = str(cwd)
print(f"{cwd}\n-----")

secret_file = json.load(open(cwd+'/bot_config/secrets.json'))
logging.basicConfig(level=logging.INFO)

##adds intents for member grabbing
client = discord.Client(intents=intents)

class Sugriva(commands.Bot):
    ##bot setup
    def __init__(self):
        super().__init__(description="Sugriva",command_prefix="$",case_insensitive=True,pm_help=False,owner_id=201822409903439872, intents=intents)
        Sugriva.config_token = secret_file['token']
        for cog in cog_list:
            self.load_extension(cog)
            
    ##add users to database
    def monkify(self,user):
        c.execute("INSERT OR IGNORE into bananas (UID,name,balance) VALUES (?,?,?)",[user.id,user.name,100])
        conn.commit()

    ##bot info in terminal
    async def on_ready(self):
        print(f"-----\nLogged in as: {self.user.name} : {self.user.id}\n-----\nMy current prefix is: $\n-----")
        await self.change_presence(activity=discord.CustomActivity(name=f"Use $help for more info!"))
        user_list = client.users
        for x in user_list:
            self.monkify(x)
            print(x)

        #add all users to database

    async def on_message(self, message):
        if message.author != self.user: 
            pass  ####ignore self messages
        await self.process_commands(message)

    async def on_member_join(self, member):  #welcomes members and adds them to the database
        self.monkify(member)
        await member.guild.channels[1].send(f"Welcome {member.mention}")


if __name__ == "__main__":
    client=Sugriva()
    client.run(secret_file['token'])