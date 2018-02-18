from discord.ext import commands


class AlertCommands:
    """Handles commands for alert notifications of crypto prices"""

    def __init__(self, cmd_function):
        self.cmd_function = cmd_function

    @commands.command(name='adda', pass_context=True)
    async def adda(self, ctx, currency: str, operator: str, price: float, fiat='USD'):
        """
        Adds alert for when the price of crypto meets the condition given
        An example for this command would be:
        "$adda bitcoin <= 15000"

        @param currency - cryptocurrency to set an alert of
        @param operator - operator for the given choices
                          <  - less than
                          <= - less than or equal to
                          >  - greater than
                          >= - greater than or equal to
        @param price - price for condition to compare
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.cmd_function.alert.add_alert(ctx, currency, operator, price, fiat)

    @commands.command(name='addab', pass_context=True)
    async def addab(self, ctx, currency: str, operator: str, btc_price: float):
        """
        Adds alert for when the btc price of crypto meets the condition given
        An example for this command would be:
        "$addab litecoin > 0.02"

        @param currency - cryptocurrency to set an alert of
        @param operator - operator for the given choices
                          <  - less than
                          <= - less than or equal to
                          >  - greater than
                          >= - greater than or equal to
        @param btc_price - btc price for condition to compare
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.cmd_function.alert.add_alert(ctx, currency, operator, btc_price, "USD", btc=True)

    @commands.command(name='addah', pass_context=True)
    async def addahour(self, ctx, currency: str, operator: str, percent: float, fiat='USD'):
        """
        Adds alert for when percent change in 1h of crypto meets the condition given
        An example for this command would be:
        "$addah bitcoin >= 2.5"

        @param currency - cryptocurrency to set an alert of
        @param operator - operator for the given choices
                          <  - less than
                          <= - less than or equal to
                          >  - greater than
                          >= - greater than or equal to
        @param price - percent of 1h change to compare
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.cmd_function.alert.add_alert(ctx, currency, operator, percent, fiat, hour=True)

    @commands.command(name='addad', pass_context=True)
    async def addaday(self, ctx, currency: str, operator: str, percent: float, fiat='USD'):
        """
        Adds alert for when percent change in 24h of crypto meets the condition given
        An example for this command would be:
        "$addad bitcoin >= 2.5"

        @param currency - cryptocurrency to set an alert of
        @param operator - operator for the given choices
                          <  - less than
                          <= - less than or equal to
                          >  - greater than
                          >= - greater than or equal to
        @param price - percent of a day's change to compare
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.cmd_function.alert.add_alert(ctx, currency, operator, percent, fiat, day=True)

    @commands.command(name='addaw', pass_context=True)
    async def addaweek(self, ctx, currency: str, operator: str, percent: float, fiat='USD'):
        """
        Adds alert for when percent change in 7d of crypto meets the condition given
        An example for this command would be:
        "$addaw bitcoin >= 2.5"

        @param currency - cryptocurrency to set an alert of
        @param operator - operator for the given choices
                          <  - less than
                          <= - less than or equal to
                          >  - greater than
                          >= - greater than or equal to
        @param price - percent of a week's change to compare
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.cmd_function.alert.add_alert(ctx, currency, operator, percent, fiat, week=True)

    @commands.command(name='rema', pass_context=True)
    async def rema(self, ctx, alert_num: str):
        """
        Removes an alert notification made from the user
        Use $geta to see what alert number's you can remove first.
        An example for this command would be:
        "$rema 5"

        @param ctx - context of the command sent
        @param alert_num - number of the specific alert to remove
        """
        await self.cmd_function.alert.remove_alert(ctx, alert_num)

    @commands.command(name='geta', pass_context=True)
    async def geta(self, ctx):
        """
        Gets the list of alerts made from the user
        An example for this command would be:
        "$geta"

        @param ctx - context of the command sent
        """
        await self.cmd_function.alert.get_alert_list(ctx)
