from coinmarketcap import Market
from currency_converter import CurrencyConverter

fiat_currencies = {
    'AUD': '$', 'BRL': 'R$', 'CAD': '$', 'CHF': 'Fr.',
    'CLP': '$', 'CNY': '¥', 'CZK': 'Kc', 'DKK': 'kr',
    'EUR': '€', 'GBP': '£', 'HKD': 'HK$', 'HUF': 'Ft',
    'IDR': 'Rp ', 'ILS': '₪', 'INR': '₹', 'JPY': '¥‎',
    'KRW': '₩', 'MXN': '$', 'MYR': 'RM', 'NOK': 'kr',
    'NZD': '$', 'PHP': '₱', 'PKR': 'Rupees', 'PLN': 'zł',
    'RUB': '₽', 'SEK': 'kr', 'SGD': 'S$', 'THB': '฿',
    'TRY': '₺', 'TWD': 'NT$', 'ZAR': 'R ', 'USD': '$'
}

fiat_suffix = [
    'CZK', 'DKK', 'HUF',
    'NOK', 'PKR', 'RUB',
    'SEK'
]


class CurrencyException(Exception):
    """Exception class for invalid currencies"""


class CoinMarketException(Exception):
    """Exception class for CoinMarket"""


class FiatException(Exception):
    """Exception class for invalid fiat"""


class MarketStatsException(Exception):
    """Exception class for invalid retrieval of market stats"""


class CoinMarket:
    """Handles CoinMarketCap API features"""

    def __init__(self):
        """
        Initiates CoinMarket

        @param bot - discord bot object
        """
        self.market = Market()

    def fiat_check(self, fiat):
        """
        Checks if fiat is valid. If invalid, raise FiatException error.

        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        @return - uppercase fiat
        """
        if fiat is not fiat.upper():
            fiat = fiat.upper()
        if fiat not in fiat_currencies:
            error_msg = "This fiat currency is not supported: `{}`".format(fiat)
            raise FiatException(error_msg)
        return fiat

    def format_price(self, price, fiat, symbol=True):
        """
        Formats price under the desired fiat

        @param price - price to format
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        @param symbol - if True add currency symbol to fiat
                        if False symbol will not be added
        @return - formatted price under fiat
        """
        c = CurrencyConverter()
        ucase_fiat = fiat.upper()
        if fiat is not "USD":
            price = float(c.convert(float(price), "USD", fiat))
        if symbol:
            if ucase_fiat in fiat_suffix:
                formatted_fiat = "{:,.6f} {}".format(float(price),
                                                     fiat_currencies[ucase_fiat])
            else:
                formatted_fiat = "{}{:,.6f}".format(fiat_currencies[ucase_fiat],
                                                    float(price))
        else:
            formatted_fiat = str(price)
        formatted_fiat = formatted_fiat.rstrip('0')
        if formatted_fiat.endswith('.'):
            formatted_fiat = formatted_fiat.replace('.', '')
        return formatted_fiat

    def fetch_currency_data(self, currency="", fiat="", load_all=False):
        """
        Fetches the currency data based on the desired currency

        @param currency - the cryptocurrency to search for (i.e. 'bitcoin',
                          'ethereum')
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        @param load_all - True: load all cryptocurrencies
                          False: don't load all cryptocurrencies
        @return - currency data
        """
        try:
            if load_all:
                return self.market.ticker(start=0, limit=0)
            return self.market.ticker(currency, convert=fiat)
        except Exception as e:
            raise CurrencyException("Failed to find currency: `{}`. Check "
                                    "if this currency is valid and also check "
                                    "for spelling errors.".format(currency))

    def _format_currency_data(self, data, fiat, single_search=True):
        """
        Formats the data fetched

        @param currency - the cryptocurrency to search for (i.e. 'bitcoin',
                          'ethereum')
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        @param single_search - separate more lines if True
        @return - formatted currency data
        """
        try:
            price = CurrencyConverter()
            isPositivePercent = True
            formatted_data = ''
            hour_trend = ''
            if float(data['percent_change_24h']) >= 0:
                hour_trend = '<:small_green_triangle:396586561413578752>'
            else:
                hour_trend = ':small_red_triangle_down:'
                isPositivePercent = False

            formatted_data += '__**#{}. {} ({})**__ {}\n'.format(data['rank'],
                                                                 data['name'],
                                                                 data['symbol'],
                                                                 hour_trend)
            if fiat is not "USD":
                converted_price = float(price.convert(float(data['price_usd']),
                                                      'USD',
                                                      fiat))
            converted_price = "{:,.6f}".format(converted_price).rstrip('0')
            if converted_price.endswith('.'):
                converted_price = converted_price.replace('.', '')
            if fiat in fiat_suffix:
                formatted_data += 'Price ({}): **{} {}**\n'.format(fiat,
                                                                   converted_price,
                                                                   fiat_currencies[fiat])
            else:
                formatted_data += 'Price ({}): **{}{}**\n'.format(fiat,
                                                                  fiat_currencies[fiat],
                                                                  converted_price)
            formatted_data += 'Price (BTC): **{:,}**\n'.format(float(data['price_btc']))
            if single_search:
                formatted_data += '\n'
            if (data['market_cap_usd'] is None):
                formatted_data += 'Market Cap ({}): Unknown\n'.format(fiat)
            else:
                converted_price = float(price.convert(float(data['market_cap_usd']),
                                                      'USD',
                                                      fiat))
                formatted_data += 'Market Cap ({}): **${:,}**\n'.format(fiat,
                                                                        converted_price)
            if (data['available_supply'] is None):
                formatted_data += 'Available Supply: Unknown\n'
            else:
                formatted_data += 'Available Supply: **{:,}**\n'.format(float(data['available_supply']))
            if single_search:
                formatted_data += '\n'
            formatted_data += 'Percent Change (1H): **{}%**\n'.format(data['percent_change_1h'])
            formatted_data += 'Percent Change (24H): **{}%**\n'.format(data['percent_change_24h'])
            formatted_data += 'Percent Change (7D): **{}%**\n'.format(data['percent_change_7d'])
            return formatted_data, isPositivePercent
        except Exception as e:
            raise CoinMarketException("Failed to format data: {}".format(e))

    def get_currency(self, acronym_list, currency, fiat):
        """
        Obtains the data of the specified currency and returns them.

        @param acronym_list - list of cryptocurrency acronyms
        @param currency - the cryptocurrency to search for (i.e. 'bitcoin',
                          'ethereum')
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        try:
            isPositivePercent = False
            fiat = self.fiat_check(fiat)
            if currency.upper() in acronym_list:
                try:
                    data = self.fetch_currency_data(acronym_list[currency.upper()], fiat)[0]
                except CurrencyException:
                    formatted_data = acronym_list[currency.upper()]
                    return formatted_data, isPositivePercent
            else:
                data = self.fetch_currency_data(currency, fiat)[0]
            formatted_data, isPositivePercent = self._format_currency_data(data, fiat)
            return formatted_data, isPositivePercent
        except CurrencyException as e:
            raise
        except FiatException as e:
            raise
        except Exception as e:
            raise CoinMarketException(e)

    def get_current_currency(self, market_list, acronym_list, currency, fiat):
        """
        Obtains the data of the specified currency and returns them using
        the current updated market list

        @param market_list - list of entire crypto market
        @param acronym_list - list of cryptocurrency acronyms
        @param currency - the cryptocurrency to search for (i.e. 'bitcoin',
                          'ethereum')
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        try:
            isPositivePercent = False
            fiat = self.fiat_check(fiat)
            if currency.upper() in acronym_list:
                currency = acronym_list[currency.upper()]
                if "Duplicate" in currency:
                    return currency, isPositivePercent
            if currency not in market_list:
                raise CurrencyException("Invalid currency: `{}`".format(currency))
            data = market_list[currency]
            formatted_data, isPositivePercent = self._format_currency_data(data, fiat)
            return formatted_data, isPositivePercent
        except CurrencyException as e:
            raise
        except FiatException as e:
            raise
        except Exception as e:
            raise CoinMarketException(e)

    def fetch_coinmarket_stats(self, fiat=''):
        """
        Fetches the coinmarket stats

        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        @return - market stats
        """
        try:
            return self.market.stats(convert=fiat)
        except Exception as e:
            raise MarketStatsException("Unable to retrieve crypto market stats "
                                       "at this time.")

    def _format_coinmarket_stats(self, stats, fiat):
        """
        Receives and formats coinmarket stats

        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        @return - formatted stats
        """
        try:
            c = CurrencyConverter()
            formatted_stats = ''
            if (stats['total_market_cap_usd'] is None):
                formatted_stats += "Total Market Cap (USD): Unknown"
            else:
                if fiat is not "USD":
                    converted_price = c.convert(float(stats['total_market_cap_usd']), 'USD', fiat)
                if fiat in fiat_suffix:
                    formatted_stats += "Total Market Cap ({}): **{:,} {}**\n".format(fiat,
                                                                                     converted_price,
                                                                                     fiat_currencies[fiat])
                else:
                    formatted_stats += "Total Market Cap ({}): **{}{:,}**\n".format(fiat,
                                                                                    fiat_currencies[fiat],
                                                                                    converted_price)
            formatted_stats += "Bitcoin Percentage of Market: **{:,}%**\n".format(stats['bitcoin_percentage_of_market_cap'])
            formatted_stats += "Active Markets: **{:,}**\n".format(stats['active_markets'])
            formatted_stats += "Active Currencies: **{:,}**\n".format(stats['active_currencies'])
            formatted_stats += "Active Assets: **{:,}**\n".format(stats['active_assets'])

            return formatted_stats
        except Exception as e:
            raise CoinMarketException("Failed to format data: `{}`".format(e))

    def get_stats(self, fiat):
        """
        Returns the market stats

        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        @return - formatted market stats
        """
        try:
            fiat = self.fiat_check(fiat)
            stats = self.fetch_coinmarket_stats(fiat)
            formatted_stats = self._format_coinmarket_stats(stats, fiat)
            return formatted_stats
        except FiatException as e:
            raise
        except MarketStatsException as e:
            raise
        except Exception as e:
            raise CoinMarketException(e)

    def get_current_stats(self, market_stats, fiat):
        """
        Returns the market stats

        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        @return - formatted market stats
        """
        try:
            fiat = self.fiat_check(fiat)
            formatted_stats = self._format_coinmarket_stats(market_stats, fiat)
            return formatted_stats
        except FiatException as e:
            raise
        except MarketStatsException as e:
            raise
        except Exception as e:
            raise CoinMarketException(e)

    def get_multiple_currency(self, acronym_list, currency_list, fiat):
        """
        Returns updated info of multiple coin stats
        @param acronym_list - list of cryptocurrency acronyms
        @param currency_list - list of cryptocurrencies
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        @return - formatted cryptocurrency data
        """
        try:
            fiat = self.fiat_check(fiat)
            formatted_data = ''
            data_list = []
            for currency in currency_list:
                if acronym_list is not None:
                    if currency.upper() in acronym_list:
                        data_list.append(self.fetch_currency_data(acronym_list[currency.upper()], fiat)[0])
                    else:
                        data_list.append(self.fetch_currency_data(currency, fiat)[0])
                else:
                    data_list.append(self.fetch_currency_data(currency, fiat)[0])
            data_list.sort(key=lambda x: int(x['rank']))
            for data in data_list:
                formatted_data += self._format_currency_data(data, fiat, False)[0] + '\n'
            return formatted_data
        except CurrencyException as e:
            raise
        except FiatException as e:
            raise
        except Exception as e:
            raise CoinMarketException(e)

    def get_current_multiple_currency(self, market_list, acronym_list, currency_list, fiat):
        """
        Returns updated info of multiple coin stats using the current
        updated market list

        @param market_list - list of entire crypto market
        @param acronym_list - list of cryptocurrency acronyms
        @param currency_list - list of cryptocurrencies to retrieve
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        @return - list of formatted cryptocurrency data
        """
        try:
            fiat = self.fiat_check(fiat)
            formatted_data = []
            data_list = []
            result_msg = ''
            for currency in currency_list:
                try:
                    if currency.upper() in acronym_list:
                        currency = acronym_list[currency.upper()]
                        if "Duplicate" in currency:
                            return currency
                    data_list.append(market_list[currency])
                except:
                    raise CurrencyException("Invalid currency: `{}`".format(currency))
            data_list.sort(key=lambda x: int(x['rank']))
            for data in data_list:
                formatted_msg = self._format_currency_data(data, fiat, False)[0]
                if len(result_msg + formatted_msg) < 2000:
                    result_msg += formatted_msg + '\n'
                else:
                    formatted_data.append(result_msg)
                    result_msg = '{}'.format(formatted_msg)
            formatted_data.append(result_msg)
            return formatted_data
        except CurrencyException as e:
            raise
        except FiatException as e:
            raise
        except Exception as e:
            raise CoinMarketException(e)
