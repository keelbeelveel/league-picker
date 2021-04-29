import sys,os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),os.pardir))

from cogs.rolls import Rolls
from cogs.lists import Lists
bot_cogs = []
bot_cogs.append(Rolls)
bot_cogs.append(Lists)
