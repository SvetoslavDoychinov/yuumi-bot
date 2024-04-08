# https://developer.riotgames.com/docs/lol#game-client-api_live-client-data-api
import logging
from time import sleep
from typing import Dict, Tuple

from common.constants import MapLocationRatios, Items
from common.request_api import RequestAPI
from common.utils import is_process_running, run_process
from common.window_manager import WindowManager


class PlayerChampion:
    """Class that handles player champion in game"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.window_name = "League of Legends (TM) Client"
        self.process_name = "League of Legends.exe"
        self.items = 0
        self.current_gold = None
        self.game_in_progress = False
        self.side = None
        self.summoner_name = None
        self.is_alive = False
        self._window_manager = WindowManager(self.window_name)
        self._request_api = RequestAPI("https", "127.0.0.1", "2999")

    def update_player_data(self) -> None:
        """Update all object attributes with data from game if game not ended else kill process"""
        self.set_game_events_data()
        if self.game_in_progress:
            self.set_gold_n_summoner_name()
            self.set_player_state()
        else:
            run_process(process_name="taskkill", args=f'/IM "{self.process_name}" /F')

    def set_gold_n_summoner_name(self) -> None:
        """Set summoner_name"""
        self.logger.debug("Setting player summoner name")
        if is_process_running(self.process_name):
            data = self._request_api.get(url="/liveclientdata/activeplayer").json()
            self.summoner_name = data["summonerName"].split("#")[0]  # it includes tag
            self.current_gold = data["currentGold"]

    def set_game_events_data(self) -> None:
        """Set object attributes with data from game events"""
        if is_process_running(self.process_name):
            self.logger.debug("Setting game state")
            events = self._request_api.get(url="/liveclientdata/eventdata").json()
            if events.get("Events"):
                for event in events.get("Events"):
                    if event["EventName"] == "GameEnd":
                        self.game_in_progress = False
                        return  # game ended no reason to update anything
                    if event["EventName"] == "GameStart":
                        self.game_in_progress = True

    def set_player_state(self) -> None:
        """Set player champion state"""
        self.logger.debug("Setting player state")
        if is_process_running(self.process_name):
            player_list = self._request_api.get("/liveclientdata/playerlist").json()
            for player in player_list:
                if player["summonerName"] == self.summoner_name:
                    self.side = player["team"]
                    self.is_alive = not player["isDead"]
                    sleep(player["respawnTimer"])  # will sleep if player is dead

    def get_player_abilities(self) -> Dict:
        """
        Get player abilities
        :return: Dict containing all abilities information
        """
        return self._request_api.get(url="/liveclientdata/activeplayerabilities").json()

    def go_to_enemy_nexus(self) -> None:
        """Go to the enemy nexus if alive"""
        self.update_player_data()
        if self.side and self.is_alive and self.game_in_progress:
            self.logger.info("Go to enemy nexus")
            self._window_manager.right_click(ratio=MapLocationRatios[self.side].value)

    def go_to_ally(self, ally: str) -> None:
        """
        Go to an allied champion
        :param ally: ally to go ot from f1-f5
        """
        self.update_player_data()
        if self.side and self.is_alive and self.game_in_progress:
            self.logger.info(f"Going to ally champion {ally}")
            self._window_manager.hold_key(ally)
            sleep(1)
            self._window_manager.right_click(ratio=MapLocationRatios.CENTER.value)
            sleep(1)
            self._window_manager.release(ally)
            sleep(1)

    def upgrade_ability(self, ability: str) -> None:
        """
        Upgrade an ability
        :param ability: ability to upgrade
        """
        self.update_player_data()
        if self.side and self.is_alive and self.game_in_progress:
            self.logger.info(f"Upgrading ability {ability}")
            self._window_manager.press_key(f"ctrl+{ability}")

    def use_spell(self, spell: str) -> None:
        """
        Use a spell
        :param spell: spell to click
        """
        self.update_player_data()
        if self.side and self.is_alive and self.game_in_progress:
            self.logger.info(f"Using ability {spell}")
            self._window_manager.press_key(spell)

    def lock_camera(self) -> None:
        """Lock camera on champion if alive"""
        self.update_player_data()
        if self.is_alive and self.side and self.game_in_progress:
            self._window_manager.press_key("y")

    def buy_items(self, item_path: Tuple[Items]) -> None:
        """
        Buy items from item path in order if enough gold
        :param item_path: list of Items to build
        """
        self.update_player_data()
        self.logger.info("Buying item")
        if self.side and self.game_in_progress:
            item_to_buy = item_path[self.items]
            if self.current_gold > item_to_buy.value:
                self._window_manager.press_key("p")
                self._window_manager.press_key("ctrl+l")
                sleep(1)
                self._window_manager.write(item_to_buy.name.replace("_", " "))
                sleep(1)
                self._window_manager.press_key("enter")
                sleep(2)
                self.items += 1
