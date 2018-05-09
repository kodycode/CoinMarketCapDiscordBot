from discord.ext import commands


CMB_ADMIN = "CMB ADMIN"
ADMIN_ONLY = "ADMIN_ONLY"
PREFIX_DISABLED = "PREFIX_DISABLED"
CMC_DISABLED = "CMC_DISABLED"
ALERT_DISABLED = "ALERT_DISABLED"
SUBSCRIBER_DISABLED = "SUBSCRIBER_DISABLED"
MISC_DISABLED = "MISC_DISABLED"
CAL_DISABLED = "CAL_DISABLED"


class AdminCommands:
    """Handles admin commands"""

    def __init__(self, cmd_function):
        self.cmd_function = cmd_function

    @commands.command(name='ss', pass_context=True)
    async def ss(self, ctx):
        """
        Obtains server settings
        An example for this command would be:
        "$ss"
        """
        await self.cmd_function.display_server_settings(ctx)

    @commands.command(name='admin', pass_context=True)
    async def admin(self, ctx):
        """
        Toggles admin mode
        An example for this command would be:
        "$admin"
        """
        await self.cmd_function.toggle_commands(ctx, ADMIN_ONLY)

    @commands.command(name='togglep', pass_context=True)
    async def togglep(self, ctx):
        """
        Toggles prefix command availability
        An example for this command would be:
        "$togglep"
        """
        await self.cmd_function.toggle_commands(ctx, PREFIX_DISABLED)

    @commands.command(name='togglec', pass_context=True)
    async def togglec(self, ctx):
        """
        Toggles cmc command availability
        An example for this command would be:
        "$togglec"
        """
        await self.cmd_function.toggle_commands(ctx, CMC_DISABLED)

    @commands.command(name='togglea', pass_context=True)
    async def togglea(self, ctx):
        """
        Toggles alert command availability
        An example for this command would be:
        "$togglea"
        """
        await self.cmd_function.toggle_commands(ctx, ALERT_DISABLED)

    @commands.command(name='toggles', pass_context=True)
    async def toggles(self, ctx):
        """
        Toggles subscriber command availability
        An example for this command would be:
        "$toggles"
        """
        await self.cmd_function.toggle_commands(ctx, SUBSCRIBER_DISABLED)

    @commands.command(name='togglem', pass_context=True)
    async def togglem(self, ctx):
        """
        Toggles misc command availability
        An example for this command would be:
        "$togglem"
        """
        await self.cmd_function.toggle_commands(ctx, MISC_DISABLED)

    @commands.command(name='togglecal', pass_context=True)
    async def togglecal(self, ctx):
        """
        Toggles calendar command availability
        An example for this command would be:
        "$togglecal"
        """
        await self.cmd_function.toggle_commands(ctx, CAL_DISABLED)
