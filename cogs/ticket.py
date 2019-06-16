import discord
from discord.ext import commands
import pymongo
import json, asyncio
from datetime import datetime as dt
dbclient = pymongo.MongoClient("mongodb://localhost:27017/")

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        f = open("./config.json", "r")
        data = json.loads(f.read())
        f.close()
        self.c = data
    
    async def get_ticket_number(self, user):
        db = dbclient["o-ticket-num"]
        listcols = db.list_collection_names()

        if "num" in listcols:
            col = db["num"]
            z = col.find_one()
            x = int(z["new"])
            y = int(x + 1)
            numdata = {
                "new": y,
                "old": x
            }
            col.delete_many({})
            col.insert_one(numdata)
        else:
            col = db["num"]
            x = int(1)
            y = int(2)
            numdata = {
                "new": y,
                "old": x
            }
            col.insert_one(numdata)
        return x

    async def get_category(self, user, channel):
        embed=discord.Embed(title=":arrows_counterclockwise: Processing...", color=discord.Color.blue())
        m = await channel.send(embed=embed)
        embed=discord.Embed(title="Choose one of these categories", description="To open a ticket choose a category", color=discord.Color.green())
        for cat in self.c["CATS"]:
            e = cat["emoji"]
            n = cat["name"]
            d = cat["desc"]
            embed.add_field(name=f"{e} {n}", value=str(d))
            await m.add_reaction(e)
        await m.edit(embed=embed)
        def check(r, u):
            for cat in self.c["CATS"]:
                e = cat["emoji"]

                if str(r.emoji) == e:
                    return r.message.id == m.id and user.id == u.id
            return False

        r, u = await self.bot.wait_for("reaction_add", check=check)
        for cat in self.c["CATS"]:
            e = cat["emoji"]
            if r.emoji == e:
                return cat, m
        raise "No good :o"

    async def ping_support_team(self, ticket, user):
        await self.bot.get_channel(589696723673284638).send(content="<@&556471825513840640>", embed=discord.Embed(title="Support needed!", description=f"**{user.name}** needs your help in {ticket.mention}!", colour=discord.Colour.blue(), timestamp=dt.utcnow()))
        await ticket.send(embed=discord.Embed(title="We have told the support team to help you out!", description="Please wait untill we get here."))

    async def create_ticket_channel(self, user, channel, reason, cat, num, m:discord.Message):
        cname = cat["name"]
        cdesc = cat["desc"]
        cemoji = cat["emoji"] 
        staffrole = channel.guild.get_role(self.c["ROLE"])
        t = await channel.guild.create_text_channel(f"ticket-{num}", category=self.bot.get_channel(cat["cat"]), overwrites = {
        channel.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        channel.guild.me: discord.PermissionOverwrite(read_messages=True),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        staffrole: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True)
        }, topic=f"Ticket from {user} opened with reason {reason} in category {cname} ({cdesc})")
        await m.edit(embed=discord.Embed(colour=discord.Colour.blue(), title="Your ticket has been created", description=f"View it in {t.mention}"))
        await m.clear_reactions()
        self.save_data(t, user, cat, reason)
        if cat["name"] == "Order from us.":
            m = await t.send(embed=discord.Embed(color=discord.Color.green(), title=f"Welcome to your private ticket {user.name}", description="Please wait until we assist you further!").add_field(name="Order:", value=f"{reason}").add_field(name="Lets get started!", value="Choose one of these options to get started.\n\n**🤖 Answer the bots questions**\n\n**🤵 Talk to our support team**", inline=False))
            await m.add_reaction("🤖")
            await m.add_reaction("🤵")
            def check(r, u):
                return r.message.id == m.id and u.id == user.id and (str(r.emoji) == "🤵" or str(r.emoji) == "🤖")
            r, u = await self.bot.wait_for("reaction_add", check=check)
            if str(r.emoji) == "🤵":
                await self.ping_support_team(t, user)
            elif str(r.emoji) == "🤖":
                await self.get_commission_info(user, t, t)

        elif cat["name"] == "Apply":
            return t
        else:
            await t.send("Unknown")
        return t

    def save_data(self, ticket, user, category, reason):
        data = {
            "user":user.id,
            "ticket": ticket.id,
            "cat": category,
            "reason" : reason,
            "closed" : False
        }
        db = dbclient["o-ticket-data"]
        col = db[str(ticket.id)]
        col.insert_one(data)

        col = db[str(ticket.name)]
        col.insert_one(data)

    @commands.command()
    async def new(self, ctx,*, x="No given reason"):
        num = await self.get_ticket_number(ctx.author)
        cat, m = await self.get_category(ctx.author, ctx.channel)
        t = await self.create_ticket_channel(ctx.author, ctx.channel, x, cat, num, m)


    @commands.group()
    async def ticket(self, ctx):
        if ctx.invoked_subcommand == None:
            await ctx.send(embed=discord.Embed(colour=discord.Colour.red(), title="Invalid usage!", description=f"Please use a subcommand or `-new` to create a ticket"))
            return



    @ticket.command()
    async def add(self, ctx, user:discord.Member = None):
        if user == None:
            await ctx.send(embed=discord.Embed(colour=discord.Colour.red(), title="Invalid user!", description=f"Correct usage: `-ticket add <@user#1234>`"))
        else:
            db = dbclient["o-ticket-data"]
            l = db.list_collection_names()
            if str(ctx.channel.id) in l:
                col = db[str(ctx.channel.id)]
                x = col.find_one()
                await ctx.channel.set_permissions(user, read_messages=True, send_messages=True)
                await ctx.send(embed=discord.Embed(title=f"{user} has been added!", description="This user is now part of this ticket."))
            else:
                await ctx.send(embed=discord.Embed(colour=discord.Colour.red(), title="Not a ticket!", description=f"This is not a ticket!"))


    @ticket.command()
    async def remove(self, ctx, user:discord.Member = None):
        if user == None:
            await ctx.send(embed=discord.Embed(colour=discord.Colour.red(), title="Invalid user!", description=f"Correct usage: `-ticket remove <@user#1234>`"))
        else:
            db = dbclient["o-ticket-data"]
            l = db.list_collection_names()
            if str(ctx.channel.id) in l:
                await ctx.channel.set_permissions(user, read_messages=False, send_messages=False)
                await ctx.send(embed=discord.Embed(title=f"{user} has been removed!", description="This user is no longer part of this ticket."))
            else:
                await ctx.send(embed=discord.Embed(colour=discord.Colour.red(), title="Not a ticket!", description=f"This is not a ticket!"))

    @ticket.command()
    async def stats(self, ctx):
        db = dbclient["o-ticket-data"]
        l = db.list_collection_names()
        if str(ctx.channel.id) in l:
            x = db[str(ctx.channel.id)]
            d = x.find_one()
            c = self.bot.get_channel(d["ticket"])
            u = ctx.guild.get_member(d["user"])
            cat = d["cat"]
            cname = cat["name"]
            cdesc = cat["desc"]
            cemoji = cat["emoji"] 
            o = 0
            reason = d["reason"]
            async for m in c.history(limit=1000000):
                o += 1
            embed = discord.Embed(title="Ticket stats", description="These are the stats from the tickets")
            embed.add_field(name="Reason:", value=f"{cemoji} {cname}: {reason}")
            embed.add_field(name="Messages sent:", value=f"{o} messages.")
            embed.add_field(name="Ticket owner:", value=f"{u.mention} ({u.id})")
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=discord.Embed(colour=discord.Colour.red(), title="Not a ticket!", description=f"This is not a ticket!"))

    @ticket.command()
    async def close(self, ctx, *, r="No given reason."):
        db = dbclient["o-ticket-data"]
        ticket = ctx.channel
        if str(ticket.id) in db.list_collection_names():

            col = db[str(ticket.id)]
            d = col.find_one()
            col.delete_many({})
            data = {
                "user":d["user"],
                "ticket": d["ticket"],
                "cat": d["cat"],
                "reason" : d["reason"],
                "closed" : True
            }
            db = dbclient["o-ticket-data"]
            col = db[str(ticket.id)]
            col.insert_one(data)

            col = db[str(ticket.name)]
            col.insert_one(data)
            x = db[str(ctx.channel.id)]
            d = x.find_one()
            c = self.bot.get_channel(d["ticket"])
            u = ctx.guild.get_member(d["user"])
            cat = d["cat"]
            cname = cat["name"]
            cdesc = cat["desc"]
            cemoji = cat["emoji"] 
            o = 0
            reason = d["reason"]
            x = f"Welcome to #{ticket.name}! Reason: {reason}"
            async for m in ctx.channel.history(limit=1000000, oldest_first=True):
                if m.content == "" or m.content == None:
                    try:
                        x = f"{x}\n{m.author}: {m.embeds[0].title}"
                        try:
                            x = f"{x} {m.embeds[0].description}"
                            try:
                                x = f"{x} {m.embeds[0].feilds[0].name}"
                                x = f"{x} {m.embeds[0].feilds[0].value}"
                            except:
                                pass
                        except:
                            pass
                    except:
                        pass
                else:
                    x = f"{x}\n{m.author}: {m.content}"
                o += 1
            
            embed = discord.Embed(title="Ticket closed", colour=discord.Colour.red())
            embed.add_field(name="Ticket:", value=f"{ctx.channel.name} ({ctx.channel.id})")
            embed.add_field(name="Closed by:", value=f"{ctx.author.mention} ({ctx.author.id})")
            embed.add_field(name="Reason:", value=f"{reason}")
            embed.add_field(name="Messages sent:", value=f"{o} messages.")
            embed.add_field(name="Ticket owner:", value=f"{u.mention} ({u.id})")
            embed.add_field(name="Close reason:", value=f"{r}")

            await self.bot.get_channel(self.c["log-channel"]).send(embed=embed)
            x = f"{x}\nClosed by {ctx.author} with reason: {r}"
            f = open(f"./logs/{ctx.channel.id}.txt", "w")
            f.write(str(x))
            f.close()

            await self.bot.get_channel(self.c["log-channel"]).send(file=discord.File(fp=f"./logs/{ctx.channel.id}.txt"))
            await ctx.channel.delete()
        else:
            await ctx.send(embed=discord.Embed(title="Not a ticket", description="This is not a ticket", colour=discord.Colour.red()))
    

    @ticket.command()
    async def logs(self, ctx):
        db = dbclient["o-ticket-data"]
        ticket = ctx.channel
        if str(ticket.id) in db.list_collection_names():
            col = db[str(ticket.id)]
            d = col.find_one()
            reason = d["reason"]
            x = f"Welcome to #{ticket.name}! Reason: {reason}"
            async for m in ctx.channel.history(limit=1000000, oldest_first=True):
                if m.content == "" or m.content == None:
                    try:
                        x = f"{x}\n{m.author}: {m.embeds[0].title}"
                        try:
                            x = f"{x} {m.embeds[0].description}"
                            try:
                                x = f"{x} {m.embeds[0].feilds[0].name}"
                                x = f"{x} {m.embeds[0].feilds[0].value}"
                            except:
                                pass
                        except:
                            pass
                    except:
                        pass
                else:
                    x = f"{x}\n{m.author}: {m.content}"
                
            f = open(f"./logs/{ctx.channel.id}.txt", "w")
            f.write(str(x))
            f.close()

            await ctx.send(file=discord.File(fp=f"./logs/{ctx.channel.id}.txt"))

        else:
            await ctx.send(embed=discord.Embed(title="Not a ticket", description="This is not a ticket", colour=discord.Colour.red()))


    async def get_ticket_info(self, ticket):
        db = dbclient["o-ticket-data"]
        col = db[str(ticket.id)] or db[str(ticket.name)]
        return col.find_one()

    async def get_role_by_reaction(self, user, channelin, title, desc):
        desc = desc + "\n"
        items = [{'text': '📹 Animator', 'roleid': 577070012456763392, 'emoji': '📹'}, {'text': '🤖 Bot developer', 'roleid': 526337367020404747, 'emoji': '🤖'}, {'text': '🏛 Builder', 'roleid': 526762240481820672, 'emoji': '🏛'}, {'text': '💬 Discord Server Setup', 'roleid': 560216937045688320, 'emoji': '💬'}, {'text': '🖌 Graphics Designer', 'roleid': 526568306597953557, 'emoji': '🖌'}, {'text': '🔧 Java Developer', 'roleid': 560217765210750976, 'emoji': '🔧'}, {'text': '🛠 Minecraft Server Setup', 'roleid': 526341195803394058, 'emoji': '🛠'}, {'text': '💻 Web Design', 'roleid': 479193617773232129, 'emoji': '💻'}, {'text': '🖥 Web Development', 'roleid': 479193618222153729, 'emoji': '🖥'}, {'text': '🔌 Plugin Development', 'roleid': 479194063577284619, 'emoji': '🔌'}, {'text': '🎮 Java Development', 'roleid': 479194064525197313, 'emoji': '🎮'}, {'text': '🤖 Bot Development', 'roleid': 479194066224021534, 'emoji': '🤖'}, {'text': '📁 Configuration', 'roleid': 479194093520683023, 'emoji': '📁'}, {'text': '🏛 Building', 'roleid': 479194277373804546, 'emoji': '🏛'}, {'text': '🏔 Terraforming', 'roleid': 479194275658203137, 'emoji': '🏔'}, {'text': '🔧 System Administration', 'roleid': 479194089875832833, 'emoji': '🔧'}]
        embed = discord.Embed(title=":arrows_counterclockwise: Processing...")
        msg = await channelin.send(embed = embed)
        for item in items:
            text = item["text"]
            desc = f"""
            {desc}
            **{text}**
            """
            await msg.add_reaction(item["emoji"])
        embed = discord.Embed(title=title, description=desc)
        await msg.edit(embed=embed)
        r = None
        while r == None:
            def check(r, u):
                print(str(bool(r.message.id == msg.id)) + str(bool(user.id == u.id)) + f"{r.message.id} and {msg.id} and {user.id} and {u.id}")
                return r.message.id == msg.id and user.id == u.id
            reaction, u = await self.bot.wait_for("reaction_add", check=check)
            r = None
            for i in items:
                if i["emoji"] == str(reaction.emoji):
                    r = channelin.guild.get_role(i["roleid"])
            if r == None:
                embed = discord.Embed(title="❌ Invalid option.", description="Choose one of the options listed above, try again")
                await channelin.send(embed=embed, delete_after=3)
        return r


    async def get_commission_info(self, author, channel, ticket):
        role = await self.get_role_by_reaction(channel, author, "Choose a category for this ticket", "Please choose one of the options bellow to let your commission be posted!")
        def check(m):
            return m.author == author and m.channel == channel
        await channel.send(embed=discord.Embed(title="What should the name of this ticket be?", description="A breif summary of what you need eg: Sheep Spawner Plugin"))
    
        title = await self.bot.wait_for("message", check=check)
        await channel.send(embed=discord.Embed(title="Please Provide an in-depth description of your request.", description="All details we will need to create your product. Include images using links \n(such as [imgur](https://imgur.com/) or [gyazo](https://gyazo.com/) Note: *we are in no way affiliated with these.*"))
    
        description = await self.bot.wait_for("message", check=check)
        await channel.send(embed=discord.Embed(title="What is your timeframe?", description="How long it should take for us to complete your product."))
    
        timeframe = await self.bot.wait_for("message", check=check)
        def check2(r, u):
            return r.message.id == m.id and u.id == user.id and (str(r.emoji) == "💰" or str(r.emoji) == "❓")
        m = await channel.send(embed=discord.Embed(title="Budget and Quotes", description="Choose an option below to allow quotes or freelancers to come to your ticket:\n\n**💰 Set a budget**\n\n**❓ Ask our freelancers**"))
    
        r, u = await self.bot.wait_for("reaction_add", check=check2)
        if str(r.emoji) == "💰":
            await self.post_commission()
        return


    @commands.command()
    @commands.has_any_role("Support")
    async def post(self, ctx, ticket:discord.TextChannel):
        db = dbclient["o-ticket-data"]
        if str(ticket.id) in db.list_collection_names():
            data = self.get_ticket_info(ticket)
            await self.get_commission_info(ctx.author, ctx.channel, ticket)
            await self.post_commission(ticket)
        else:
            await ctx.send(embed=discord.Embed(title="Invalid Ticket", description="The specified channel is not a ticket."))


def setup(bot):
    bot.add_cog(Ticket(bot))