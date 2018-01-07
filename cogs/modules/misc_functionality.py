from bot_logger import logger
import discord
import json
import time


class MiscFunctionality:
    """Handles all Misc command functionality"""

    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

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

    async def display_info(self):
        """
        Displays information about the bot
        """
        try:
            alert_count = 0
            channel_count = 0
            member_count = 0
            username = await self.bot.get_user_info(str(133108920511234048))
            with open('subscribers.json') as subscribers:
                subscriber_list = json.load(subscribers)
            with open('alerts.json') as alerts:
                alert_list = json.load(alerts)
                for user in alert_list:
                    alert_count += len(alert_list[user])
            uptime = time.gmtime(time.time() - self.start_time)
            uptime = time.strftime("%H hours, %M minutes, %S seconds", uptime)
            for server in self.bot.servers:
                channel_count += len(server.channels)
                member_count += server.member_count
            em = discord.Embed(colour=0xFFFFFF)
            em.set_author(name=self.bot.user,
                          icon_url=self.bot.user.avatar_url)
            em.set_thumbnail(url=self.bot.user.avatar_url)
            em.add_field(name="Author",
                         value=str(username),
                         inline=False)
            em.add_field(name="Servers",
                         value=str(len(self.bot.servers)),
                         inline=False)
            em.add_field(name="Channels",
                         value=str(channel_count),
                         inline=True)
            em.add_field(name="Members",
                         value=str(member_count),
                         inline=True)
            em.add_field(name="Subscribers",
                         value=str(len(subscriber_list)),
                         inline=True)
            em.add_field(name="Alerts",
                         value=str(alert_count),
                         inline=True)
            em.add_field(name="Uptime",
                         value=uptime,
                         inline=False)
            em.set_footer(text="Created with discord.py",
                          icon_url="https://www.python.org/static/"
                                   "opengraph-icon-200x200.png")
            await self.bot.say(embed=em)
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))
