from discord.ext import commands


class SubscriberCommands:
    """Handles Subscriber commands for live updates"""

    def __init__(self, cmd_function):
        self.cmd_function = cmd_function

    @commands.command(name='sub', pass_context=True)
    async def subscribe(self, ctx, fiat='USD'):
        """
        Subscribes the channel to live updates.
        An example for this command would be:
        "$sub"

        @param ctx - context of the command sent
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        await self.cmd_function.add_subscriber(ctx, fiat)

    @commands.command(name='unsub', pass_context=True)
    async def unsubscribe(self, ctx):
        """
        Unsubscribes the channel from live updates.
        An example for this command would be:
        "$sub"

        @param ctx - context of the command sent
        """
        await self.cmd_function.remove_subscriber(ctx)

    @commands.command(name='getc', pass_context=True)
    async def getc(self, ctx):
        """
        Gets the currencies the channel is currently subscribed to
        An example for this command would be:
        "$getc"

        @param ctx - context of the command sent
        """
        await self.cmd_function.get_sub_currencies(ctx)

    @commands.command(name='addc', pass_context=True)
    async def addc(self, ctx, currency: str):
        """
        Adds a cryptocurrency to display in live updates
        An example for this command would be:
        "$addc bitcoin"

        @param ctx - context of the command sent
        @param currency - the cryptocurrency to add
        """
        await self.cmd_function.add_currency(ctx, currency)

    @commands.command(name='remc', pass_context=True)
    async def remc(self, ctx, currency: str):
        """
        Removes a cryptocurrency from being displayed in live updates
        An example for this command would be:
        "$remc bitcoin"

        @param ctx - context of the command sent
        @param currency - the cryptocurrency to add
        """
        await self.cmd_function.remove_currency(ctx, currency)

    @commands.command(name='purge', pass_context=True)
    async def purge(self, ctx):
        """
        Enables the bot to purge messages from the channel
        An example for this command would be:
        "$purge"

        @param ctx - context of the command sent
        """
        await self.cmd_function.toggle_purge(ctx)
