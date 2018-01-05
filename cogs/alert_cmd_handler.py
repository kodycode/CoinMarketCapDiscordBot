from discord.ext import commands


class AlertCommands:
    """Handles commands for alert notifications of crypto prices"""

    def __init__(self, cmd_function):
        self.cmd_function = cmd_function

    @commands.command(name='adda', pass_context=True)
    async def adda(self, ctx, currency: str, operator: str, price: float, fiat='USD'):
        """
        Adds an alert notification for the user when a price meets the condition specified
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
        await self.cmd_function.add_alert(ctx, currency, operator, price, fiat)

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
        await self.cmd_function.remove_alert(ctx, alert_num)

    @commands.command(name='geta', pass_context=True)
    async def geta(self, ctx):
        """
        Gets the list of alerts made from the user
        An example for this command would be:
        "$geta"

        @param ctx - context of the command sent
        """
        await self.cmd_function.get_alert_list(ctx)
