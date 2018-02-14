from bot_logger import logger
from cogs.modules.coin_market import CoinMarketException, CurrencyException, FiatException
from collections import defaultdict
from discord.errors import Forbidden
from cogs.modules.asyncioplus import limited_as_completed
import discord
import json


class SubscriberFunctionality:
    """Handles Subscriber command Functionality"""

    def __init__(self, bot, coin_market, sub_capacity):
        self.bot = bot
        self.coin_market = coin_market
        self.sub_capacity = int(sub_capacity)
        self.market_list = ""
        self.acronym_list = ""
        self.cache_data = {}
        self.cache_channel = {}
        self.supported_rates = ["default", "half", "hourly"]
        self.subscriber_data = self._check_subscriber_file()
        self._save_subscriber_file(self.subscriber_data, backup=True)

    def update(self, market_list, acronym_list):
        """
        Updates utilities with new coin market data
        """
        self.market_list = market_list
        self.acronym_list = acronym_list
        self.cache_data.clear()

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
                    if self.market_list:
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

    async def _get_live_data(self, channel, channel_settings, minute):
        """
        Obtains and returns the data of currencies requested
        """
        try:
            valid_time = True
            if int(minute) != int(channel_settings["interval"]):
                if int(minute) % int(channel_settings["interval"]) != 0:
                    valid_time = False
        except KeyError:
            pass
        except Exception as e:
            logger.error("Something went wrong with retrieving live data: {}"
                         "".format(str(e)))
            valid_time = False
        finally:
            if not valid_time:
                return None
            if channel_settings["currencies"]:
                return self.coin_market.get_current_multiple_currency(self.market_list,
                                                                      None,
                                                                      self.cache_data,
                                                                      channel_settings["currencies"],
                                                                      channel_settings["fiat"])

    async def display_live_data(self, minute):
        """
        Obtains and displays live updates of coin stats in n-second intervals.

        @param minute - the minute the clock is at
        """
        try:
            self._check_invalid_sub_currencies()
            subscriber_list = self.subscriber_data.copy()
            for channel in subscriber_list:
                if channel not in self.cache_channel:
                    self.cache_channel[channel] = self.bot.get_channel(channel)

            async def get_data(channel, minute):
                channel_settings = subscriber_list[channel]
                data = await self._get_live_data(channel,
                                                 channel_settings,
                                                 minute)
                if not data:
                    return None
                return channel, data

            async def post_data(data_set, bot):
                for data in limited_as_completed(data_set, 10):
                    first_post = True
                    try:
                        data = await data
                        ch = data[0]
                        data = data[1]
                        channel_settings = subscriber_list[ch]
                        if channel_settings["purge"]:
                            try:
                                await bot.purge_from(bot.get_channel(ch),
                                                     limit=10)
                            except:
                                pass
                        for msg in data:
                            if first_post:
                                em = discord.Embed(title="Live Currency Update",
                                                   description=msg,
                                                   colour=0xFF9900)
                                first_post = False
                            else:
                                em = discord.Embed(description=msg,
                                                   colour=0xFF9900)
                            await self._say_msg(channel=self.cache_channel[ch],
                                                emb=em)
                    except TypeError:
                        pass
            coros = (get_data(channel, minute) for channel in self.cache_channel)
            self.bot.loop.create_task(post_data(coros, self.bot))
        except CurrencyException as e:
            print("An error has occured. See error.log.")
            logger.error("CurrencyException: {}".format(str(e)))
        except FiatException as e:
            logger.error("FiatException: {}".format(str(e)))
            await self._say_msg(e)
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
            channel = ctx.message.channel.id
            subscriber_list = self.subscriber_data
            try:
                self.bot.get_channel(channel).server  # validate channel
            except:
                await self._say_msg("Failed to add channel as a subscriber. "
                                    " Please make sure this channel is within a "
                                    "valid server.")
                return
            if channel not in subscriber_list:
                if len(self.subscriber_data) >= self.sub_capacity:
                    await self._say_msg("Subscriber capacity met. Contact the "
                                        "owner of this bot to reserve a "
                                        "channel.")
                    return
                subscriber_list[channel] = {}
                channel_settings = subscriber_list[channel]
                channel_settings["interval"] = "5"
                channel_settings["purge"] = False
                channel_settings["fiat"] = ucase_fiat
                channel_settings["currencies"] = []
                self._save_subscriber_file(self.subscriber_data)
                await self._say_msg("Channel has succcesfully subscribed. Now "
                                    "add some currencies with `$addc` to begin "
                                    "receiving updates.")
            else:
                await self._say_msg("Channel is already subscribed.")
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
                await self._say_msg("Channel has unsubscribed.")
            else:
                await self._say_msg("Channel was never subscribed.")
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
                await self._say_msg("Channel was never subscribed.")
                return
            channel_settings = subscriber_list[channel]
            channel_settings["purge"] = not channel_settings["purge"]
            self._save_subscriber_file(self.subscriber_data)
            if channel_settings["purge"]:
                await self._say_msg("Purge mode on. Bot will now purge messages upon"
                                    " live updates. Please make sure your bot has "
                                    "the right permissions to remove messages.")
            else:
                await self._say_msg("Purge mode off.")
        except Exception as e:
            await self._say_msg("Failed to set purge mode. Please make sure this"
                                " channel is within a valid server.")

    async def get_sub_currencies(self, ctx):
        """
        Displays the currencies the channel in context is subbed too

        @param ctx - context of the command sent
        """
        try:
            channel = ctx.message.channel.id
            subscriber_list = self.subscriber_data
            if channel in subscriber_list:
                channel_settings = subscriber_list[channel]
                currency_list = channel_settings["currencies"]
                if len(currency_list) != 0:
                    msg = ""
                    for currency in currency_list:
                        msg += "__**{}**__\n".format(currency.title())
                        color = 0x00FF00
                else:
                    msg = "Channel does not have any currencies to display."
                    color = 0xD14836
            else:
                msg = "Channel was never subscribed."
                color = 0xD14836
            try:
                em = discord.Embed(title="Subscriber Currencies",
                                   description=msg,
                                   colour=color)
                await self._say_msg(emb=em)
            except:
                pass
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
                    await self._say_msg(currency)
                    return
            if currency not in self.market_list:
                raise CurrencyException("Currency is invalid: ``{}``".format(currency))
            channel = ctx.message.channel.id
            subscriber_list = self.subscriber_data
            if channel in subscriber_list:
                channel_settings = subscriber_list[channel]
                if currency in channel_settings["currencies"]:
                    await self._say_msg("``{}`` is already added.".format(currency.title()))
                    return
                channel_settings["currencies"].append(currency)
                self._save_subscriber_file(self.subscriber_data)
                await self._say_msg("``{}`` was successfully added.".format(currency.title()))
            else:
                await self._say_msg("The channel needs to be subscribed first.")
        except Forbidden:
            pass
        except CurrencyException as e:
            logger.error("CurrencyException: {}".format(str(e)))
            await self._say_msg(e)
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
                    await self._say_msg(currency)
                    return
            channel = ctx.message.channel.id
            subscriber_list = self.subscriber_data
            if channel in subscriber_list:
                channel_settings = subscriber_list[channel]
                if currency in channel_settings["currencies"]:
                    channel_settings["currencies"].remove(currency)
                    self._save_subscriber_file(self.subscriber_data)
                    await self._say_msg("``{}`` was successfully removed."
                                        "".format(currency.title()))
                else:
                    await self._say_msg("``{}`` was never added or is invalid."
                                        "".format(currency.title()))
            else:
                await self._say_msg("The channel needs to be subscribed first.")
        except Forbidden:
            pass
        except CurrencyException as e:
            logger.error("CurrencyException: {}".format(str(e)))
            await self._say_msg(e)
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def set_live_update_interval(self, ctx, rate):
        """
        Sets the interval at which the bot should post updates
        to the channel. By default, it will be every 5 minutes.

        @param ctx - context of the command sent
        @param minutes - interval in minutes to send an update
                         (only accepts multiples of 5)
        """
        try:
            if rate not in self.supported_rates:
                await self._say_msg("The rate entered is not supported. "
                                    "Current intervals you can choose are:\n"
                                    "**default** - every 5 minutes\n"
                                    "**half** - every 30 minute mark\n"
                                    "**hourly** - every hour mark\n")
                return
            channel = ctx.message.channel.id
            if channel in self.subscriber_data:
                if rate == "hourly":
                    self.subscriber_data[channel]["interval"] = "60"
                elif rate == "half":
                    self.subscriber_data[channel]["interval"] = "30"
                else:
                    self.subscriber_data[channel]["interval"] = "5"
                self._save_subscriber_file(self.subscriber_data)
                await self._say_msg("Interval is set to **{}**".format(rate))
            else:
                await self._say_msg("Channel must be subscribed first.")
        except Exception as e:
            print("Unable to set live update interval. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def get_subset(self, ctx):
        """
        Gets the substats of the subscribed channel and displays
        the interval of the bot, purge mode, and the number of
        currencies

        @param ctx - context of the command sent
        """
        try:
            error = False
            channel = ctx.message.channel.id
            if channel not in self.subscriber_data:
                raise Exception("Channel not in subscriber list.")
            interval = self.subscriber_data[channel]["interval"]
        except KeyError:
            interval = "5"
            pass
        except Exception as e:
            error = True
            print("Unable to get sub settings. See error.log.")
            logger.error("Exception: {}".format(str(e)))
        finally:
            if error:
                await self._say_msg("Unable to get sub settings. Please check "
                                    "if this channel is subbed. If you believe"
                                    " this is a mistake, please contact the "
                                    "owner of the bot.")
                return
            fiat = self.subscriber_data[channel]["fiat"]
            purge_mode = self.subscriber_data[channel]["purge"]
            num_currencies = len(self.subscriber_data[channel]["currencies"])
            msg = ("Fiat: **{}**\n"
                   "Purge Mode: **{}**\n"
                   "Update interval: Every **{}** minutes\n"
                   "Number of currencies subscribed to: **{}**\n"
                   "To see what currencies are subscribed, type "
                   "`$getc`".format(fiat,
                                    purge_mode,
                                    interval,
                                    num_currencies))
            em = discord.Embed(title="Subscriber Settings",
                               description=msg,
                               colour=0xFF9900)
            await self._say_msg(emb=em)
