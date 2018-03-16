from bot_logger import logger
import json


class AdminFunctionality:
    """Handles all admin related commands"""

    def __init__(self, bot):
        self.bot = bot
        self.admin_data = self._check_admin_file()
        self._save_admin_file(self.admin_data, backup=True)

    def _check_admin_file(self):
        """
        Checks to see if there's a valid admins.json file
        """
        try:
            with open('admins.json') as admins:
                return json.load(admins)
        except FileNotFoundError:
            self._save_admin_file()
            return json.loads('{}')
        except Exception as e:
            print("Unable to load admin file. See error.log.")
            logger.error("Exception: {}".format(str(e)))

    def _save_admin_file(self, admin_data={}, backup=False):
        """
        Saves admin.json file
        """
        if backup:
            alert_filename = "admins_backup.json"
        else:
            alert_filename = "admins.json"
        with open(alert_filename, 'w') as outfile:
            json.dump(admin_data,
                      outfile,
                      indent=4)

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

    async def toggle_admin_mode(self, ctx):
        """
        Toggles admin mode on/off
        """
        try:
            try:
                user_roles = ctx.message.author.roles
            except:
                await self._say_msg("Command must be used in a server.")
                return
            if "CMB Admin" not in [role.name for role in user_roles]:
                await self._say_msg("Admin privilege is required for "
                                    "this command.")
                return
            channel = ctx.message.channel.id
            try:
                server = self.bot.get_channel(channel).server  # validate channel
            except:
                await self._say_msg("Not a valid server to toggle admin mode.")
                return
            if server.id not in self.admin_data:
                self.admin_data[server.id] = {"admin_mode": False}
            self.admin_data[server.id]["admin_mode"] = not self.admin_data[server.id]["admin_mode"]
            self._save_admin_file(self.admin_data)
            if self.admin_data[server.id]["admin_mode"]:
                await self._say_msg("Server is set to admin mode.")
            else:
                await self._say_msg("Admin mode off.")
        except Exception as e:
            print("Failed to toggle admin mode. See error.log.")
            logger.error("Exception: {}".format(str(e)))
