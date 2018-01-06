from bot_logger import logger
from cogs.modules.alert_functionality import AlertFunctionality
from cogs.modules.coin_market_functionality import CoinMarketFunctionality
from cogs.modules.coin_market import CoinMarket
from cogs.modules.subscriber_functionality import SubscriberFunctionality
import asyncio
import datetime
import json
import re


class CoreFunctionality:
    """Handles Core functionality"""

    def __init__(self, bot):
        with open('config.json') as config:
            self.config_data = json.load(config)
        self.bot = bot
        self.market_list = None
        self.market_stats = None
        self.acronym_list = None
        self.coin_market = CoinMarket()
        self.cmc = CoinMarketFunctionality(bot, self.coin_market)
        self.alert = AlertFunctionality(bot,
                                        self.coin_market,
                                        self.config_data["alert_capacity"])
        self.subscriber = SubscriberFunctionality(bot, self.coin_market)
        asyncio.async(self._continuous_updates_())

    @asyncio.coroutine
    def _update_data_(self):
        try:
            self._update_market_()
            self.acronym_list = self._load_acronyms_()
            self.cmc.update(self.market_list,
                            self.acronym_list,
                            self.market_stats)
            self.alert.update(self.market_list, self.acronym_list)
            self.subscriber.update(self.market_list, self.acronym_list)
            yield from self.subscriber.display_live_data()
            yield from self.alert._alert_user_()
            logger.info("Bot updated.")
        except Exception as e:
            print("Failed to update data. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    @asyncio.coroutine
    def _continuous_updates_(self):
        yield from self._update_data_()
        print('CoinMarketDiscordBot is online.')
        logger.info('Bot is online.')
        while True:
            time = datetime.datetime.now()
            if time.minute % 5 == 0:
                yield from self._update_data_()
                yield from asyncio.sleep(60)
            else:
                yield from asyncio.sleep(20)

    def _update_market_(self):
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
        except Exception as e:
            print("Failed to update market. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    def _load_acronyms_(self):
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
