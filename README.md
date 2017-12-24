# CoinMarketDiscordBot
A Discord bot that reports data from https://coinmarketcap.com/

Created with the python [CoinMarketCap API](https://github.com/mrsmn/coinmarketcap-api) wrapper.

Click [here](https://discordapp.com/oauth2/authorize?&client_id=353373501274456065&scope=bot) to add the bot to your server.

## Installation:
1. Install necessary requirements using ```pip install -r requirements.txt```
2. Rename `config_template.json` to `config.json`
3. Enter your discord token inside the token variable in `config.json`
4. Run with ```python bot.py```

```load_acronyms``` will load all the crypto acronyms so you can search for any cryptocurrency with just the acronym. For example, rather than searching with ```$s bitcoin```, you can just type ```$s btc```.

This bot now also supports live status updates for cryptocurrencies with the `$live` command. If you want to use this command, you must install this bot on your own and fill in the `live_channel`, `live_update_interval`, and `live_check_currency` fields within the `config.json`. It'll read in the config.json file to determine what text channel it'll be posting in, what interval (or amount of seconds) until the next post, and what currencies it'll be posting about.

***It's recommended that you make a separate channel specifically for this command for it will erase the messages within the channel with each iteration.***

## Commands:
| Commands      | Arguments | Output        |
| ------------- | --------- | :------------:|
| $search or $s | **1.** Cryptocurrency to search for (i.e. bitcoin).<br>For multiple searches, seperate each coin with a comma (i.e. bitcoin,ethereum,litecoin)<br>**2.** (Optional) Currency to convert to (i.e. USD, EUR, etc.) | Displays the data of the specified currency. |
| $profit or $p | **1.** Cryptocurrency to search for (i.e. bitcoin)<br>**2.** Amount of crypto coins(i.e. 500)<br>**3.** Cost of each crypto coin that was bought at (i.e. 43.99)<br>**4.** (Optional) Currency to convert to (i.e. USD, EUR, etc.) | Determines how much profit you've made based on the cryptocurrency you specify, the amount of coins that was bought, and the price of each coin |
| $stats | (Optional) Currency to convert to (i.e. USD, EUR, etc.) | Displays the overall stats of the coin market |
| $live | (Optional) Currency to convert to (i.e. USD, EUR, etc.) | Displays live updates of coin stats in n-second intervals (see Installation for more information) |
| $help | | Displays available commands and descriptions of them |

If no fiat currency is entered, the command will default to display in USD.

***Currencies supported:***

USD, AUD, BRL, CAD, CHF, CLP, CNY, CZK, DKK, EUR, GBP, HKD, HUF, IDR, ILS, INR, JPY, KRW, MXN, MYR, NOK, NZD, PHP, PKR, PLN, RUB, SEK, SGD, THB, TRY, TWD, ZAR

Stay tuned for more features.
