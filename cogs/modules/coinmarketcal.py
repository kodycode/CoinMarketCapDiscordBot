from bot_logger import logger
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
            return token_req.json()["access_token"]
        except CoinMarketCalException as e:
            print("Error receiving cal access token.")
            logger.error("Exception: {}".format(str(e)))

    def get_coin_event(self, coin, page):
        """
        Retrieves events based around the specified coin
        (Gets 1 event in one request)

        @param coin - coin to get events on
        @param page - page of the number of events
        """
        try:
            r_url = ("{}access_token={}&page={}&max=1&coins={}"
                     "".format(EVENT_URL, self.access_token, page, coin))
            event_req = requests.get(r_url)
            return event_req.json()
        except CoinMarketCalException as e:
            print("Error receiving coin events.")
            logger.error("Exception: {}".format(str(e)))
