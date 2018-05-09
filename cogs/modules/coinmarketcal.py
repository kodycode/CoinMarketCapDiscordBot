# from bot_logger import logger
import requests


TOKEN_URL = ("https://api.coinmarketcal.com/oauth/v2/token?"
             "grant_type=client_credentials")

EVENT_URL = "https://api.coinmarketcal.com/v1/events?"


class CoinMarketCalException(Exception):
    """Exception class for coinmarketcal"""


class CoinMarketCal:
    """Handles coinmarketcal API features"""

    def __init__(self, client_id, client_secret):
        """
        Initiates CoinMarketCal
        """
        self.access_token = self.get_access_token(client_id,
                                                  client_secret)

    def get_access_token(self, client_id, client_secret):
        """
        Receives access token from coinmarketcal

        @return - access token
        """
        try:
            r_url = ("{}&client_id={}&client_secret={}"
                     "".format(TOKEN_URL, client_id, client_secret))
            token_req = requests.get(r_url)
            print(token_req.json()["access_token"])
            return token_req.json()["access_token"]
        except Exception as e:
            print("Error receiving cal access token.")
            print("Exception: {}".format(str(e)))
            # logger.error("Exception: {}".format(str(e)))

    def get_coin_events(self, coin, page):
        """
        Retrieves events based around the specified coin
        (Gets 5 events in one request)

        @param coin - coin to get events on
        @param page - page of the number of events
        """
        try:
            r_url = ("{}access_token={}&page={}&max=5&coins={}"
                     "".format(EVENT_URL, self.access_token, page, coin))
            token_req = requests.get(r_url)
            event_list = token_req.json()
        except Exception as e:
            print("Error receiving coin events.")
            print("Exception: {}".format(str(e)))
            # logger.error("Exception: {}".format(str(e)))
