from discord.ext import commands


class CoinMarketCommands:
    """Handles all CMC related commands"""

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
        await self.cmd_function.cmc.display_search(currency, fiat)

    @commands.command(name='s', hidden=True)
    async def s(self, currency: str, fiat='USD'):
        """
        Shortcut for "$search" command.
        An example for this command would be:
        "$s bitcoin"

        @param currency - cryptocurrency to search for
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.cmd_function.cmc.display_search(currency, fiat)

    @commands.command(name='stats')
    async def stats(self, fiat='USD'):
        """
        Displays the market stats.
        An example for this command would be:
        "$stats"

        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.cmd_function.cmc.display_stats(fiat)

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
        await self.cmd_function.cmc.calculate_profit(currency,
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
        await self.cmd_function.cmc.calculate_profit(currency,
                                                     currency_amt,
                                                     cost,
                                                     fiat)

    @commands.command(name='cb')
    async def cb(self, currency1: str, currency2: str, currency_amt: float):
        """
        Displays conversion from one cryptocurrency to another
        An example for this command would be:
        "$cb bitcoin litecoin 500"

        @param currency1 - currency to convert from
        @param currency2 - currency to convert to
        @param currency_amt - amount of currency1 to convert
                              to currency2
        """
        await self.cmd_function.cmc.calculate_coin_to_coin(currency1,
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
        await self.cmd_function.cmc.calculate_coin_to_fiat(currency,
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
        await self.cmd_function.cmc.calculate_fiat_to_coin(currency,
                                                           price,
                                                           fiat)
