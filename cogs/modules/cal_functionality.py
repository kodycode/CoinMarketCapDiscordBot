from bot_logger import logger
from cogs.modules.coinmarketcal import CoinMarketCal
import discord

MONTHS = ["January", "February", "March",
          "April", "May", "June",
          "July", "August", "September",
          "October", "November", "December"]


class CalFunctionality:
    """Handles coinmarketcal functionality"""

    def __init__(self, bot, config_data, server_data):
        self.bot = bot
        self.acronym_list = ""
        self.server_data = server_data
        self.cal = CoinMarketCal(config_data["coinmarketcal_client_id"],
                                 config_data["coinmarketcal_client_secret"])

    def update(self, acronym_list=None, server_data=None):
        """
        Updates utilities with new coin market and server data
        """
        if server_data:
            self.server_data = server_data
        if acronym_list:
            self.acronym_list = acronym_list

    async def _say_msg(self, msg=None, channel=None, emb=None):
        """
        Bot will say msg if given correct permissions

        @param msg - msg to say
        @param channel - channel to send msg to
        @param emb - embedded msg to say
        """
        try:
            if channel:
                if emb:
                    await self.bot.send_message(channel, embed=emb)
                else:
                    await self.bot.send_message(channel, msg)
            else:
                if emb:
                    await self.bot.say(embed=emb)
                else:
                    await self.bot.say(msg)
        except:
            pass

    def format_events(self, coin, event):
        """
        Formats the requested event into a string,
        and returns the event date along with the
        formatted string
        """
        footer = ""
        # format date of event
        date_event = event["date_event"].split("T")[0]
        date_split = date_event.split("-")
        date_split[1] = MONTHS[int(date_split[1])]  # replace month num with name
        date_event = "{} {} {}".format(date_split[0], date_split[1], date_split[2])
        # format created date
        created_date = event["created_date"].split("T")[0]
        created_split = created_date.split("-")
        created_split[1] = MONTHS[int(created_split[1])]  # replace month num with name
        created_date = "{} {} {}".format(created_split[0], created_split[1], created_split[2])
        twitter_acc = event["twitter_account"]
        if event["is_hot"]:
            event["title"] = event["title"] + " :fire:"
        if twitter_acc is not None:
            footer = twitter_acc
        msg = ("__**{}**__\n"
               "**{}** (created at {})\n\n"
               "**Description:**\n{}\n\n"
               "**Proof:**\n{}\n"
               "**Source:**\n{}\n\n"
               "**Total Votes:** {}\n"
               "**Positive Vote Percentage:** {}%\n"
               "".format(coin.title(),
                         event["title"],
                         created_date,
                         event["description"],
                         event["proof"],
                         event["source"],
                         event["vote_count"],
                         event["percentage"]))
        em = discord.Embed(title="**Date: {}**".format(date_event),
                           description=msg,
                           colour=0xFFFFFF,
                           footer=footer)
        return em

    async def display_event(self, currency, page):
        """
        Displays events about a requested cryptocurrency
        """
        try:
            if currency.upper() in self.acronym_list:
                currency = self.acronym_list[currency.upper()]
            try:
                event = self.cal.get_coin_event(currency, page)[0]
            except:
                await self.bot.say("No event available for the following "
                                   "currency: **{}**".format(currency))
                return
            em = self.format_events(currency, event)
            await self._say_msg(emb=em)
        except Exception as e:
            print("Failed to display calendar events. See error.log.")
            logger.error("Exception: {}".format(str(e)))
