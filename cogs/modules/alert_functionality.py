from bot_logger import logger
from cogs.modules.coin_market import CurrencyException, FiatException
from collections import defaultdict
from discord.errors import Forbidden
import json


class AlertFunctionality:
    """Handles Alert Command functionality"""

    def __init__(self, bot, coin_market, alert_capacity):
        self.bot = bot
        self.coin_market = coin_market
        self.alert_capacity = alert_capacity
        self.market_list = ""
        self.acronym_list = ""
        self.supported_operators = ["<", ">", "<=", ">="]
        self.alert_data = self._check_alert_file_()
        self._save_alert_file_(self.alert_data, backup=True)

    def update(self, market_list, acronym_list):
        """
        Updates utilities with new coin market data
        """
        self.market_list = market_list
        self.acronym_list = acronym_list

    def _check_alert_file_(self):
        """
        Checks to see if there's a valid alerts.json file
        """
        try:
            with open('alerts.json') as alerts:
                return json.load(alerts)
        except FileNotFoundError:
            self._save_alert_file_()
            return json.loads('{}')
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    def _translate_operation_(self, operator):
        """
        Translates the supported operations for alerts
        into english

        @param operator - operator condition to notify the channel
        """
        if operator in self.supported_operators:
            if operator == "<":
                operator_translation = "less than"
            elif operator == "<=":
                operator_translation = "less than or equal to"
            elif operator == ">":
                operator_translation = "greater than"
            elif operator == ">=":
                operator_translation = "greater than or equal to"
            return operator_translation
        else:
            raise Exception("Unable to translate operation.")

    def _check_alert_(self, currency, operator, price, fiat):
        """
        Checks if the alert condition isn't true

        @param currency - cryptocurrency to set an alert of
        @param operator - operator condition to notify the channel
        @param price - price for condition to compare
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        @return - True if condition doesn't exist, False if it does
        """
        market_price = float(self.market_list[currency]["price_usd"])
        market_price = float(self.coin_market.format_price(market_price,
                                                           fiat,
                                                           False))
        if operator in self.supported_operators:
            if operator == "<":
                if market_price < float(price):
                    return False
            elif operator == "<=":
                if market_price <= float(price):
                    return False
            elif operator == ">":
                if market_price > float(price):
                    return False
            elif operator == ">=":
                if market_price >= float(price):
                    return False
            return True
        else:
            raise Exception

    async def add_alert(self, ctx, currency, operator, price, fiat):
        """
        Adds an alert to alerts.json

        @param currency - cryptocurrency to set an alert of
        @param operator - operator condition to notify the channel
        @param price - price for condition to compare
        @param fiat - desired fiat currency (i.e. 'EUR', 'USD')
        """
        try:
            i = 1
            alert_num = None
            ucase_fiat = self.coin_market.fiat_check(fiat)
            if currency.upper() in self.acronym_list:
                currency = self.acronym_list[currency.upper()]
                if "Duplicate" in currency:
                    await self.bot.say(currency)
                    return
            if currency not in self.market_list:
                raise CurrencyException("Currency is invalid: ``{}``".format(currency))
            try:
                if not self._check_alert_(currency, operator, price, ucase_fiat):
                    await self.bot.say("Failed to create alert. Current price "
                                       "of **{}** already meets the condition."
                                       "".format(currency.title()))
                    return
            except Exception:
                await self.bot.say("Invalid operator: **{}**".format(operator))
                return
            user_id = str(ctx.message.author.id)
            if user_id not in self.alert_data:
                self.alert_data[user_id] = {}
            while i <= len(self.alert_data[user_id]) + 1:
                if str(i) not in self.alert_data[user_id]:
                    alert_num = str(i)
                i += 1
            if alert_num is None:
                raise Exception("Something went wrong with adding alert.")
            alert_cap = int(self.alert_capacity)
            if int(alert_num) > alert_cap:
                await self.bot.say("Unable to add alert, user alert capacity of"
                                   " **{}** has been reached.".format(alert_cap))
                return
            alert_list = self.alert_data[user_id]
            alert_list[alert_num] = {}
            channel_alert = alert_list[alert_num]
            channel_alert["currency"] = currency
            if operator in self.supported_operators:
                channel_alert["operation"] = operator
            else:
                await self.bot.say("Invalid operator: {}. Your choices are **<*"
                                   "*, **<=**, **>**, or **>=**"
                                   "".format(operator))
                return
            channel_alert["price"] = ("{:.6f}".format(price)).rstrip('0')
            if channel_alert["price"].endswith('.'):
                channel_alert["price"] = channel_alert["price"].replace('.', '')
            channel_alert["fiat"] = ucase_fiat
            self._save_alert_file_(self.alert_data)
            await self.bot.say("Alert has been set.")
        except CurrencyException as e:
            logger.error("CurrencyException: {}".format(str(e)))
            await self.bot.say(e)
        except FiatException as e:
            logger.error("FiatException: {}".format(str(e)))
            await self.bot.say(e)
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    def _save_alert_file_(self, alert_data={}, backup=False):
        """
        Saves alerts.json file
        """
        if backup:
            alert_filename = "alerts_backup.json"
        else:
            alert_filename = "alerts.json"
        with open(alert_filename, 'w') as outfile:
            json.dump(alert_data,
                      outfile,
                      indent=4)

    async def remove_alert(self, ctx, alert_num):
        """
        Removes an alert from the user's list of alerts

        @param ctx - context of the command sent
        @param alert_num - number of the specific alert to remove
        """
        try:
            user_id = str(ctx.message.author.id)
            user_list = self.alert_data
            alert_list = user_list[user_id]
            if alert_num in alert_list:
                removed_alert = alert_num
                alert_setting = alert_list[alert_num]
                alert_currency = alert_setting["currency"]
                alert_operation = self._translate_operation_(alert_setting["operation"])
                alert_price = alert_setting["price"]
                alert_fiat = alert_setting["fiat"]
                alert_list.pop(str(alert_num))
                self._save_alert_file_(self.alert_data)
                await self.bot.say("Alert **{}** where **{}** is **{}** **{}** "
                                   "in **{}** was successfully "
                                   "removed.".format(removed_alert,
                                                     alert_currency,
                                                     alert_operation,
                                                     alert_price,
                                                     alert_fiat))
            else:
                await self.bot.say("The number you've entered does not exist "
                                   "in the alert list. Use `$geta` to receive "
                                   "a list of ongoing alerts.")
        except Forbidden:
            pass
        except CurrencyException as e:
            logger.error("CurrencyException: {}".format(str(e)))
            await self.bot.say(e)
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def get_alert_list(self, ctx):
        """
        Gets the list of alerts and displays them

        @param ctx - context of the command sent
        """
        try:
            user_id = ctx.message.author.id
            user_list = self.alert_data
            msg = {}
            result_msg = ""
            if user_id in user_list:
                alert_list = user_list[user_id]
                if len(alert_list) != 0:
                    msg[0] = "The following alerts have been set:\n"
                    for alert in alert_list:
                        currency = alert_list[alert]["currency"].title()
                        operation = self._translate_operation_(alert_list[alert]["operation"])
                        msg[int(alert)] = ("[**{}**] Alert when **{}** is **{}** **{}** "
                                           "in **{}**\n".format(alert,
                                                                currency,
                                                                operation,
                                                                alert_list[alert]["price"],
                                                                alert_list[alert]["fiat"]))
                    for line in sorted(msg):
                        result_msg += msg[line]
                else:
                    result_msg = "Channel does not have any alerts to display."
            else:
                result_msg = "User never created any alerts."
            await self.bot.say(result_msg)
        except Forbidden:
            pass
        except CurrencyException as e:
            logger.error("CurrencyException: {}".format(str(e)))
            await self.bot.say(e)
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    async def _alert_user_(self):
        """
        Checks and displays alerts that have met the condition of the
        cryptocurrency price
        """
        try:
            raised_alerts = defaultdict(list)
            for user in self.alert_data:
                alert_list = self.alert_data[str(user)]
                for alert in alert_list:
                    alert_currency = alert_list[alert]["currency"]
                    operator_symbol = alert_list[alert]["operation"]
                    alert_operator = self._translate_operation_(operator_symbol)
                    alert_price = alert_list[alert]["price"]
                    alert_fiat = alert_list[alert]["fiat"]
                    if not self._check_alert_(alert_currency, operator_symbol,
                                              alert_price, alert_fiat):
                        raised_alerts[user].append(alert)
                        user_obj = await self.bot.get_user_info(user)
                        await self.bot.send_message(user_obj,
                                                    "Alert **{}**! "
                                                    "**{}** is **{}** **{}** "
                                                    "in **{}**"
                                                    "".format(alert,
                                                              alert_currency.title(),
                                                              alert_operator,
                                                              alert_price,
                                                              alert_fiat))
            if raised_alerts:
                for user in raised_alerts:
                    for alert_num in raised_alerts[user]:
                        self.alert_data[user].pop(str(alert_num))
                self._save_alert_file_(self.alert_data)
        except Exception as e:
            print("An error has occured. See error.log.")
            logger.error("Exception: {}".format(str(e)))
