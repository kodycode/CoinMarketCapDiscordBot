from discord.ext import commands
import json

bot = commands.Bot(command_prefix='$', description='Displays market data from https://coinmarketcap.com/')

initial_extensions = [
    'cogs.command_handler'
]


class CoinMarketBotException(Exception):
    """Exception class for CoinMarketBot"""


class CoinMarketBot:
    """Initiates the Bot"""

    def __init__(self):
        with open('config.json') as config:
            self.config_data = json.load(config)
        bot.run(self.config_data["token"])

    @bot.event
    async def on_ready():
        for extension in initial_extensions:
            try:
                bot.load_extension(extension)
                print('CoinMarketDiscordBot is online.')
            except Exception as e:
                print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))
                return

    @bot.event
    async def on_message(message):
        await bot.process_commands(message)


def main():
    try:
        CoinMarketBot()
    except Exception as e:
        print(e)


main()
