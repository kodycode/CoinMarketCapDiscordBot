from cogs.admin_cmd_handler import AdminCommands
from cogs.alert_cmd_handler import AlertCommands
from cogs.coin_market_cmd_handler import CoinMarketCommands
from cogs.misc_cmd_handler import MiscCommands
from cogs.subscriber_cmd_handler import SubscriberCommands
from cogs.modules.core_functionality import CoreFunctionality


def setup(bot):
    cmd_function = CoreFunctionality(bot)
    bot.add_cog(MiscCommands(cmd_function))
    bot.add_cog(AdminCommands(cmd_function))
    bot.add_cog(CoinMarketCommands(cmd_function))
    bot.add_cog(SubscriberCommands(cmd_function))
    bot.add_cog(AlertCommands(cmd_function))
