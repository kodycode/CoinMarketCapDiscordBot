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
        await self.cmd_function.subscriber.add_subscriber(ctx, fiat)

    @commands.command(name='unsub', pass_context=True)
    async def unsubscribe(self, ctx):
        """
        Unsubscribes the channel from live updates.
        An example for this command would be:
        "$sub"

        @param ctx - context of the command sent
        """
        await self.cmd_function.subscriber.remove_subscriber(ctx)

    @commands.command(name='getc', pass_context=True)
    async def getc(self, ctx):
        """
        Gets the currencies the channel is currently subscribed to
        An example for this command would be:
        "$getc"

        @param ctx - context of the command sent
        """
        await self.cmd_function.subscriber.get_sub_currencies(ctx)

    @commands.command(name='addc', pass_context=True)
    async def addc(self, ctx, currency: str):
        """
        Adds a cryptocurrency to display in live updates
        An example for this command would be:
        "$addc bitcoin"

        @param ctx - context of the command sent
        @param currency - the cryptocurrency to add
        """
        await self.cmd_function.subscriber.add_currency(ctx, currency)

    @commands.command(name='remc', pass_context=True)
    async def remc(self, ctx, currency: str):
        """
        Removes a cryptocurrency from being displayed in live updates
        An example for this command would be:
        "$remc bitcoin"

        @param ctx - context of the command sent
        @param currency - the cryptocurrency to add
        """
        await self.cmd_function.subscriber.remove_currency(ctx, currency)

    @commands.command(name='purge', pass_context=True)
    async def purge(self, ctx):
        """
        Enables the bot to purge messages from the channel
        An example for this command would be:
        "$purge"

        @param ctx - context of the command sent
        """
        await self.cmd_function.subscriber.toggle_purge(ctx)

    @commands.command(name='interval', pass_context=True)
    async def interval(self, ctx, rate: str):
        """
        Sets the interval of how often the bot should post
        (Interval begins at midnight)
        An example for this command would be:
        "$interval hourly"

        Possible rate inputs currently are:
        "default" - posts every 5 minutes
        "half" - posts at every half-hour mark
        "hourly" - posts at every hour mark
        "2h" - posts every 2 hours
        "3h" - posts every 3 hours
        "6h" - posts every 6 hours
        "12h" - posts every 12 hours
        "24h" - posts every 24 hours

        @param ctx - context of the command sent
        @param rate - rate at which the bot should post
        """
        await self.cmd_function.subscriber.set_live_update_interval(ctx,
                                                                    rate)

    @commands.command(name='subset', pass_context=True)
    async def substats(self, ctx):
        """
        Gets subscriber settings
        """
        await self.cmd_function.subscriber.get_subset(ctx)
