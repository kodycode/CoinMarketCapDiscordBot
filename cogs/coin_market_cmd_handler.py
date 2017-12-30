from bot_logger import logger
from cogs.modules.coin_market import CoinMarket, CoinMarketException, CurrencyException, FiatException, MarketStatsException
from discord.ext import commands
import asyncio
import datetime
import discord
import json
import re


class CoinMarketCommands:
    """
    Handles all CMC related commands
    """
    def __init__(self, cmd_function):
        self.cmd_function = cmd_function

    @commands.command(name='search')
    async def search(self, currency: str, fiat='USD'):
        """
        Displays the data of the specified currency.
        An example for this command would be:
        "$search bitcoin"

        @param currency - cryptocurrency to search for
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.cmd_function.display_search(currency, fiat)

    @commands.command(name='s', hidden=True)
    async def s(self, currency: str, fiat='USD'):
        """
        Shortcut for "$search" command.
        An example for this command would be:
        "$s bitcoin"

        @param currency - cryptocurrency to search for
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.cmd_function.display_search(currency, fiat)

    @commands.command(name='stats')
    async def stats(self, fiat='USD'):
        """
        Displays the market stats.
        An example for this command would be:
        "$stats"

        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.cmd_function.display_stats(fiat)

    @commands.command(name='profit')
    async def profit(self, currency: str, currency_amt: float, cost: float, fiat='USD'):
        """
        Calculates and displays profit made from buying cryptocurrency.
        An example for this command would be:
        "$profit bitcoin 500 999"

        @param currency - cryptocurrency that was bought
        @param currency_amt - amount of currency coins
        @param cost - the price of the cryptocurrency bought at the time
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.cmd_function.calculate_profit(currency,
                                                 currency_amt,
                                                 cost,
                                                 fiat)

    @commands.command(name='p', hidden=True)
    async def p(self, currency: str, currency_amt: float, cost: float, fiat='USD'):
        """
        Shortcut for $profit command.

        @param currency - cryptocurrency that was bought
        @param currency_amt - amount of currency coins
        @param cost - the price of the cryptocurrency bought at the time
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.cmd_function.calculate_profit(currency,
                                                 currency_amt,
                                                 cost,
                                                 fiat)

    @commands.command(name='cb')
    async def cb(self, currency1: str, currency2: str, currency_amt: float):
        """
        Displays conversion from one cryptocurrency to another
        An example for this command would be:
        "$cc bitcoin litecoin 500"

        @param currency1 - currency to convert from
        @param currency2 - currency to convert to
        @param currency_amt - amount of currency1 to convert
                              to currency2
        """
        await self.cmd_function.calculate_coin_to_coin(currency1,
                                                       currency2,
                                                       currency_amt)

    @commands.command(name='cc')
    async def cc(self, currency: str, currency_amt: float, fiat='USD'):
        """
        Displays conversion from coins to fiat.
        An example for this command would be:
        "$cc bitcoin 500"

        @param currency - cryptocurrency that was bought
        @param currency_amt - amount of currency coins
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.cmd_function.calculate_coin_to_fiat(currency,
                                                       currency_amt,
                                                       fiat)

    @commands.command(name='cf')
    async def cf(self, currency: str, price: float, fiat='USD'):
        """
        Displays conversion from fiat to coins.
        An example for this command would be:
        "$cf bitcoin 500"

        @param currency - cryptocurrency that was bought
        @param price - price amount you wish to convert to coins
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.cmd_function.calculate_fiat_to_coin(currency,
                                                       price,
                                                       fiat)


class SubscriberCommands:
    """
    Handles Subscriber commands for live updates
    """
    def __init__(self, cmd_function):
        self.cmd_function = cmd_function

    @commands.command(name='sub', pass_context=True)
    async def subscribe(self, ctx, fiat='USD'):
        """
        Subscribes the channel to live updates.
        An example for this command would be:
        "$sub"

        @param ctx - context of the command sent
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.cmd_function.add_subscriber(ctx, fiat)

    @commands.command(name='unsub', pass_context=True)
    async def unsubscribe(self, ctx):
        """
        Unsubscribes the channel from live updates.
        An example for this command would be:
        "$sub"

        @param ctx - context of the command sent
        """
        await self.cmd_function.remove_subscriber(ctx)

    @commands.command(name='addc', pass_context=True)
    async def addc(self, ctx, currency: str):
        """
        Adds a cryptocurrency to display in live updates
        An example for this command would be:
        "$addc bitcoin"

        @param ctx - context of the command sent
        """
        await self.cmd_function.add_currency(ctx, currency)

    @commands.command(name='remc', pass_context=True)
    async def remc(self, ctx, currency: str):
        """
        Removes a cryptocurrency from being displayed in live updates
        An example for this command would be:
        "$remc bitcoin"

        @param ctx - context of the command sent
        """
        await self.cmd_function.remove_currency(ctx, currency)

    @commands.command(name='purge', pass_context=True)
    async def purge(self, ctx):
        """
        Enables the bot to purge messages from the channel
        An example for this command would be:
        "$purge"
        """
        await self.cmd_function.toggle_purge(ctx)


class CoinMarketFunctionality:
    """
    Handles CMC command functionality
    """
    def __init__(self, bot):
        with open('config.json') as config:
            self.config_data = json.load(config)
        self.bot = bot
        self.market_list = None
        self.market_stats = None
        self.coin_market = CoinMarket()
        self.live_on = False
        asyncio.async(self._continuous_updates())

    @asyncio.coroutine
    def _update_data(self):
        self._update_market()
        if self.config_data['load_acronyms']:
            self.acronym_list = self._load_acronyms()
        yield from self._display_live_data()

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
            if ',' in currency:
                if ' ' in currency:
                    await self.bot.say("Don't include spaces in multi-coin search.")
                    return
                currency_list = currency.split(',')
                data = self.coin_market.get_current_multiple_currency(self.market_list,
                                                                      self.acronym_list,
                                                                      currency_list,
                                                                      fiat.upper())
                em = discord.Embed(title="Search results",
                                   description=data,
                                   colour=0xFFD700)
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
            remove_channels = []
            subscriber_list = self.config_data["subscriber_list"][0]
            for channel in subscriber_list:
                channel_settings = subscriber_list[channel][0]
                if channel_settings["currencies"]:
                    if channel_settings["purge"] is True:
                        try:
                            await self.bot.purge_from(self.bot.get_channel(channel),
                                                      limit=10)
                        except:
                            pass
                    data = self.coin_market.get_current_multiple_currency(self.market_list,
                                                                          self.acronym_list,
                                                                          channel_settings["currencies"],
                                                                          channel_settings["fiat"])
                    em = discord.Embed(title="Live Currency Update",
                                       description=data,
                                       colour=0xFFD700)
                    try:
                        await self.bot.send_message(self.bot.get_channel(channel),
                                                    embed=em)
                    except Exception as e:
                        remove_channels.append(channel)
                        logger.error("Something went wrong with this channel. "
                                     "This channel will now be removed.")
            if remove_channels:
                for channel in remove_channels:
                    if channel in subscriber_list:
                        subscriber_list.pop(channel)
                        with open('config.json', 'w') as outfile:
                            json.dump(self.config_data,
                                      outfile,
                                      indent=4)
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
            if currency1.upper() in self.acronym_list:
                acronym1 = currency1.upper()
                currency1 = self.acronym_list[currency1.upper()]
            if currency2.upper() in self.acronym_list:
                acronym2 = currency2.upper()
                currency2 = self.acronym_list[currency2.upper()]
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

    async def add_subscriber(self, ctx, fiat):
        """
        Adds channel to the live update subscriber list in config.json

        @param ctx - context of the command sent
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        try:
            ucase_fiat = self.coin_market.fiat_check(fiat)
            channel = str(ctx.message.channel.id)
            subscriber_list = self.config_data["subscriber_list"][0]
            try:
                self.bot.get_channel(channel).server  # validate channel
            except:
                await self.bot.say("Failed to add channel as a subscriber. "
                                   " Please make sure this channel is within a "
                                   "valid server.")
                return
            if channel not in subscriber_list:
                subscriber_list[channel] = [{}]
                channel_settings = subscriber_list[channel][0]
                channel_settings["purge"] = False
                channel_settings["fiat"] = ucase_fiat
                channel_settings["currencies"] = []
                with open('config.json', 'w') as outfile:
                    json.dump(self.config_data,
                              outfile,
                              indent=4)
                num_channels = len(subscriber_list)
                game_status = discord.Game(name="with {} subscriber(s)".format(num_channels))
                await self.bot.change_presence(game=game_status)
                await self.bot.say("Channel has succcesfully subscribed.")
            else:
                await self.bot.say("Channel is already subscribed.")
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def remove_subscriber(self, ctx):
        """
        Removes channel from the subscriber list in config.json

        @param ctx - context of the command sent
        """
        try:
            channel = ctx.message.channel.id
            subscriber_list = self.config_data["subscriber_list"][0]
            if channel in subscriber_list:
                subscriber_list.pop(channel)
                with open('config.json', 'w') as outfile:
                    json.dump(self.config_data,
                              outfile,
                              indent=4)
                num_channels = len(subscriber_list)
                game_status = discord.Game(name="with {} subscriber(s)".format(num_channels))
                await self.bot.change_presence(game=game_status)
                await self.bot.say("Channel has unsubscribed.")
            else:
                await self.bot.say("Channel was never subscribed.")
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def toggle_purge(self, ctx):
        """
        Turns purge mode on/off for the channel
        """
        try:
            channel = ctx.message.channel.id
            subscriber_list = self.config_data["subscriber_list"][0]
            self.bot.get_channel(channel).server  # validate channel
            if channel not in subscriber_list:
                await self.bot.say("Channel was never subscribed.")
                return
            channel_settings = subscriber_list[channel][0]
            channel_settings["purge"] = not channel_settings["purge"]
            with open('config.json', 'w') as outfile:
                json.dump(self.config_data,
                          outfile,
                          indent=4)
            if channel_settings["purge"]:
                await self.bot.say("Purge mode on. Bot will now purge messages upon"
                                   " live updates. Please make sure your bot has "
                                   "the right permissions to remove messages.")
            else:
                await self.bot.say("Purge mode off.")
        except Exception as e:
            await self.bot.say("Failed to set purge mode. Please make sure this"
                               " channel is within a valid server.")

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
            subscriber_list = self.config_data["subscriber_list"][0]
            if channel in subscriber_list:
                channel_settings = subscriber_list[channel][0]
                if currency in channel_settings["currencies"]:
                    await self.bot.say("``{}`` is already added.".format(currency.title()))
                    return
                channel_settings["currencies"].append(currency)
                with open('config.json', 'w') as outfile:
                    json.dump(self.config_data,
                              outfile,
                              indent=4)
                await self.bot.say("``{}`` was successfully added.".format(currency.title()))
            else:
                await self.bot.say("The channel needs to be subscribed first.")
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
            subscriber_list = self.config_data["subscriber_list"][0]
            if channel in subscriber_list:
                channel_settings = subscriber_list[channel][0]
                if currency in channel_settings["currencies"]:
                    channel_settings["currencies"].remove(currency)
                    with open('config.json', 'w') as outfile:
                        json.dump(self.config_data,
                                  outfile,
                                  indent=4)
                    await self.bot.say("``{}`` was successfully removed.".format(currency.title()))
                    return
                else:
                    await self.bot.say("``{}`` was never added or is invalid.".format(currency.title()))
            else:
                await self.bot.say("The channel needs to be subscribed first.")
        except CurrencyException as e:
            logger.error("CurrencyException: {}".format(str(e)))
            await self.bot.say(e)
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))


def setup(bot):
    cmd_function = CoinMarketFunctionality(bot)
    bot.add_cog(CoinMarketCommands(cmd_function))
    bot.add_cog(SubscriberCommands(cmd_function))
