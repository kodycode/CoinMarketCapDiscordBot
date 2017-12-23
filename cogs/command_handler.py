from bot_logger import logger
from cogs.modules.coin_market import CoinMarket, CoinMarketException, CurrencyException, FiatException, MarketStatsException
from discord.ext import commands
import asyncio
import discord
import json


class CoinMarketCommand:
    """
    Handles all Coin Market Cap related commands
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
        """
        try:
            acronym_list, duplicate_count = self.coin_market.load_all_acronyms()
            print("Acronyms have successfully loaded.")
            logger.info("Acronyms have successfully loaded.")
            return acronym_list
        except CoinMarketException as e:
            print("Failed to load cryptocurrency acronyms. See error.log.")
            logger.error(str(e))
            return None

    async def display_search(self, currency, fiat):
        """
        Embeds search results and displays it in chat

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
            logger.error(str(e))
            await self.bot.say(e)
        except FiatException as e:
            error_msg = (str(e) +
                         "\nIf you're doing multiple searches, please "
                         "make sure there's no spaces after the comma.")
            logger.error(error_msg)
            await self.bot.say(error_msg)
        except CoinMarketException as e:
            print("An error has occured. See error.log.")
            logger.error(str(e))
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error(str(e))

    @commands.command(name='search')
    async def search(self, currency: str, fiat='USD'):
        """
        Displays the data of the specified currency.
        An example for this command would be:
        "$search bitcoin"

        @param currency - cryptocurrency to search for
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.display_search(currency, fiat)

    @commands.command(name='s')
    async def s(self, currency: str, fiat='USD'):
        """
        Shortcut for "$search" command.
        An example for this command would be:
        "$s bitcoin"

        @param currency - cryptocurrency to search for
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.display_search(currency, fiat)

    @commands.command(name='stats')
    async def stats(self, fiat='USD'):
        """
        Displays the market stats.
        An example for this command would be:
        "$stats"

        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        try:
            data = await self.coin_market.get_stats(fiat)
            em = discord.Embed(title="Market Stats",
                               description=data,
                               colour=0x008000)
            await self.bot.say(embed=em)
        except MarketStatsException as e:
            logger.error(str(e))
            await self.bot.say(e)
        except FiatException as e:
            logger.error(str(e))
            await self.bot.say(e)
        except CoinMarketException as e:
            print("An error has occured. See error.log.")
            logger.error(str(e))
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error(str(e))

    @commands.command(name='live')
    async def live(self, fiat='USD'):
        """
        Displays live updates of coin stats in n-second intervals.
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
            logger.error(str(e))
            self.live_on = False
            await self.bot.say(e)
        except FiatException as e:
            logger.error(str(e))
            self.live_on = False
            await self.bot.say(e)
        except CoinMarketException as e:
            print("An error has occured. See error.log.")
            logger.error(str(e))
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error(str(e))


def setup(bot):
    bot.add_cog(CoinMarketCommand(bot))
