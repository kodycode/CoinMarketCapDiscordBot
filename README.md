# CoinMarketDiscordBot
A Discord bot that reports data from https://coinmarketcap.com/

Created with Python 3.6 and the [CoinMarketCap API](https://github.com/mrsmn/coinmarketcap-api) wrapper.

Click [here](https://discordapp.com/oauth2/authorize?&client_id=353373501274456065&scope=bot) to add the bot to your server.

## Installation:
1. Install necessary requirements using ```pip install -r requirements.txt```
2. Rename `config_template.json` to `config.json`
3. Enter your discord token inside the token variable in `config.json`
4. Run with ```python bot.py```

```load_acronyms``` will load all the crypto acronyms so you can search for any cryptocurrency with just the acronym. For example, rather than searching with ```$s bitcoin```, you can just type ```$s btc```.

## Commands:

***As of 12/28/2017, the live command has been removed and in place exists a pub/sub system to simplify and expand the bot's utility. You do not need to host your own to bot to receive live updates anymore, you can sub to the bot's subscriber list to receive live updates (Please see the wiki page below for more details).***

See wiki page [here](https://github.com/kodycode/CoinMarketDiscordBot/wiki/Command-Page) or type ```$help```.

Stay tuned for more features.

## Donations:
Not mandatory at all, but if you're feeling generous:
```
ETH: 0x13318b2A795940D119b999ECfe827708131fA3f6
LTC: LiChyn9o9VhppANUHDhe6ReFjGoGhLqtZm
```

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=XVWUDA7TZH2SU)
