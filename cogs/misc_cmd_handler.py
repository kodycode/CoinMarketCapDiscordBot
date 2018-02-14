from discord.ext import commands


class MiscCommands:
    """Handles misc commands"""

    def __init__(self, cmd_function):
        self.cmd_function = cmd_function

    @commands.command(name="profile")
    async def profile(self):
        """
        Shows bot profile
        An example for this command would be:
        "$profile"
        """
        await self.cmd_function.display_bot_profile()

    @commands.command(name="updates")
    async def updates(self):
        """
        Shows update log of the bot
        An example for this command would be:
        "$updates"
        """
        await self.cmd_function.display_update_page()

    @commands.command(name="donate")
    async def donate(self):
        """
        Shows donation options
        An example for this command would be:
        "$donate"
        """
        await self.cmd_function.display_donation_option()

    @commands.command(name="info")
    async def info(self):
        """
        Shows information about the bot
        An example for this command would be:
        "$info"
        """
        await self.cmd_function.display_info()
