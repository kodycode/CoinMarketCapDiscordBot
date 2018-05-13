from bot_logger import logger
from cogs.modules.alert_functionality import AlertFunctionality
from cogs.modules.cal_functionality import CalFunctionality
from cogs.modules.coin_market_functionality import CoinMarketFunctionality
from cogs.modules.coin_market import CoinMarket
from cogs.modules.misc_functionality import MiscFunctionality
from cogs.modules.subscriber_functionality import SubscriberFunctionality
import asyncio
import datetime
import discord
import json


CMB_ADMIN = "CMB ADMIN"


class CoreFunctionalityException(Exception):
    """Handles core related errors"""


class CoreFunctionality:
    """Handles Core functionality"""

    def __init__(self, bot):
        with open('config.json') as config:
            self.config_data = json.load(config)
        self.bot = bot
        self.started = False
        self.market_list = None
        self.market_stats = None
        self.acronym_list = None
        self.coin_market = CoinMarket()
        self.server_data = self._check_server_file()
        self.cmc = CoinMarketFunctionality(bot,
                                           self.coin_market,
                                           self.server_data)
        self.alert = AlertFunctionality(bot,
                                        self.coin_market,
                                        self.config_data["alert_capacity"],
                                        self.server_data)
        self.subscriber = SubscriberFunctionality(bot,
                                                  self.coin_market,
                                                  self.config_data["subscriber_capacity"],
                                                  self.server_data)
        self.cal = CalFunctionality(bot,
                                    self.config_data,
                                    self.server_data)
        self.misc = MiscFunctionality(bot, self.server_data)
        self._save_server_file(self.server_data, backup=True)
        self.bot.loop.create_task(self._continuous_updates())

    def _check_server_file(self):
        """
        Checks to see if there's a valid server_settings.json file
        """
        try:
            with open('server_settings.json') as settings:
                return json.load(settings)
        except FileNotFoundError:
            self._save_server_file()
            return json.loads('{}')
        except Exception as e:
            print("Unable to load server file. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    def _save_server_file(self, server_data={}, backup=False):
        """
        Saves server_settings.json file
        """
        if backup:
            server_settings_filename = "server_settings_backup.json"
        else:
            server_settings_filename = "server_settings.json"
        with open(server_settings_filename, 'w') as outfile:
            json.dump(server_data,
                      outfile,
                      indent=4)

    def _update_server_data(self):
        try:
            self.cmc.update(server_data=self.server_data)
            self.alert.update(server_data=self.server_data)
            self.subscriber.update(server_data=self.server_data)
            self.misc.update(server_data=self.server_data)
            self.cal.update(server_data=self.server_data)
        except Exception as e:
            print("Failed to update server data. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def _update_data(self, minute=0):
        try:
            await self._update_market()
            self._load_acronyms()
            self.cmc.update(self.market_list,
                            self.acronym_list,
                            self.market_stats)
            self.alert.update(self.market_list, self.acronym_list)
            self.subscriber.update(self.market_list, self.acronym_list)
            self.cal.update(self.acronym_list)
            await self._update_game_status()
            await self.alert.alert_user()
            if self.started:
                await self.subscriber.display_live_data(minute)
        except Exception as e:
            print("Failed to update data. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def _update_game_status(self):
        """
        Updates the game status of the bot
        """
        try:
            game_status = discord.Game(name="$updates to see log")
            await self.bot.change_presence(game=game_status)
        except Exception as e:
            print("Failed to update game status. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def _continuous_updates(self):
        await self._update_data()
        self.started = True
        print('CoinMarketDiscordBot is online.')
        logger.info('Bot is online.')
        while True:
            time = datetime.datetime.now()
            if time.minute % 5 == 0:
                await self._update_data(time.minute)
                await asyncio.sleep(60)
            else:
                await asyncio.sleep(20)

    async def _update_market(self):
        """
        Loads all the cryptocurrencies that exist in the market

        @return - list of crypto-currencies
        """
        try:
            retry_count = 0
            market_stats = self.coin_market.fetch_coinmarket_stats()
            currency_data = self.coin_market.fetch_currency_data(load_all=True)
            while market_stats is None or currency_data is None:
                if retry_count >= 10:
                    msg = ("Max retry attempts reached. Please make "
                           "sure you're able to access coinmarketcap "
                           "through their website, check if the coinmarketapi "
                           "is down, and check if "
                           "anything is blocking you from requesting "
                           "data.")
                    raise CoreFunctionalityException(msg)
                logger.warning("Retrying to get data..")
                if market_stats is None:
                    market_stats = self.coin_market.fetch_coinmarket_stats()
                if currency_data is None:
                    currency_data = self.coin_market.fetch_currency_data(load_all=True)
                retry_count += 1
                await asyncio.sleep(5)
            market_dict = {}
            for currency in currency_data:
                market_dict[currency['id']] = currency
            self.market_stats = market_stats
            self.market_list = market_dict
        except CoreFunctionalityException as e:
            logger.error(str(e))
        except Exception as e:
            print("Failed to update market. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    def _load_acronyms(self):
        """
        Loads all acronyms of existing crypto-coins out there

        @return - list of crypto-acronyms
        """
        try:
            if self.market_list is None:
                raise Exception("Market list was not loaded.")
            acronym_list = {}
            duplicate_list = {}
            for currency, data in self.market_list.items():
                if data['symbol'] in acronym_list:
                    if data['symbol'] not in duplicate_list:
                        duplicate_list[data['symbol']] = 1
                    duplicate_list[data['symbol']] += 1
                    if data['symbol'] not in acronym_list[data['symbol']]:
                        acronym_list[data['symbol'] + '1'] = acronym_list[data['symbol']]
                        acronym_list[data['symbol']] = ("Duplicate acronyms "
                                                        "found. Possible "
                                                        "searches are:\n"
                                                        "{}1 ({})\n".format(data['symbol'],
                                                                            acronym_list[data['symbol']]))
                    dupe_key = data['symbol'] + str(duplicate_list[data['symbol']])
                    acronym_list[dupe_key] = currency
                    acronym_list[data['symbol']] = (acronym_list[data['symbol']]
                                                    + "{} ({})\n".format(dupe_key,
                                                                         currency))
                else:
                    acronym_list[data['symbol']] = currency
            self.acronym_list = acronym_list
        except Exception as e:
            print("Failed to load cryptocurrency acronyms. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def _say_msg(self, msg=None, channel=None, emb=None):
        """
        Bot will say msg if given correct permissions

        @param msg - msg to say
        @param channel - channel to send msg to
        @param emb - embedded msg to say
        """
        try:
            if channel:
                if emb:
                    await self.bot.send_message(channel, embed=emb)
                else:
                    await self.bot.send_message(channel, msg)
            else:
                if emb:
                    await self.bot.say(embed=emb)
                else:
                    await self.bot.say(msg)
        except:
            pass

    async def display_server_settings(self, ctx):
        """
        Displays server settings of cmds the admins have enabled
        """
        try:
            try:
                ctx.message.channel.server
            except:
                await self._say_msg("Not a valid server to retrieve settings.")
                return
            msg = ''
            server_id = ctx.message.server.id
            if server_id not in self.server_data:
                await self._say_msg("No settings to display.")
                return
            elif len(self.server_data[server_id]) == 0:
                await self._say_msg("No settings to display.")
                return
            for setting in self.server_data[server_id]:
                setting_line = "{}\n".format(setting)
                msg += setting_line
            em = discord.Embed(title="Server Settings",
                               description=msg,
                               colour=0xFFFFFF)
            await self._say_msg(emb=em)
        except Exception as e:
            print("Failed to display server settings. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def toggle_commands(self, ctx, mode):
        """
        Toggles the command mode on/off
        """
        try:
            try:
                user_roles = ctx.message.author.roles
            except:
                await self._say_msg("Command must be used in a server.")
                return
            if CMB_ADMIN not in [role.name for role in user_roles]:
                await self._say_msg("Admin role '{}' is required for "
                                    "this command.".format(CMB_ADMIN))
                return
            channel = ctx.message.channel.id
            try:
                server = self.bot.get_channel(channel).server  # validate channel
            except:
                await self._say_msg("Not a valid server to toggle mode.")
                return
            if server.id not in self.server_data:
                self.server_data[server.id] = [mode]
                await self._say_msg("Server set '{}'.".format(mode))
            elif mode in self.server_data[server.id]:
                self.server_data[server.id].remove(mode)
                await self._say_msg("'{}' has been taken off.".format(mode))
            elif mode not in self.server_data[server.id]:
                self.server_data[server.id].append(mode)
                await self._say_msg("Server set '{}'.".format(mode))
            self._save_server_file(self.server_data)
            self._update_server_data()
        except Exception as e:
            print("Failed to toggle {}. See error.log.".format(mode))
            logger.error("Exception: {}".format(str(e)))
