import discord
from discord.ext import commands
from datetime import datetime as dt
import os
from ast import literal_eval

def getconfig():
    f = open("./config.json")
    data = literal_eval(f.read())
    f.close()
    return data


bot = commands.Bot(command_prefix=getconfig()["PREFIX"])
bot.remove_command("help")


@bot.event
async def on_ready():
    print(f"Starting on {len(bot.guilds)} servers")
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="over Odyssey!"))
    print(f"Started up as {bot.user.name}!")

def check(ctx):
    return ctx.author.id == 445556389532925952

@bot.command()
@commands.check(check)
async def unload(ctx, extention):
    if extention == "all":
        for cog in os.listdir("cogs"):
            if cog.endswith(".py") == True:
                extention = cog.replace(".py", "")
                try:
                    bot.unload_extension(f"cogs.{extention}")
                    print(f"Unloaded {extention} in cogs")
                    await ctx.send(f"Unloaded {extention} in cogs")
                except Exception as error:
                    print(f"Failed to unload extention {extention} in cogs:\n{error}")
                    await ctx.send(f"Failed to unload extention {extention} in cogs:\n{error}")
    else:
        try:
            bot.unload_extension(f"cogs.{extention}")
            print(f"unloaded {extention} in cogs")
            await ctx.send(f"Unloaded {extention} in cogs")
        except Exception as error:
            print(f"Failed to unload extention {extention} in cogs:\n{error}")
            await ctx.send(f"Failed to unload extention {extention} in cogs:\n{error}")

@bot.command()
@commands.check(check)
async def reload(ctx, extention):
    if extention == "all":
        for cog in os.listdir("cogs"):
            if cog.endswith(".py") == True:
                extention = cog.replace(".py", "")
                try:
                    bot.unload_extension(f"cogs.{extention}")
                    print(f"Unloaded {extention} in cogs")
                    await ctx.send(f"Unloaded {extention} in cogs")
                except Exception as error:
                    print(f"Failed to unload extention {extention} in cogs:\n{error}")
                    await ctx.send(f"Failed to unload extention {extention} in cogs:\n{error}")
    else:
        try:
            bot.unload_extension(f"cogs.{extention}")
            print(f"unloaded {extention} in cogs")
            await ctx.send(f"Unloaded {extention} in cogs")
        except Exception as error:
            print(f"Failed to unload extention {extention} in cogs:\n{error}")
            await ctx.send(f"Failed to unload extention {extention} in cogs:\n{error}")

    if extention == "all":
        for cog in os.listdir("cogs"):
            if cog.endswith(".py") == True:
                extention = cog.replace(".py", "")
                try:
                    bot.load_extension(f"cogs.{extention}")
                    print(f"Loaded {extention} in cogs")
                    await ctx.send(f"Loaded {extention} in cogs")
                except Exception as error:
                    print(f"Failed to load extention {extention} in cogs:\n{error}")
                    await ctx.send(f"Failed to load extention {extention} in cogs:\n{error}")
    else:
        try:
            bot.load_extension(f"cogs.{extention}")
            print(f"Loaded {extention} in cogs")
            await ctx.send(f"Loaded {extention} in cogs")
        except Exception as error:
            print(f"Failed to load extention {extention} in cogs:\n{error}")
            await ctx.send(f"Failed to load extention {extention} in cogs:\n{error}")



@bot.command()
@commands.check(check)
async def load(ctx, extention):
    if extention == "all":
        for cog in os.listdir("cogs"):
            if cog.endswith(".py") == True:
                extention = cog.replace(".py", "")
                try:
                    bot.load_extension(f"cogs.{extention}")
                    print(f"Loaded {extention} in cogs")
                    await ctx.send(f"Loaded {extention} in cogs")
                except Exception as error:
                    print(f"Failed to load extention {extention} in cogs:\n{error}")
                    await ctx.send(f"Failed to load extention {extention} in cogs:\n{error}")
    else:
        try:
            bot.load_extension(f"cogs.{extention}")
            print(f"Loaded {extention} in cogs")
            await ctx.send(f"Loaded {extention} in cogs")
        except Exception as error:
            print(f"Failed to load extention {extention} in cogs:\n{error}")
            await ctx.send(f"Failed to load extention {extention} in cogs:\n{error}")




if __name__ == "__main__":

    print("Loading extentions")

    for cog in os.listdir("cogs"):
        if cog.endswith(".py") == True:
            extention = cog.replace(".py", "")
            try:
                bot.load_extension(f"cogs.{extention}")
                print(f"Loaded {extention} in cogs")
            except Exception as error:
                print(f"Failed to load extention {extention} in cogs:\n{error}")

    bot.run(getconfig()["TOKEN"])