from bot_logger import logger
from cogs.modules.coin_market import CoinMarketException, CurrencyException, FiatException
from collections import defaultdict
from discord.errors import Forbidden
import asyncio
import discord
import json


class SubscriberFunctionality:
    """Handles Subscriber command Functionality"""

    def __init__(self, bot, coin_market):
        self.bot = bot
        self.coin_market = coin_market
        self.market_list = ""
        self.acronym_list = ""
        self.subscriber_data = self._check_subscriber_file()
        self._save_subscriber_file(self.subscriber_data, backup=True)
        asyncio.ensure_future(self._update_game_status())

    def update(self, market_list, acronym_list):
        """
        Updates utilities with new coin market data
        """
        self.market_list = market_list
        self.acronym_list = acronym_list

    def _check_subscriber_file(self):
        """
        Checks to see if there's a valid subscribers.json file
        """
        try:
            with open('subscribers.json') as subscribers:
                return json.load(subscribers)
        except FileNotFoundError:
            self._save_subscriber_file()
            return json.loads('{}')
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    def _save_subscriber_file(self, subscriber_data={}, backup=False):
        """
        Saves subscribers.json file
        """
        if backup:
            subscriber_filename = "subscribers_backup.json"
        else:
            subscriber_filename = "subscribers.json"
        with open(subscriber_filename, 'w') as outfile:
            json.dump(subscriber_data,
                      outfile,
                      indent=4)

    async def _say_error(self, e):
        """
        Bot will check and say the error if given correct permissions

        @param e - error object
        """
        try:
            await self.bot.say(e)
        except:
            pass

    async def _update_game_status(self):
        """
        Updates the game status of the bot
        """
        try:
            num_channels = len(self.subscriber_data)
            game_status = discord.Game(name="with {} subscriber(s)"
                                            "".format(num_channels))
            await self.bot.change_presence(game=game_status)
        except Exception as e:
            print("Failed to update game status. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    def _check_invalid_sub_currencies(self):
        """
        Check if currencies have become invalid
        If invalid, the currencies will be removed from the
        subscriber currency list
        """
        try:
            remove_currencies = defaultdict(list)
            subscriber_list = self.subscriber_data
            for channel in subscriber_list:
                channel_settings = subscriber_list[channel]
                for currency in channel_settings["currencies"]:
                    if self.market_list is not None:
                        if currency not in self.market_list:
                            remove_currencies[channel].append(currency)
            for channel in remove_currencies:
                for currency in remove_currencies[channel]:
                    subscriber_list[channel]["currencies"].remove(currency)
                    logger.error("Removed '{}' from channel {}".format(currency,
                                                                       channel))
            if remove_currencies:
                self._save_subscriber_file(self.subscriber_data)
        except Exception as e:
            raise CurrencyException("Failed to validate sub "
                                    "currencies: {}".format(str(e)))

    async def display_live_data(self):
        """
        Obtains and displays live updates of coin stats in n-second intervals.
        """
        try:
            self._check_invalid_sub_currencies()
            subscriber_list = self.subscriber_data
            msg_count = 0
            for channel in subscriber_list:
                if self.bot.get_channel(channel) in self.bot.get_all_channels():
                    channel_settings = subscriber_list[channel]
                    if channel_settings["currencies"]:
                        if channel_settings["purge"]:
                            try:
                                await self.bot.purge_from(self.bot.get_channel(channel),
                                                          limit=100)
                            except:
                                pass
                        data = self.coin_market.get_current_multiple_currency(self.market_list,
                                                                              self.acronym_list,
                                                                              channel_settings["currencies"],
                                                                              channel_settings["fiat"])
                        for msg in data:
                            if msg_count == 0:
                                em = discord.Embed(title="Live Currency Update",
                                                   description=msg,
                                                   colour=0xFFD700)
                                msg_count += 1
                            else:
                                em = discord.Embed(description=msg,
                                                   colour=0xFFD700)
                            try:
                                await self.bot.send_message(self.bot.get_channel(channel),
                                                            embed=em)
                            except:
                                pass
                        msg_count = 0
        except CurrencyException as e:
            print("An error has occured. See error.log.")
            logger.error("CurrencyException: {}".format(str(e)))
        except FiatException as e:
            logger.error("FiatException: {}".format(str(e)))
            await self.bot.say(e)
        except CoinMarketException as e:
            print("An error has occured. See error.log.")
            logger.error("CoinMarketException: {}".format(str(e)))
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def add_subscriber(self, ctx, fiat):
        """
        Adds channel to the live update subscriber list in subscribers.json

        @param ctx - context of the command sent
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        try:
            ucase_fiat = self.coin_market.fiat_check(fiat)
            channel = str(ctx.message.channel.id)
            subscriber_list = self.subscriber_data
            try:
                self.bot.get_channel(channel).server  # validate channel
            except:
                await self.bot.say("Failed to add channel as a subscriber. "
                                   " Please make sure this channel is within a "
                                   "valid server.")
                return
            if channel not in subscriber_list:
                subscriber_list[channel] = {}
                channel_settings = subscriber_list[channel]
                channel_settings["purge"] = False
                channel_settings["fiat"] = ucase_fiat
                channel_settings["currencies"] = []
                self._save_subscriber_file(self.subscriber_data)
                await self._update_game_status()
                await self.bot.say("Channel has succcesfully subscribed. Now "
                                   "add some currencies with `$addc` to begin "
                                   "receiving updates.")
            else:
                await self.bot.say("Channel is already subscribed.")
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def remove_subscriber(self, ctx):
        """
        Removes channel from the subscriber list in subscribers.json

        @param ctx - context of the command sent
        """
        try:
            channel = ctx.message.channel.id
            subscriber_list = self.subscriber_data
            if channel in subscriber_list:
                subscriber_list.pop(channel)
                self._save_subscriber_file(self.subscriber_data)
                await self._update_game_status()
                await self.bot.say("Channel has unsubscribed.")
            else:
                await self.bot.say("Channel was never subscribed.")
        except Forbidden:
            pass
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def toggle_purge(self, ctx):
        """
        Turns purge mode on/off for the channel
        """
        try:
            channel = ctx.message.channel.id
            subscriber_list = self.subscriber_data
            self.bot.get_channel(channel).server  # validate channel
            if channel not in subscriber_list:
                await self.bot.say("Channel was never subscribed.")
                return
            channel_settings = subscriber_list[channel]
            channel_settings["purge"] = not channel_settings["purge"]
            self._save_subscriber_file(self.subscriber_data)
            if channel_settings["purge"]:
                await self.bot.say("Purge mode on. Bot will now purge messages upon"
                                   " live updates. Please make sure your bot has "
                                   "the right permissions to remove messages.")
            else:
                await self.bot.say("Purge mode off.")
        except Exception as e:
            await self.bot.say("Failed to set purge mode. Please make sure this"
                               " channel is within a valid server.")

    async def get_sub_currencies(self, ctx):
        """
        Displays the currencies the channel in context is subbed too

        @param ctx - context of the command sent
        """
        try:
            channel = str(ctx.message.channel.id)
            subscriber_list = self.subscriber_data
            if channel in subscriber_list:
                channel_settings = subscriber_list[channel]
                currency_list = channel_settings["currencies"]
                if len(currency_list) != 0:
                    msg = "Currently this channel displays the following:\n"
                    for currency in currency_list:
                        msg += "__**{}**__\n".format(currency.title())
                else:
                    msg = "Channel does not have any currencies to display."
                    await self.bot.say(msg)
            else:
                msg = "Channel was never subscribed."
            await self.bot.say(msg)
        except Forbidden:
            pass
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def add_currency(self, ctx, currency):
        """
        Adds a cryptocurrency to the subscriber settings

        @param ctx - context of the command sent
        @param currency - the cryptocurrency to add
        """
        try:
            if currency.upper() in self.acronym_list:
                currency = self.acronym_list[currency.upper()]
                if "Duplicate" in currency:
                    await self.bot.say(currency)
                    return
            if currency not in self.market_list:
                raise CurrencyException("Currency is invalid: ``{}``".format(currency))
            channel = ctx.message.channel.id
            subscriber_list = self.subscriber_data
            if channel in subscriber_list:
                channel_settings = subscriber_list[channel]
                if currency in channel_settings["currencies"]:
                    await self.bot.say("``{}`` is already added.".format(currency.title()))
                    return
                channel_settings["currencies"].append(currency)
                self._save_subscriber_file(self.subscriber_data)
                await self.bot.say("``{}`` was successfully added.".format(currency.title()))
            else:
                await self.bot.say("The channel needs to be subscribed first.")
        except Forbidden:
            pass
        except CurrencyException as e:
            logger.error("CurrencyException: {}".format(str(e)))
            await self._say_error(e)
        except CoinMarketException as e:
            print("An error has occured. See error.log.")
            logger.error("CoinMarketException: {}".format(str(e)))
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def remove_currency(self, ctx, currency):
        """
        Removes a cryptocurrency from the subscriber settings

        @param ctx - context of the command sent
        @param currency - the cryptocurrency to remove
        """
        try:
            if currency.upper() in self.acronym_list:
                currency = self.acronym_list[currency.upper()]
                if "Duplicate" in currency:
                    await self.bot.say(currency)
                    return
            channel = ctx.message.channel.id
            subscriber_list = self.subscriber_data
            if channel in subscriber_list:
                channel_settings = subscriber_list[channel]
                if currency in channel_settings["currencies"]:
                    channel_settings["currencies"].remove(currency)
                    self._save_subscriber_file(self.subscriber_data)
                    await self.bot.say("``{}`` was successfully removed.".format(currency.title()))
                    return
                else:
                    await self.bot.say("``{}`` was never added or is invalid.".format(currency.title()))
            else:
                await self.bot.say("The channel needs to be subscribed first.")
        except Forbidden:
            pass
        except CurrencyException as e:
            logger.error("CurrencyException: {}".format(str(e)))
            await self._say_error(e)
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))
