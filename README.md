[![Discord Bots](https://discordbots.org/api/widget/lib/353373501274456065.svg?noavatar=true)](https://discordbots.org/bot/353373501274456065)
[![Discord Bots](https://discordbots.org/api/widget/status/353373501274456065.svg?noavatar=true)](https://discordbots.org/bot/353373501274456065)
[![Discord Bots](https://discordbots.org/api/widget/servers/353373501274456065.svg?noavatar=true)](https://discordbots.org/bot/353373501274456065)
[![Discord Bots](https://discordbots.org/api/widget/upvotes/353373501274456065.svg?noavatar=true)](https://discordbots.org/bot/353373501274456065)
# CoinMarketBot
A Discord bot that sends constant cryptocurrency updates to text-channel subscribers and can create alert notifications.

Created with Python 3.6 and the [CoinMarketCap API](https://github.com/mrsmn/coinmarketcap-api) wrapper.

Click [here](https://discordapp.com/oauth2/authorize?client_id=353373501274456065&scope=bot&permissions=338944) to add the bot to your server.

[![Discord Bots](https://discordbots.org/api/widget/353373501274456065.svg)](https://discordbots.org/bot/353373501274456065)

## Installation:
1. Install necessary requirements using ```pip install -r requirements.txt```
2. Rename `config_template.json` to `config.json`
3. Enter your discord token inside the token variable in `config.json`
4. Run with ```python bot.py``` or ```python3 bot.py```

You're also given the option to change the command prefix as you see fit inside of the config.json.

If you want to use the :small_green_triangle: emoji, I've uploaded it in the emoji folder. To use it for your bot, have a server with the emoji uploaded to it (while also naming it small_green_triangle) and edit the id of the `SMALL_GREEN_TRIANGLE` variable at the top of `coin_market.py` to the emoji ID of your emoji.
## Commands:
This bot has commands to look up cryptocurrencies, subscribe to live updates, create crypto price alerts for the user, and many more.

[See examples of the commands here](https://github.com/kodycode/CoinMarketDiscordBot/wiki/Examples)

[See wiki page here](https://github.com/kodycode/CoinMarketDiscordBot/wiki/Command-Page) or type ```$help```.

Stay tuned for more features.

## Donations:
All donations are greatly appreciated and they help very much with maintaining the live bot:
```
ETH: 0x13318b2A795940D119b999ECfe827708131fA3f6
LTC: LiChyn9o9VhppANUHDhe6ReFjGoGhLqtZm
```

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=XVWUDA7TZH2SU)
