# https://developer.riotgames.com/docs/lol#game-client-api_live-client-data-api
import logging
import random
from time import sleep
from typing import Dict, Tuple, List

from common.constants import MapLocationRatios, Items
from common.request_api import RequestAPI
from common.utils import is_process_running
from common.window_manager import WindowManager


class PlayerChampion:
    """Class that handles player champion in game"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.window_name = "League of Legends (TM) Client"
        self.process_name = "League of Legends.exe"
        self.current_gold = 0
        self.max_hp = 0
        self.current_hp = 0
        self.item = 0
        self.game_in_progress = False
        self.side = None
        self.summoner_name = None
        self.is_alive = False
        self._window_manager = WindowManager(self.window_name)
        self._request_api = RequestAPI("https", "127.0.0.1", "2999")

    def update_player_data(self) -> None:
        """Update all object attributes with data from game if game not ended"""
        self.set_game_events_data()
        if self.game_in_progress:
            self.set_active_player_data()
            self.set_player_state()

    def set_active_player_data(self) -> None:
        """Set summoner_name"""
        self.logger.debug("Setting player summoner name")
        if is_process_running(self.process_name):
            data = self._request_api.get(url="/liveclientdata/activeplayer").json()
            self.summoner_name = data["summonerName"].split("#")[0]  # it includes tag
            self.current_gold = data["currentGold"]
            self.max_hp = data["championStats"]["maxHealth"]
            self.current_hp = data["championStats"]["currentHealth"]

    def set_game_events_data(self) -> None:
        """Set object attributes with data from game events"""
        if is_process_running(self.process_name):
            self.logger.debug("Setting game state")
            events = self._request_api.get(url="/liveclientdata/eventdata").json()
            if events.get("Events"):
                for event in events.get("Events"):
                    if event["EventName"] == "GameEnd":
                        self.game_in_progress = False
                        self.side = None
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

    def get_current_items(self) -> List[str]:
        """
        Get list of current items on champion
        :return: current items
        """
        if self.side and self.game_in_progress:
            response = self._request_api.get(f"/liveclientdata/playeritems?summonerName={self.summoner_name}").json()
            current_items = [item["displayName"] for item in response]
            # Support item upgrades itself causes confusion
            if current_items and current_items[0] == "Runic Compass":
                current_items[0] = Items.World_Atlas.name
            self.logger.info(f"Current items {current_items}")
            return current_items

    def get_player_abilities(self) -> Dict:
        """
        Get player abilities
        :return: Dict containing all abilities information
        """
        if self.side and self.game_in_progress:
            return self._request_api.get(url="/liveclientdata/activeplayerabilities").json()

    def go_to_enemy_nexus(self) -> None:
        """Go to the enemy nexus if alive"""
        self.update_player_data()
        if self.side and self.is_alive and self.game_in_progress:
            self.logger.info("Go to enemy nexus")
            self._window_manager.right_click(ratio=MapLocationRatios[self.side].value)

    def go_to_ally(self, ally: str) -> None:
        """
        Better use lock_on_ally + go_to_center + release_ally funcs
        Go to an allied champion
        :param ally: ally to go ot from f1-f5
        """
        self.update_player_data()
        if self.side and self.is_alive and self.game_in_progress:
            self.logger.info(f"Going to ally champion {ally}")
            self._window_manager.hold_key(ally)
            self._window_manager.right_click(ratio=MapLocationRatios.CENTER.value)
            sleep(1)
            self._window_manager.release(ally)

    def lock_on_ally(self, ally: str):
        """
        Lock camera on allied champion
        :param ally: go ot from f1-f5
        """
        self.update_player_data()
        if self.side and self.is_alive and self.game_in_progress:
            self.logger.info(f"Locking on ally champion {ally}")
            self._window_manager.press_key(ally)
            self._window_manager.hold_key(ally)

    def go_to_center(self):
        """Going to center of screen"""
        self.update_player_data()
        if self.side and self.is_alive and self.game_in_progress:
            self.logger.info("Clicking on center of screen")
            self._window_manager.right_click(ratio=MapLocationRatios.CENTER.value)

    def release_ally(self, ally: str):
        """Release camera on allied champion"""
        self.update_player_data()
        if self.side and not self.game_in_progress:
            self.logger.info(f"Releasing ally champion {ally}")
            self._window_manager.release(ally)

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

    def write_in_chat(self, msg: str) -> None:
        """Write a message in game chat"""
        self._window_manager.press_key("enter")
        self._window_manager.write(msg)
        self._window_manager.press_key("enter")
        sleep(1)

    def buy_items(self, item_path: Tuple[Items]) -> True:
        """
        Buy a random not already bought item from item path if enough gold
        :param item_path: list of Items to build
        :return: True bought item successfully, False otherwise
        """
        item_to_buy = item_path[self.item]
        prev_gold = self.current_gold
        self.update_player_data()
        if self.side and self.game_in_progress and self.current_gold > item_to_buy.value:
            if item_to_buy.name in self.get_current_items():
                self.item += 1
                return False
            self.logger.info(f"Buying item {item_to_buy.name}")
            self._window_manager.press_key("p")
            self._window_manager.press_key("ctrl+l")
            self._window_manager.write(item_to_buy.name)
            self._window_manager.press_key("enter")
            self._window_manager.press_key("p")
            sleep(1)
            self.update_player_data()
            if prev_gold > self.current_gold:
                self.item += 1
                return True
        return False

    def tactical_retreat(self, hp_to_retreat: int) -> None:
        """
        Retreats and recalls
        :param hp_to_retreat: minimal fraction of max_hp to start retreating at
        """
        self.update_player_data()
        if self.is_alive and self.side and self.game_in_progress and \
                self.current_hp / self.max_hp <= hp_to_retreat:
            own_nexus = MapLocationRatios.CHAOS.value if self.side == "ORDER" else MapLocationRatios.ORDER.value
            self._window_manager.right_click(ratio=own_nexus)
            sleep(5)  # time to retreat
            self.use_spell("b")
            sleep(12)  # recall time + heal up
