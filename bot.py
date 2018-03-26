from discord.ext import commands
from bot_logger import logger
import json
import logging
import requests

CMB_ADMIN = "CMB ADMIN"
PREFIX_DISABLED = "PREFIX_DISABLED"
DISCORD_BOT_URL = "https://discordbots.org/api/bots/353373501274456065/stats"
COG_MANAGER = "cogs.cog_manager"
with open('config.json') as config:
    config_data = json.load(config)
bot = commands.Bot(command_prefix=config_data["cmd_prefix"],
                   description="Displays market data from "
                               "https://coinmarketcap.com/")


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
            bot.load_extension(COG_MANAGER)
            update_server_count(len(bot.servers))
        except Exception as e:
            error_msg = 'Failed to load cog manager\n{}: {}'.format(type(e).__name__, e)
            print(error_msg)
            logger.error(error_msg)

    @bot.event
    async def on_message(message):
        if not message.author.bot:
            if message.content.startswith("<@" + str(bot.user.id) + ">"):
                try:
                    if message.server.id in prefix_list:
                        await bot.send_message(message.channel,
                                               "The prefix for this bot is `{0}`. "
                                               "Type `{0}help` for a list of commands."
                                               "".format(prefix_list[message.server.id]))
                    else:
                        await bot.send_message(message.channel,
                                               "The prefix for this bot is `{0}`. "
                                               "Type `{0}help` for a list of commands."
                                               "".format(config_data["cmd_prefix"]))
                except AttributeError:
                    await bot.send_message(message.channel,
                                           "The prefix for this bot is `{0}`. "
                                           "Type `{0}help` for a list of commands."
                                           "".format(config_data["cmd_prefix"]))
            else:
                try:
                    if message.server.id in prefix_list:
                        server_prefix = prefix_list[message.server.id]
                        if message.content.startswith(config_data["cmd_prefix"]):
                            if config_data["cmd_prefix"] != server_prefix:
                                return
                        message.content = message.content.replace(server_prefix,
                                                                  config_data["cmd_prefix"],
                                                                  1)
                    await process_cmd(message)
                except AttributeError:
                    await process_cmd(message)

    @bot.event
    async def on_command_error(error, ctx):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await send_cmd_help(ctx)
        if isinstance(error, commands.errors.BadArgument):
            await send_cmd_help(ctx)


async def process_cmd(message):
    """
    Processes command
    """
    if message.content.startswith(config_data["cmd_prefix"]):
        cmd_input = message.content[1:].split(' ')
        if cmd_input[0] not in bot.commands:
            if cmd_input[0] != '':
                cmd_input.insert(0, "{}s".format(config_data["cmd_prefix"]))
                message.content = ' '.join(cmd_input)
        await bot.process_commands(message)


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


def save_prefix_file(prefix_data={}, backup=False):
    """
    Saves prefixes.json file
    """
    if backup:
        prefix_filename = "prefixes_backup.json"
    else:
        prefix_filename = "prefixes.json"
    with open(prefix_filename, 'w') as outfile:
        json.dump(prefix_data,
                  outfile,
                  indent=4)


def check_prefix_file():
    """
    Checks to see if there's a valid prefixes.json file
    """
    try:
        with open('prefixes.json') as prefixes:
            return json.load(prefixes)
    except FileNotFoundError:
        save_prefix_file()
        return json.loads('{}')
    except Exception as e:
        print("An error has occured. See error.log.")
        logger.error("Exception: {}".format(str(e)))


def _check_permission(ctx):
    """
    Checks if user contains the correct permissions to use these
    commands
    """
    try:
        with open('server_settings.json') as settings:
            server_list = json.load(settings)
        user_roles = ctx.message.author.roles
        server_id = ctx.message.server.id
        if server_id not in server_list:
            return True
        elif (CMB_ADMIN in server_list[server_id]
              or PREFIX_DISABLED in server_list[server_id]):
            if CMB_ADMIN not in [role.name for role in user_roles]:
                return False
    except:
        pass
    finally:
        return True


def update_server_count(server_count):
    try:
        header = {'Authorization': '{}'.format(config_data["auth_token"])}
        payload = {'server_count': server_count}
        requests.post(DISCORD_BOT_URL,
                      headers=header,
                      data=payload)
    except:
        pass


@bot.command(pass_context=True)
async def prefix(ctx, prefix: str):
    """
    Customizes the prefix for the server
    An example for this command would be:
    "$prefix !"

    @param ctx - context of the command
    @param prefix - new prefix for the channel
    """
    try:
        if not _check_permission(ctx):
            return
        try:
            server = str(ctx.message.server.id)
        except:
            await bot.say("Failed to create a prefix for the server. "
                          "Please make sure this channel is within a "
                          "valid server.")
            return
        prefix_list[server] = prefix
        save_prefix_file(prefix_list)
        msg = "`{}` prefix has been set for bot commands.".format(prefix)
        await bot.say(msg)
    except Exception as e:
        print("An error has occured. See error.log.")
        logger.error("Exception: {}".format(str(e)))

prefix_list = check_prefix_file()
save_prefix_file(prefix_list, backup=True)


def main():
    try:
        logger.info('Starting bot..')
        print("Starting bot..")
        CoinMarketBot()
    except Exception as e:
        logging.error('Bot failed to run: {}'.format(str(e)))
        print(e)
    logger.info("Bot is now offline.")


main()
