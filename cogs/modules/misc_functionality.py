from bot_logger import logger
import discord
import json
import time


CMB_ADMIN = "CMB ADMIN"
ADMIN_ONLY = "ADMIN_ONLY"
MISC_DISABLED = "MISC_DISABLED"


class MiscFunctionality:
    """Handles all Misc command functionality"""

    def __init__(self, bot, server_data):
        self.bot = bot
        self.server_data = server_data
        self.start_time = time.time()

    def _check_permission(self, ctx):
        """
        Checks if user contains the correct permissions to use these
        commands
        """
        try:
            user_roles = ctx.message.author.roles
            server_id = ctx.message.server.id
            if server_id not in self.server_data:
                return True
            elif (ADMIN_ONLY in self.server_data[server_id]
                  or MISC_DISABLED in self.server_data[server_id]):
                if CMB_ADMIN not in [role.name for role in user_roles]:
                    return False
            return True
        except:
            pass

    def update(self, server_data=None):
        """
        Updates utilities with new coin market and server data
        """
        self.server_data = server_data

    async def display_bot_profile(self, ctx):
        """
        Displays the bot profile URL
        """
        try:
            if not self._check_permission(ctx):
                return
            msg = "https://discordbots.org/bot/353373501274456065"
            await self.bot.say(msg)
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def display_update_page(self, ctx):
        """
        Links the update page URL
        """
        try:
            if not self._check_permission(ctx):
                return
            msg = "https://github.com/kodycode/CoinMarketDiscordBot/wiki/Updates"
            await self.bot.say(msg)
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def display_donation_option(self, ctx):
        """
        Displays donation message
        """
        try:
            if not self._check_permission(ctx):
                return
            msg = ("If you'd like to donate, you can send coins to the "
                   "following addresses:\n```"
                   "ETH: 0x13318b2A795940D119b999ECfe827708131fA3f6\n"
                   "LTC: LiChyn9o9VhppANUHDhe6ReFjGoGhLqtZm\n"
                   "```Or via paypal: https://paypal.me/Kodycode")
            await self.bot.say(msg)
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def display_info(self, ctx):
        """
        Displays information about the bot
        """
        try:
            if not self._check_permission(ctx):
                return
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
            uptime = time.time() - self.start_time
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            seconds = int(uptime % 60)
            uptime = "{} hours, {} minutes, {} seconds".format(hours,
                                                               minutes,
                                                               seconds)
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
