import discord
from discord.ext import commands
import sqlite3
import random
import asyncio
from cogs import gamelist

class General(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        self.conn=sqlite3.connect('bananas.db', detect_types=sqlite3.PARSE_DECLTYPES)
        self.c=self.conn.cursor()

    ####channel grabber for future functions####
    def channelGet(self,ctx,n):
        channel = discord.utils.get(ctx.guild.text_channels, name=n)
        channel_id = channel.id
        return channel_id

    ####looking for group command####
    @commands.command(name='lfg')
    async def _lfg(self,ctx,n,p,t):
        ##convert (t)ime to floating time unit for second conversion
        tf = float(t)
        game = gamelist.gameList[n]['gameName']
        ri=gamelist.gameList[n]['role']
        gr = discord.utils.get(ctx.guild.roles,name=ri)
        max = gamelist.gameList[n]['max']
        min = gamelist.gameList[n]['min']
        ##needs floated minute for conversion for use in discordpy message sd
        ts = tf*60

        if p >= max:
            await ctx.send('Error: too many players')
        elif p<min:
            return
        else:
            message = f'{gr.mention} {ctx.author.display_name} is looking for {p} people to play {game}. React to this message to fill a spot! Message will be deleted after {t} min.'
            game_channel = self.bot.get_channel(self.channelGet(ctx,n))
            
            await game_channel.send(content=message,delete_after=ts)


    ####stop command####
    @commands.command(aliases=['disconnect','close','stopbot'])
    @commands.is_owner()
    async def logout(self,ctx):
        await ctx.send(f"Logging out")
        await self.bot.logout()

def setup(bot):
    bot.add_cog(General(bot))