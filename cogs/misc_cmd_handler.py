from discord.ext import commands


class MiscCommands:
    """Handles misc commands"""

    def __init__(self, cmd_function):
        self.cmd_function = cmd_function

    @commands.command(name="profile")
    async def bot(self):
        """
        Shows bot profile
        An example for this command would be:
        "$donate"
        """
        await self.cmd_function.display_bot_profile()

    @commands.command(name="contact")
    async def contact(self):
        """
        Shows contact information
        An example for this command would be:
        "$donate"
        """
        await self.cmd_function.display_contact()

    @commands.command(name="donate")
    async def donate(self):
        """
        Shows donation options
        An example for this command would be:
        "$donate"
        """
        await self.cmd_function.display_donation_option()
