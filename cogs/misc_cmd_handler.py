from discord.ext import commands


class MiscCommands:
    """Handles misc commands"""

    def __init__(self, cmd_function):
        self.cmd_function = cmd_function

    @commands.command(name="profile", pass_context=True)
    async def profile(self, ctx):
        """
        Shows bot profile
        An example for this command would be:
        "$profile"
        """
        await self.cmd_function.misc.display_bot_profile(ctx)

    @commands.command(name="updates", pass_context=True)
    async def updates(self, ctx):
        """
        Shows update log of the bot
        An example for this command would be:
        "$updates"
        """
        await self.cmd_function.misc.display_update_page(ctx)

    @commands.command(name="donate", pass_context=True)
    async def donate(self, ctx):
        """
        Shows donation options
        An example for this command would be:
        "$donate"
        """
        await self.cmd_function.misc.display_donation_option(ctx)

    @commands.command(name="info", pass_context=True)
    async def info(self, ctx):
        """
        Shows information about the bot
        An example for this command would be:
        "$info"
        """
        await self.cmd_function.misc.display_info(ctx)
