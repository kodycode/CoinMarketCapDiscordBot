from bot_logger import logger
from collections import defaultdict
from cogs.modules.coin_market import CoinMarket, CoinMarketException, CurrencyException, FiatException, MarketStatsException
from discord.errors import Forbidden
import asyncio
import datetime
import discord
import json
import re


class CommandFunctionality:
    """Handles CMC command functionality"""

    def __init__(self, bot):
        self.supported_operators = ["<", ">", "<=", ">="]
        self.subscriber_data = self._check_subscriber_file()
        self.alert_data = self._check_alert_file()
        self.bot = bot
        self.market_list = None
        self.market_stats = None
        self.coin_market = CoinMarket()
        self.live_on = False
        asyncio.async(self._continuous_updates())

    def _check_subscriber_file(self):
        """
        Checks to see if there's a valid subscribers.json file
        """
        try:
            with open('subscribers.json') as subscribers:
                return json.load(subscribers)
        except FileNotFoundError:
            with open('subscribers.json', 'w') as outfile:
                json.dump({},
                          outfile,
                          indent=4)
                return json.loads('{}')
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    def _check_alert_file(self):
        """
        Checks to see if there's a valid alerts.json file
        """
        try:
            with open('alerts.json') as alerts:
                return json.load(alerts)
        except FileNotFoundError:
            with open('alerts.json', 'w') as outfile:
                json.dump({},
                          outfile,
                          indent=4)
                return json.loads('{}')
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    @asyncio.coroutine
    def _update_data(self):
        self._update_market()
        self.acronym_list = self._load_acronyms()
        yield from self._display_live_data()
        yield from self._alert_user_()

    @asyncio.coroutine
    def _continuous_updates(self):
        yield from self._update_data()
        while True:
            time = datetime.datetime.now()
            if time.minute % 5 == 0:
                yield from self._update_data()
            yield from asyncio.sleep(60)

    def _update_market(self):
        """
        Loads all the cryptocurrencies that exist in the market

        @return - list of crypto-currencies
        """
        try:
            self.market_stats = self.coin_market.fetch_coinmarket_stats()
            currency_data = self.coin_market.fetch_currency_data(load_all=True)
            market_dict = {}
            for currency in currency_data:
                market_dict[currency['id']] = currency
            self.market_list = market_dict
        except CurrencyException as e:
            print("An error has occured. See error.log.")
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
            duplicate_count = 0
            for currency, data in self.market_list.items():
                if data['symbol'] in acronym_list:
                    duplicate_count += 1
                    if data['symbol'] not in acronym_list[data['symbol']]:
                        acronym_list[data['symbol'] + str(1)] = acronym_list[data['symbol']]
                        acronym_list[data['symbol']] = ("Duplicate acronyms "
                                                        "found. Possible "
                                                        "searches are:\n"
                                                        "{}1 ({})\n".format(data['symbol'],
                                                                            acronym_list[data['symbol']]))
                    dupe_acronym = re.search('\\d+', acronym_list[data['symbol']])
                    dupe_num = str(int(dupe_acronym.group(len(dupe_acronym.group()) - 1)) + 1)
                    dupe_key = data['symbol'] + dupe_num
                    acronym_list[dupe_key] = currency
                    acronym_list[data['symbol']] = (acronym_list[data['symbol']]
                                                    + "{} ({})".format(dupe_key,
                                                                       currency))
                else:
                    acronym_list[data['symbol']] = currency
            return acronym_list
        except Exception as e:
            print("Failed to load cryptocurrency acronyms. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def display_search(self, currency, fiat):
        """
        Embeds search results and displays it in chat.

        @param currency - cryptocurrency to search for
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        try:
            msg_count = 0
            if ',' in currency:
                if ' ' in currency:
                    await self.bot.say("Don't include spaces in multi-coin search.")
                    return
                currency_list = currency.split(',')
                data = self.coin_market.get_current_multiple_currency(self.market_list,
                                                                      self.acronym_list,
                                                                      currency_list,
                                                                      fiat.upper())
                for msg in data:
                    if msg_count == 0:
                        em = discord.Embed(title="Search results",
                                           description=msg,
                                           colour=0xFFD700)
                        msg_count += 1
                    else:
                        em = discord.Embed(description=msg,
                                           colour=0xFFD700)
                    await self.bot.say(embed=em)
            else:
                data, isPositivePercent = self.coin_market.get_current_currency(self.market_list,
                                                                                self.acronym_list,
                                                                                currency,
                                                                                fiat.upper())
                if isPositivePercent:
                    em = discord.Embed(title="Search results",
                                       description=data,
                                       colour=0x009993)
                else:
                    em = discord.Embed(title="Search results",
                                       description=data,
                                       colour=0xD14836)
                await self.bot.say(embed=em)
        except Forbidden:
            pass
        except CurrencyException as e:
            logger.error("CurrencyException: {}".format(str(e)))
            await self.bot.say(e)
        except FiatException as e:
            error_msg = (str(e) +
                         "\nIf you're doing multiple searches, please "
                         "make sure there's no spaces after the comma.")
            logger.error("FiatException: {}".format(str(e)))
            await self.bot.say(error_msg)
        except CoinMarketException as e:
            print("An error has occured. See error.log.")
            logger.error("CoinMarketException: {}".format(str(e)))
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def display_stats(self, fiat):
        """
        Obtains the market stats to display

        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        try:
            data = self.coin_market.get_current_stats(self.market_stats, fiat)
            em = discord.Embed(title="Market Stats",
                               description=data,
                               colour=0x008000)
            await self.bot.say(embed=em)
        except Forbidden:
            pass
        except MarketStatsException as e:
            logger.error("MarketStatsException: {}".format(str(e)))
            await self.bot.say(e)
        except FiatException as e:
            logger.error("FiatException: {}".format(str(e)))
            await self.bot.say(e)
        except CoinMarketException as e:
            print("An error has occured. See error.log.")
            logger.error("CoinMarketException: {}".format(str(e)))
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def _display_live_data(self):
        """
        Obtains and displays live updates of coin stats in n-second intervals.
        """
        try:
            # remove_channels = []
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
            #     else:
            #         remove_channels.append(channel)
            # if remove_channels:
            #     for channel in remove_channels:
            #         if channel in subscriber_list:
            #             subscriber_list.pop(channel)
            #     with open('subscribers.json', 'w') as outfile:
            #         json.dump(self.subscriber_data,
            #                   outfile,
            #                   indent=4)
            #     num_channels = len(subscriber_list)
            #     game_status = discord.Game(name="with {} subscriber(s)".format(num_channels))
            #     await self.bot.change_presence(game=game_status)
        except CurrencyException as e:
            logger.error("CurrencyException: {}".format(str(e)))
            self.live_on = False
            await self.bot.say(e)
        except FiatException as e:
            logger.error("FiatException: {}".format(str(e)))
            self.live_on = False
            await self.bot.say(e)
        except CoinMarketException as e:
            print("An error has occured. See error.log.")
            logger.error("CoinMarketException: {}".format(str(e)))
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def calculate_coin_to_coin(self, currency1, currency2, currency_amt):
        """
        Calculates cryptocoin to another cryptocoin and displays it

        @param currency1 - currency to convert from
        @param currency2 - currency to convert to
        @param currency_amt - amount of currency coins
        """
        try:
            acronym1 = ''
            acronym2 = ''
            if currency1.upper() in self.acronym_list:
                acronym1 = currency1.upper()
                currency1 = self.acronym_list[currency1.upper()]
            else:
                acronym1 = self.market_list[currency1]["symbol"]
            if currency2.upper() in self.acronym_list:
                acronym2 = currency2.upper()
                currency2 = self.acronym_list[currency2.upper()]
            else:
                acronym2 = self.market_list[currency2]["symbol"]
            price_btc1 = float(self.market_list[currency1]['price_btc'])
            price_btc2 = float(self.market_list[currency2]['price_btc'])
            btc_amt = float("{:.8f}".format(currency_amt * price_btc1))
            converted_amt = "{:.8f}".format(btc_amt/price_btc2).rstrip('0')
            currency_amt = "{:.8f}".format(currency_amt).rstrip('0')
            if currency_amt.endswith('.'):
                currency_amt = currency_amt.replace('.', '')
            result = "**{} {}** converts to **{} {}**".format(currency_amt,
                                                              currency1.title(),
                                                              converted_amt,
                                                              currency2.title())
            em = discord.Embed(title="{}({}) to {}({})".format(currency1.title(),
                                                               acronym1,
                                                               currency2.title(),
                                                               acronym2),
                               description=result,
                               colour=0xFFD700)
            await self.bot.say(embed=em)
        except Forbidden:
            pass
        except Exception as e:
            await self.bot.say("Command failed. Make sure the arguments are valid.")
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def calculate_coin_to_fiat(self, currency, currency_amt, fiat):
        """
        Calculates coin to fiat rate and displays it

        @param currency - cryptocurrency that was bought
        @param currency_amt - amount of currency coins
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        try:
            ucase_fiat = self.coin_market.fiat_check(fiat)
            if currency.upper() in self.acronym_list:
                currency = self.acronym_list[currency.upper()]
            data = self.market_list[currency]
            current_cost = float(data['price_usd'])
            fiat_cost = self.coin_market.format_price(currency_amt*current_cost,
                                                      ucase_fiat)
            currency = currency.title()
            result = "**{} {}** is worth **{}**".format(currency_amt,
                                                        data['symbol'],
                                                        str(fiat_cost))
            em = discord.Embed(title="{}({}) to {}".format(currency,
                                                           data['symbol'],
                                                           ucase_fiat),
                               description=result,
                               colour=0xFFD700)
            await self.bot.say(embed=em)
        except Forbidden:
            pass
        except CurrencyException as e:
            logger.error("CurrencyException: {}".format(str(e)))
            self.live_on = False
            await self.bot.say(e)
        except FiatException as e:
            logger.error("FiatException: {}".format(str(e)))
            self.live_on = False
            await self.bot.say(e)
        except Exception as e:
            await self.bot.say("Command failed. Make sure the arguments are valid.")
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def calculate_fiat_to_coin(self, currency, price, fiat):
        """
        Calculates coin to fiat rate and displays it

        @param currency - cryptocurrency that was bought
        @param currency_amt - amount of currency coins
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        try:
            ucase_fiat = self.coin_market.fiat_check(fiat)
            if currency.upper() in self.acronym_list:
                currency = self.acronym_list[currency.upper()]
            data = self.market_list[currency]
            current_cost = float(data['price_usd'])
            amt_of_coins = "{:.8f}".format(price/current_cost)
            amt_of_coins = amt_of_coins.rstrip('0')
            price = self.coin_market.format_price(price, ucase_fiat)
            currency = currency.title()
            result = "**{}** is worth **{} {}**".format(price,
                                                        amt_of_coins,
                                                        currency)
            em = discord.Embed(title="{} to {}({})".format(ucase_fiat,
                                                           currency,
                                                           data['symbol']),
                               description=result,
                               colour=0xFFD700)
            await self.bot.say(embed=em)
        except Forbidden:
            pass
        except CurrencyException as e:
            logger.error("CurrencyException: {}".format(str(e)))
            self.live_on = False
            await self.bot.say(e)
        except FiatException as e:
            logger.error("FiatException: {}".format(str(e)))
            self.live_on = False
            await self.bot.say(e)
        except Exception as e:
            await self.bot.say("Command failed. Make sure the arguments are valid.")
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def calculate_profit(self, currency, currency_amt, cost, fiat):
        """
        Performs profit calculation operation and displays it

        @param currency - cryptocurrency that was bought
        @param currency_amt - amount of currency coins
        @param cost - the price of the cryptocurrency bought at the time
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        try:
            ucase_fiat = self.coin_market.fiat_check(fiat)
            if currency.upper() in self.acronym_list:
                currency = self.acronym_list[currency.upper()]
            data = self.market_list[currency]
            current_cost = float(data['price_usd'])
            initial_investment = float(currency_amt)*float(cost)
            profit = float((float(currency_amt)*current_cost) - initial_investment)
            overall_investment = float(initial_investment + profit)
            currency = currency.title()
            formatted_initial_investment = self.coin_market.format_price(initial_investment,
                                                                         ucase_fiat)
            formatted_profit = self.coin_market.format_price(profit, ucase_fiat)
            formatted_overall_investment = self.coin_market.format_price(overall_investment,
                                                                         ucase_fiat)
            msg = ("Initial Investment: **{}** (**{}** coin(s), costs **{}** each)\n"
                   "Profit: **{}**\n"
                   "Total investment worth: **{}**".format(formatted_initial_investment,
                                                           currency_amt,
                                                           cost,
                                                           formatted_profit,
                                                           formatted_overall_investment))
            color = 0xD14836 if profit < 0 else 0x009993
            em = discord.Embed(title="Profit calculated ({})".format(currency),
                               description=msg,
                               colour=color)
            await self.bot.say(embed=em)
        except Forbidden:
            pass
        except CurrencyException as e:
            logger.error("CurrencyException: {}".format(str(e)))
            self.live_on = False
            await self.bot.say(e)
        except FiatException as e:
            logger.error("FiatException: {}".format(str(e)))
            self.live_on = False
            await self.bot.say(e)
        except Exception as e:
            await self.bot.say("Command failed. Make sure the arguments are valid.")
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    def _save_subscriber_file(self):
        """
        Saves subscribers.json file
        """
        with open('subscribers.json', 'w') as outfile:
            json.dump(self.subscriber_data,
                      outfile,
                      indent=4)

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
                self._save_subscriber_file()
                num_channels = len(subscriber_list)
                game_status = discord.Game(name="with {} subscriber(s)".format(num_channels))
                await self.bot.change_presence(game=game_status)
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
                self._save_subscriber_file()
                num_channels = len(subscriber_list)
                game_status = discord.Game(name="with {} subscriber(s)".format(num_channels))
                await self.bot.change_presence(game=game_status)
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
            self._save_subscriber_file()
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
                await self.bot.say("Channel was never subscribed.")
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
                self._save_subscriber_file()
                await self.bot.say("``{}`` was successfully added.".format(currency.title()))
            else:
                await self.bot.say("The channel needs to be subscribed first.")
        except Forbidden:
            pass
        except CurrencyException as e:
            logger.error("CurrencyException: {}".format(str(e)))
            await self.bot.say(e)
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
                    self._save_subscriber_file()
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
            await self.bot.say(e)
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    def _translate_operation_(self, operator):
        """
        Translates the supported operations for alerts
        into english

        @param operator - operator condition to notify the channel
        """
        if operator in self.supported_operators:
            if operator == "<":
                operator_translation = "less than"
            elif operator == "<=":
                operator_translation = "less than or equal to"
            elif operator == ">":
                operator_translation = "greater than"
            elif operator == ">=":
                operator_translation = "greater than or equal to"
            return operator_translation
        else:
            raise Exception("Unable to translate operation.")

    def _check_alert_(self, currency, operator, price, fiat):
        """
        Checks if the alert condition isn't true

        @param currency - cryptocurrency to set an alert of
        @param operator - operator condition to notify the channel
        @param price - price for condition to compare
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        @return - True if condition doesn't exist, False if it does
        """
        market_price = float(self.market_list[currency]["price_usd"])
        market_price = float(self.coin_market.format_price(market_price,
                                                           fiat,
                                                           False))
        if operator in self.supported_operators:
            if operator == "<":
                if market_price < float(price):
                    return False
            elif operator == "<=":
                if market_price <= float(price):
                    return False
            elif operator == ">":
                if market_price > float(price):
                    return False
            elif operator == ">=":
                if market_price >= float(price):
                    return False
            return True
        else:
            raise Exception

    async def add_alert(self, ctx, currency, operator, price, fiat):
        """
        Adds an alert to alerts.json

        @param currency - cryptocurrency to set an alert of
        @param operator - operator condition to notify the channel
        @param price - price for condition to compare
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        try:
            i = 1
            alert_num = None
            ucase_fiat = self.coin_market.fiat_check(fiat)
            if currency.upper() in self.acronym_list:
                currency = self.acronym_list[currency.upper()]
                if "Duplicate" in currency:
                    await self.bot.say(currency)
                    return
            if currency not in self.market_list:
                raise CurrencyException("Currency is invalid: ``{}``".format(currency))
            try:
                if not self._check_alert_(currency, operator, price, ucase_fiat):
                    await self.bot.say("Failed to create alert. Current price "
                                       "of **{}** already meets the condition."
                                       "".format(currency.title()))
                    return
            except Exception:
                await self.bot.say("Invalid operator: **{}**".format(operator))
                return
            user_id = str(ctx.message.author.id)
            if user_id not in self.alert_data:
                self.alert_data[user_id] = {}
            while i <= len(self.alert_data[user_id]) + 1:
                if str(i) not in self.alert_data[user_id]:
                    alert_num = str(i)
                i += 1
            if alert_num is None:
                raise Exception("Something went wrong with adding alert.")
            alert_cap = int(self.subscriber_data["alert_capacity"])
            if int(alert_num) > alert_cap:
                await self.bot.say("Unable to add alert, user alert capacity of"
                                   " **{}** has been reached.".format(alert_cap))
                return
            alert_list = self.alert_data[user_id]
            alert_list[alert_num] = {}
            channel_alert = alert_list[alert_num]
            channel_alert["currency"] = currency
            if operator in self.supported_operators:
                channel_alert["operation"] = operator
            else:
                await self.bot.say("Invalid operator: {}. Your choices are **<*"
                                   "*, **<=**, **>**, or **>=**"
                                   "".format(operator))
                return
            channel_alert["price"] = ("{:.6f}".format(price)).rstrip('0')
            if channel_alert["price"].endswith('.'):
                channel_alert["price"] = channel_alert["price"].replace('.', '')
            channel_alert["fiat"] = ucase_fiat
            with open('alerts.json', 'w') as outfile:
                json.dump(self.alert_data,
                          outfile,
                          indent=4)
            await self.bot.say("Alert has been set.")
        except CurrencyException as e:
            logger.error("CurrencyException: {}".format(str(e)))
            await self.bot.say(e)
        except FiatException as e:
            logger.error("FiatException: {}".format(str(e)))
            self.live_on = False
            await self.bot.say(e)
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    def _save_alert_file_(self):
        """
        Saves alerts.json file
        """
        with open('alerts.json', 'w') as outfile:
            json.dump(self.alert_data,
                      outfile,
                      indent=4)

    async def remove_alert(self, ctx, alert_num):
        """
        Removes an alert from the user's list of alerts

        @param ctx - context of the command sent
        @param alert_num - number of the specific alert to remove
        """
        try:
            user_id = str(ctx.message.author.id)
            user_list = self.alert_data
            alert_list = user_list[user_id]
            if alert_num in alert_list:
                removed_alert = alert_num
                alert_setting = alert_list[alert_num]
                alert_currency = alert_setting["currency"]
                alert_operation = self._translate_operation_(alert_setting["operation"])
                alert_price = alert_setting["price"]
                alert_fiat = alert_setting["fiat"]
                alert_list.pop(str(alert_num))
                self._save_alert_file_()
                await self.bot.say("Alert **{}** where **{}** is **{}** **{}** "
                                   "in **{}** was successfully "
                                   "removed.".format(removed_alert,
                                                     alert_currency,
                                                     alert_operation,
                                                     alert_price,
                                                     alert_fiat))
            else:
                await self.bot.say("The number you've entered does not exist "
                                   "in the alert list. Use `$geta` to receive "
                                   "a list of ongoing alerts.")
        except Forbidden:
            pass
        except CurrencyException as e:
            logger.error("CurrencyException: {}".format(str(e)))
            await self.bot.say(e)
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def get_alert_list(self, ctx):
        """
        Gets the list of alerts and displays them

        @param ctx - context of the command sent
        """
        try:
            user_id = ctx.message.author.id
            user_list = self.alert_data
            msg = {}
            result_msg = ""
            if user_id in user_list:
                alert_list = user_list[user_id]
                if len(alert_list) != 0:
                    msg[0] = "The following alerts have been set:\n"
                    for alert in alert_list:
                        currency = alert_list[alert]["currency"].title()
                        operation = self._translate_operation_(alert_list[alert]["operation"])
                        msg[int(alert)] = ("[**{}**] Alert when **{}** is **{}** **{}** "
                                           "in **{}**\n".format(alert,
                                                                currency,
                                                                operation,
                                                                alert_list[alert]["price"],
                                                                alert_list[alert]["fiat"]))
                    for line in sorted(msg):
                        result_msg += msg[line]
                else:
                    result_msg = "Channel does not have any alerts to display."
            else:
                result_msg = "User never created any alerts."
            await self.bot.say(result_msg)
        except Forbidden:
            pass
        except CurrencyException as e:
            logger.error("CurrencyException: {}".format(str(e)))
            await self.bot.say(e)
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def _alert_user_(self):
        """
        Checks and displays alerts that have met the condition of the
        cryptocurrency price
        """
        try:
            raised_alerts = defaultdict(list)
            for user in self.alert_data:
                alert_list = self.alert_data[str(user)]
                for alert in alert_list:
                    alert_currency = alert_list[alert]["currency"]
                    operator_symbol = alert_list[alert]["operation"]
                    alert_operator = self._translate_operation_(operator_symbol)
                    alert_price = alert_list[alert]["price"]
                    alert_fiat = alert_list[alert]["fiat"]
                    if not self._check_alert_(alert_currency, operator_symbol,
                                              alert_price, alert_fiat):
                        raised_alerts[user].append(alert)
                        user_obj = await self.bot.get_user_info(user)
                        await self.bot.send_message(user_obj,
                                                    "Alert **{}**! "
                                                    "**{}** is **{}** **{}** "
                                                    "in **{}**"
                                                    "".format(alert,
                                                              alert_currency.title(),
                                                              alert_operator,
                                                              alert_price,
                                                              alert_fiat))
            if raised_alerts:
                for user in raised_alerts:
                    for alert_num in raised_alerts[user]:
                        self.alert_data[user].pop(str(alert_num))
                self._save_alert_file_()
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))
