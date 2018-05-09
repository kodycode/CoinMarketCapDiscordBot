from discord.ext import commands


class CalCommands:
    """Handles coinmarketcal commands"""

    def __init__(self, cmd_function):
        self.cmd_function = cmd_function

    @commands.command(name="cal", pass_context=True)
    async def cal(self, coin, page_number):
        """
        Shows list of events for the coin given
        An example for this command would be:
        "$cal"
        """
        await self.cmd_function.cal.display_event(coin, page_number)