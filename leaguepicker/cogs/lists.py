from discord.ext import commands
from cogs.helper import send_embed

class Lists(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='lists', help='Get more information about creating and storing lists.')
    async def info_lists(self, ctx):
        await ctx.send('''```\nLists are a powerful way to randomly pick from the champs you like to play.\nCreate a list with any Roll command using the --from=[] flag. List a set of champions (separated by commas) between the brackets.\n\nLike --from=[morg,rat,lux,kha,voli] to pick from Morgana, Teemo, Lux, Kha'Zix, and Volibear.\nI'll DM you if I'm uncertain on what a champion means, and if worst comes to worst, I'll ignore it.\n\nYou can save a list for future use by specifying --as=listName. Lists are saved to your Discord ID, so your lists will be stored separately from everyone else's.\n\nFor example, ~roll --from=[teemo,shaco,eve,khazix,vayne,kaisa,pyke,senna,twitch] --as=invisibles will save the list as "invisibles". Then, next time, I just ~roll --as=invisibles to load from the stored list.\n```\n```fix\nNote that if you name a list the same thing as an existing list, the existing list will be overwritten, so be careful!\n```''')
