from discord.ext import commands
from bot_logger import logger
import json
import logging
import requests

bot = commands.Bot(command_prefix='$', description='Displays market data from https://coinmarketcap.com/')

initial_extensions = [
    'cogs.cog_manager'
]

DISCORD_BOT_URL = "https://discordbots.org/api/bots/353373501274456065/stats"
with open('config.json') as config:
    config_data = json.load(config)


class CoinMarketBotException(Exception):
    """Exception class for CoinMarketBot"""


class CoinMarketBot:
    """Initiates the Bot"""

    def __init__(self):
        bot.run(config_data["token"])

    @bot.event
    async def on_server_join(server):
        update_server_count(len(bot.servers))

    @bot.event
    async def on_server_remove(server):
        update_server_count(len(bot.servers))

    @bot.event
    async def on_ready():
        try:
            logger.info('Starting bot..')
            for extension in initial_extensions:
                bot.load_extension(extension)
            print('Bot is currently running on {} servers.'.format(len(bot.servers)))
            update_server_count(len(bot.servers))
        except Exception as e:
            error_msg = 'Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e)
            print(error_msg)
            logger.error(error_msg)

    @bot.event
    async def on_message(message):
        if not message.author.bot:
            if message.content.startswith("<@" + str(bot.user.id) + ">"):
                await bot.send_message(message.channel,
                                       "The prefix for this bot is `$`. "
                                       "Type `$help` for a list of commands.")
            else:
                await bot.process_commands(message)

    @bot.event
    async def on_command_error(error, ctx):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await send_cmd_help(ctx)
        if isinstance(error, commands.errors.BadArgument):
            await send_cmd_help(ctx)


async def send_cmd_help(ctx):
    if ctx.invoked_subcommand:
        pages = bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
        for page in pages:
            await bot.send_message(ctx.message.channel,
                                   "Please make sure you're entering a valid"
                                   "command:\n{}".format(page))
    else:
        pages = bot.formatter.format_help_for(ctx, ctx.command)
        for page in pages:
            await bot.send_message(ctx.message.channel,
                                   "Command failed. Please make sure you're "
                                   "entering the correct arguments to the "
                                   "command:\n{}".format(page))


def update_server_count(server_count):
    try:
        header = {'Authorization': '{}'.format(config_data["auth_token"])}
        payload = {'server_count': server_count}
        requests.post(DISCORD_BOT_URL,
                      headers=header,
                      data=payload)
    except:
        pass


def main():
    try:
        CoinMarketBot()
    except Exception as e:
        logging.error('Bot failed to run: {}'.format(str(e)))
        print(e)
    logger.info("Bot is now offline.")


main()
