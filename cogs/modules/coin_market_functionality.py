from bot_logger import logger
from cogs.modules.coin_market import CoinMarketException, CurrencyException, FiatException, MarketStatsException
from discord.errors import Forbidden
import discord


class CoinMarketFunctionality:
    """Handles CMC command functionality"""

    def __init__(self, bot, coin_market):
        self.bot = bot
        self.acronym_list = ""
        self.market_list = ""
        self.market_stats = ""
        self.coin_market = coin_market

    def update(self, market_list, acronym_list, market_stats):
        """
        Updates utilities with new coin market data
        """
        self.market_list = market_list
        self.acronym_list = acronym_list
        self.market_stats = market_stats

    async def _say_error(self, e):
        """
        Bot will check and say the error if given correct permissions

        @param e - error object
        """
        try:
            await self.bot.say(e)
        except:
            pass

    async def display_search(self, args):
        """
        Embeds search results and displays it in chat.

        @param currency - cryptocurrency to search for
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        try:
            args = list(args)
            first_post = True
            currency = args[0]
            if len(args) == 1:
                fiat = 'USD'
            else:
                try:
                    fiat = self.coin_market.fiat_check(args.copy().pop())
                    args.pop()
                except FiatException:
                    fiat = 'USD'
                    pass
                if len(args) > 1:
                    data = self.coin_market.get_current_multiple_currency(self.market_list,
                                                                          self.acronym_list,
                                                                          args,
                                                                          fiat)
                    for msg in data:
                        if first_post:
                            em = discord.Embed(title="Search results",
                                               description=msg,
                                               colour=0xFF9900)
                            first_post = False
                        else:
                            em = discord.Embed(description=msg,
                                               colour=0xFF9900)
                        await self.bot.say(embed=em)
                    return
            data, isPositivePercent = self.coin_market.get_current_currency(self.market_list,
                                                                            self.acronym_list,
                                                                            currency,
                                                                            fiat)
            if isPositivePercent:
                em = discord.Embed(title="Search results",
                                   description=data,
                                   colour=0x00FF00)
            else:
                em = discord.Embed(title="Search results",
                                   description=data,
                                   colour=0xD14836)
            await self.bot.say(embed=em)
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
            await self._say_error(e)
        except FiatException as e:
            logger.error("FiatException: {}".format(str(e)))
            await self._say_error(e)
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
            else:
                acronym1 = self.market_list[currency1]["symbol"]
            if currency2.upper() in self.acronym_list:
                acronym2 = currency2.upper()
                currency2 = self.acronym_list[currency2.upper()]
            else:
                acronym2 = self.market_list[currency2]["symbol"]
            converted_amt = self.coin_market.get_converted_coin_amt(self.market_list,
                                                                    currency1,
                                                                    currency2,
                                                                    currency_amt)
            currency_amt = "{:.8f}".format(currency_amt).rstrip('0')
            currency_amt = currency_amt.rstrip('.')
            result = ("**{} {}** converts to **{} {}**"
                      "".format(currency_amt,
                                currency1.title(),
                                converted_amt,
                                currency2.title()))
            em = discord.Embed(title=("{}({}) to {}({})"
                                      "".format(currency1.title(),
                                                acronym1,
                                                currency2.title(),
                                                acronym2)),
                               description=result,
                               colour=0xFF9900)
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
                               colour=0xFF9900)
            await self.bot.say(embed=em)
        except Forbidden:
            pass
        except CurrencyException as e:
            logger.error("CurrencyException: {}".format(str(e)))
            await self._say_error(e)
        except FiatException as e:
            logger.error("FiatException: {}".format(str(e)))
            await self._say_error(e)
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
                               colour=0xFF9900)
            await self.bot.say(embed=em)
        except Forbidden:
            pass
        except CurrencyException as e:
            logger.error("CurrencyException: {}".format(str(e)))
            await self._say_error(e)
        except FiatException as e:
            logger.error("FiatException: {}".format(str(e)))
            await self._say_error(e)
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
            color = 0xD14836 if profit < 0 else 0x00FF00
            em = discord.Embed(title="Profit calculated ({})".format(currency),
                               description=msg,
                               colour=color)
            await self.bot.say(embed=em)
        except Forbidden:
            pass
        except CurrencyException as e:
            logger.error("CurrencyException: {}".format(str(e)))
            await self._say_error(e)
        except FiatException as e:
            logger.error("FiatException: {}".format(str(e)))
            await self._say_error(e)
        except Exception as e:
            await self.bot.say("Command failed. Make sure the arguments are valid.")
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))
