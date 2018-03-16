from discord.ext import commands


class AdminCommands:
    """Handles admin commands"""

    def __init__(self, cmd_function):
        self.cmd_function = cmd_function

    @commands.command(name='admin', pass_context=True)
    async def admin(self, ctx):
        """
        Toggles admin mode
        An example for this command would be:
        "$adminon"
        """
        await self.cmd_function.toggle_admin_mode(ctx)
