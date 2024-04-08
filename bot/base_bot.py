import logging
from abc import ABC, abstractmethod

from api.client import ClientAPI
from api.player_champion import PlayerChampion
from config import BotConfig


class BaseBot(ABC):
    """Base Class contains all bot behaviour"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.local_host = "127.0.0.1"
        self.config = BotConfig()
        self.client = ClientAPI(self.config.protocol, self.local_host, self.config.port, self.config.password)
        self.player_champion = PlayerChampion()
        self.client.connect()
        self.is_banned = False

    @abstractmethod
    def handle_client(self) -> None:
        """Handles lobby creation, searching for game, accepting match and reconnect to game"""
        pass

    @abstractmethod
    def handle_champion_select(self) -> None:
        """Handles champion select"""
        pass

    @abstractmethod
    def handle_gameplay(self):
        """Handles gameplay once inside a summoners rift game"""
        pass

    def main_loop(self):
        """Main loop includes all bot behaviour should be executed in script"""
        while True:
            self.handle_client()
            self.handle_champion_select()
            self.handle_gameplay()
