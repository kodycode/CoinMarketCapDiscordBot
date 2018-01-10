from bot_logger import logger
from cogs.modules.alert_functionality import AlertFunctionality
from cogs.modules.coin_market_functionality import CoinMarketFunctionality
from cogs.modules.coin_market import CoinMarket
from cogs.modules.subscriber_functionality import SubscriberFunctionality
import asyncio
import datetime
import json
import re


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
        self.cmc = CoinMarketFunctionality(bot, self.coin_market)
        self.alert = AlertFunctionality(bot,
                                        self.coin_market,
                                        self.config_data["alert_capacity"])
        self.subscriber = SubscriberFunctionality(bot, self.coin_market)
        self.bot.loop.create_task(self._continuous_updates())

    async def _update_data(self, minute=0):
        try:
            await self._update_market()
            self._load_acronyms()
            self.cmc.update(self.market_list,
                            self.acronym_list,
                            self.market_stats)
            self.alert.update(self.market_list, self.acronym_list)
            self.subscriber.update(self.market_list, self.acronym_list)
            await self.alert.alert_user()
            if self.started:
                await self.subscriber.display_live_data(minute)
        except Exception as e:
            print("Failed to update data. See error.log.")
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
            self.acronym_list = acronym_list
        except Exception as e:
            print("Failed to load cryptocurrency acronyms. See error.log.")
            logger.error("Exception: {}".format(str(e)))
