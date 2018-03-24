from discord.ext import commands


class CoinMarketCommands:
    """Handles all CMC related commands"""

    def __init__(self, cmd_function):
        self.cmd_function = cmd_function

    @commands.command(name='search', pass_context=True)
    async def search(self, ctx, *args):
        """
        Displays the data of the specified currency.
        An example for this command would be:
        "$search bitcoin"
        or
        "$s bitcoin"
        or even
        "$bitcoin"

        @param currency - cryptocurrency to search for
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.cmd_function.cmc.display_search(ctx, args)

    @commands.command(name='s', pass_context=True, hidden=True)
    async def s(self, ctx, *args):
        """
        Shortcut for "$search" command.
        An example for this command would be:
        "$s bitcoin"

        @param currency - cryptocurrency to search for
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.cmd_function.cmc.display_search(ctx, args)

    @commands.command(name='stats', pass_context=True)
    async def stats(self, ctx, fiat='USD'):
        """
        Displays the market stats.
        An example for this command would be:
        "$stats"

        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.cmd_function.cmc.display_stats(ctx, fiat)

    @commands.command(name='profit', pass_context=True)
    async def profit(self, ctx, currency: str, currency_amt: float, cost: float, fiat='USD'):
        """
        Calculates and displays profit made from buying cryptocurrency.
        An example for this command would be:
        "$profit bitcoin 500 999"

        @param currency - cryptocurrency that was bought
        @param currency_amt - amount of currency coins
        @param cost - the price of the cryptocurrency bought at the time
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.cmd_function.cmc.calculate_profit(ctx,
                                                     currency,
                                                     currency_amt,
                                                     cost,
                                                     fiat)

    @commands.command(name='p', pass_context=True, hidden=True)
    async def p(self, ctx, currency: str, currency_amt: float, cost: float, fiat='USD'):
        """
        Shortcut for $profit command.

        @param currency - cryptocurrency that was bought
        @param currency_amt - amount of currency coins
        @param cost - the price of the cryptocurrency bought at the time
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.cmd_function.cmc.calculate_profit(ctx,
                                                     currency,
                                                     currency_amt,
                                                     cost,
                                                     fiat)

    @commands.command(name='cb', pass_context=True)
    async def cb(self, ctx, currency1: str, currency2: str, currency_amt: float):
        """
        Displays conversion from one cryptocurrency to another
        An example for this command would be:
        "$cb bitcoin litecoin 500"

        @param currency1 - currency to convert from
        @param currency2 - currency to convert to
        @param currency_amt - amount of currency1 to convert
                              to currency2
        """
        await self.cmd_function.cmc.calculate_coin_to_coin(ctx,
                                                           currency1,
                                                           currency2,
                                                           currency_amt)

    @commands.command(name='cc', pass_context=True)
    async def cc(self, ctx, currency: str, currency_amt: float, fiat='USD'):
        """
        Displays conversion from coins to fiat.
        An example for this command would be:
        "$cc bitcoin 500"

        @param currency - cryptocurrency that was bought
        @param currency_amt - amount of currency coins
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.cmd_function.cmc.calculate_coin_to_fiat(ctx,
                                                           currency,
                                                           currency_amt,
                                                           fiat)

    @commands.command(name='cf', pass_context=True)
    async def cf(self, ctx, currency: str, price: float, fiat='USD'):
        """
        Displays conversion from fiat to coins.
        An example for this command would be:
        "$cf bitcoin 500"

        @param currency - cryptocurrency that was bought
        @param price - price amount you wish to convert to coins
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.cmd_function.cmc.calculate_fiat_to_coin(ctx,
                                                           currency,
                                                           price,
                                                           fiat)
