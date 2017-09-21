from discord.ext import commands
import json

bot = commands.Bot(command_prefix='$', description='Displays market data from https://coinmarketcap.com/')

initial_extensions = [
    'cogs.coin_market'
]


class CoinMarketBotException(Exception):
    '''Exception class for CoinMarketBot'''


class CoinMarketBot:
    '''Initiates the Bot'''

    def __init__(self, token):
        bot.run(token)

    @bot.async_event
    async def on_ready():
        for extension in initial_extensions:
            try:
                bot.load_extension(extension)
                print('CoinMarketDiscordBot is online.')
            except Exception as e:
                CoinMarketBotException('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))
                return

    @bot.event
    async def on_message(message):
        await bot.process_commands(message)

    @bot.on_error
    async def on_error(error):
        pass


def main():
    try:
        config_file = open('config.json')
        config_str = config_file.read()
        config_data = json.loads(config_str)
        token = config_data['token']
        CoinMarketBot(token)
    except Exception as e:
        print(e)


main()
