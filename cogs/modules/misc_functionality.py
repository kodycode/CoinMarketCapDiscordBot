from bot_logger import logger


class MiscFunctionality:
    """Handles all Misc command functionality"""

    def __init__(self, bot):
        self.bot = bot

    async def display_bot_profile(self):
        """
        Displays the bot profile URL
        """
        try:
            msg = "https://discordbots.org/bot/353373501274456065"
            await self.bot.say(msg)
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def display_contact(self):
        """
        Displays the owner of this bot
        """
        try:
            username = await self.bot.get_user_info(str(133108920511234048))
            msg = ("Questions? Concerns? Hit me up: **{}**".format(username))
            await self.bot.say(msg)
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def display_donation_option(self):
        """
        Displays donation message
        """
        try:
            msg = ("If you'd like to donate, you can send coins to the "
                   "following addresses:\n```"
                   "ETH: 0x13318b2A795940D119b999ECfe827708131fA3f6\n"
                   "LTC: LiChyn9o9VhppANUHDhe6ReFjGoGhLqtZm\n"
                   "```Or via paypal: https://paypal.me/Kodycode")
            await self.bot.say(msg)
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))
