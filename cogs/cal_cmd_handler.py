from discord.ext import commands


class CalCommands:
    """Handles coinmarketcal commands"""

    def __init__(self, cmd_function):
        self.cmd_function = cmd_function

    @commands.command(name="cal")
    async def cal(self, currency, event_num=1):
        """
        Shows an upcoming event for the coin given
        An example for this command would be:
        "$cal"

        @param currency - requested cryptocurrency
        @param event_num - number in the event list to get
                           information on
                           (default is first/upcoming event)
        """
        await self.cmd_function.cal.display_event(currency, event_num)
