import discord
from discord.ext import commands
import sqlite3
import random
import asyncio

class Currency(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        self.conn=sqlite3.connect('bananas.db', detect_types=sqlite3.PARSE_DECLTYPES)
        self.c=self.conn.cursor()
        
    ####check user balance through sql query####
    def check_balance(self,user_id):
        self.c.execute("SELECT balance FROM bananas WHERE UID=?",[user_id])
        return self.c.fetchone()[0]

    ####subtract amount from sender and add amount to target####    
    def send_balance(self,sender,target,amount):
        self.c.execute("UPDATE bananas SET balance = balance + ? WHERE UID=?",[amount,target])
        self.c.execute("UPDATE bananas SET balance = balance - ? WHERE UID=?",[amount,sender])
        self.conn.commit()
        

    ####create banana group set with command prompt alias b####    
    @commands.group(name="bananas", aliases=["b"], invoke_without_command=True)
    async def bananas(self,ctx):
        self_balance=self.check_balance(ctx.author.id)
        await ctx.send(f'You have {self_balance} bananas')
    
    ####send sub command with use cases####
    @bananas.command()
    async def send(self,ctx,targeted_user:discord.Member,amount:int):
        if ctx.author == targeted_user:
            await ctx.send("You can't send to yourself")
            return 0
        
        self_balance=self.check_balance(ctx.author.id)
        if self_balance < amount:
            await ctx.send(f"You don't have enough bananas. You currently have {self_balance}")
            return 0
            
        if amount > 0:
            self.send_balance(ctx.author.id,targeted_user.id,amount)
            await ctx.send(f"{ctx.author.mention} sent {targeted_user.mention} {amount} bananas")
        else:
            await ctx.send("Please send an amount above 0")
            
    ####request subcommand with use cases####    
    @bananas.command()
    async def request(self,ctx,targeted_user:discord.Member,amount:int):
        if ctx.author == targeted_user:
            await ctx.send("You can't request from yourself")
            return 0
        
        target_balance=self.check_balance(targeted_user.id)
        if target_balance < amount:
            await ctx.send(f"{targeted_user.nick} does not have enough bananas, they have {target_balance}")
            return 0
        ####use cases for above zero request(success)
        if amount > 0:
            async def check_response(msg):
                if(msg.content.startswith('$accept') or msg.content.startswith('deny')):
                    return True

            await ctx.send(f"{ctx.author.mention} requested {amount} from {targeted_user.mention}. Type $accept or $deny")
            print('working')

            try:
                    response_message=await self.bot.wait_for('message',timeout=20,check=check_response)
            ####handle for timeout#### 
            except asyncio.TimeoutError:
                    await ctx.send("Request timed out")

            else:
                if response_message.content.startswith('$deny'):
                    await ctx.send(f"{targeted_user.mention} denied {ctx.author.mention}'s request for {amount}")

                elif response_message.content.startswith('$accept'):
                    await ctx.send(f"{targeted_user.mention} accepted {ctx.author.mention}'s request for {amount}")
                    self.send_balance(targeted_user.id,ctx.author.id,amount) 

def setup(bot):
    bot.add_cog(Currency(bot))