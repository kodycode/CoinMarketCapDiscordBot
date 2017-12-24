from bot_logger import logger
from cogs.modules.coin_market import CoinMarket, CoinMarketException, CurrencyException, FiatException, MarketStatsException
from discord.ext import commands
import asyncio
import discord
import json


class CoinMarketCommand:
    """
    Handles all CMC related commands
    """
    def __init__(self, bot):
        self.cmd_function = CoinMarketFunctionality(bot)

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

    @commands.command(name='live')
    async def live(self, fiat='USD'):
        """
        Displays live updates of coin stats in n-second intervals.
        An example for this command would be:
        "$live"

        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.cmd_function.display_live_data(fiat)

    @commands.command(name='profit')
    async def profit(self, currency, currency_amt: float, cost: float, fiat='USD'):
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
    async def p(self, currency, currency_amt: float, cost: float, fiat='USD'):
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

    @commands.command(name='cc')
    async def cc(self, currency, currency_amt: float, fiat='USD'):
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


class CoinMarketFunctionality:
    """
    Handles CMC command functionality
    """
    def __init__(self, bot):
        with open('config.json') as config:
            self.config_data = json.load(config)
        self.bot = bot
        self.coin_market = CoinMarket()
        self.live_on = False
        self.crypto_acronyms = None
        if self.config_data['load_acronyms']:
            print("Loading cryptocurrency acronyms..")
            self.acronym_list = self._load_acronyms()

    def _load_acronyms(self):
        """
        Loads all acronyms of existing crypto-coins out there

        @return - list of acronyms
        """
        try:
            acronym_list, duplicate_count = self.coin_market.load_all_acronyms()
            print("Acronyms have successfully loaded.")
            logger.info("Acronyms have successfully loaded.")
            return acronym_list
        except CoinMarketException as e:
            print("Failed to load cryptocurrency acronyms. See error.log.")
            logger.error("CoinMarketException: {}".format(str(e)))
            return None

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
                data = await self.coin_market.get_multiple_currency(self.acronym_list,
                                                                    currency_list,
                                                                    fiat)
                em = discord.Embed(title="Search results",
                                   description=data,
                                   colour=0xFFD700)
            else:
                data, isPositivePercent = await self.coin_market.get_currency(self.acronym_list,
                                                                              currency,
                                                                              fiat)
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
            data = self.coin_market.fetch_currency_data(currency, ucase_fiat)[0]
            current_cost = float(data['price_{}'.format(fiat.lower())])
            fiat_cost = self.coin_market.format_price(currency_amt*current_cost,
                                                      fiat)
            currency = currency.title()
            result = "**{} {}** is worth **{}**".format(currency_amt,
                                                        data['symbol'],
                                                        str(fiat_cost))
            em = discord.Embed(title="{}({}) to {}".format(currency,
                                                           data['symbol'],
                                                           fiat.upper()),
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
            data = self.coin_market.fetch_currency_data(currency, ucase_fiat)[0]
            current_cost = float(data['price_{}'.format(fiat.lower())])
            initial_investment = float(currency_amt)*float(cost)
            profit = float((float(currency_amt)*current_cost) - initial_investment)
            overall_investment = float(initial_investment + profit)
            currency = currency.title()
            formatted_initial_investment = self.coin_market.format_price(initial_investment,
                                                                         fiat)
            formatted_profit = self.coin_market.format_price(profit, fiat).replace('$-', '-$')
            formatted_overall_investment = self.coin_market.format_price(overall_investment,
                                                                         fiat)
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

    async def display_stats(self, fiat):
        """
        Obtains the market stats to display

        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        try:
            data = await self.coin_market.get_stats(fiat)
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

    async def display_live_data(self, fiat):
        """
        Obtains and displays live updates of coin stats in n-second intervals.
        An example for this command would be:
        "$live"

        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        try:
            currency_list = self.config_data['live_check_currency']
            live_channel = self.config_data['live_channel']
            timer = self.config_data['live_update_interval']
            if not self.live_on:
                self.live_on = True
                while True:
                    try:
                        await self.bot.purge_from(self.bot.get_channel(live_channel),
                                                  limit=100)
                    except:
                        pass
                    data = await self.coin_market.get_multiple_currency(self.acronym_list,
                                                                        currency_list,
                                                                        fiat)
                    em = discord.Embed(title="Live Currency Update",
                                       description=data,
                                       colour=0xFFD700)
                    await self.bot.send_message(self.bot.get_channel(live_channel),
                                                embed=em)
                    await asyncio.sleep(float(timer))
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


def setup(bot):
    bot.add_cog(CoinMarketCommand(bot))
