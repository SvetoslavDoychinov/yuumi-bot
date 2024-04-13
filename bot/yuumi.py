from time import sleep

from bot.base_bot import BaseBot
from common.constants import ClientPhases, LobbyTypes, Positions, ChampSelectPhases, SummonerSpells, ChampionIds, Items
from common.utils import is_process_running, run_process


class YuumiBot(BaseBot):
    """Class contains all bot behaviour for DiscoNunu"""

    def __init__(self):
        super().__init__()
        self.build_path = (Items.World_Atlas, Items.Faerie_Charm, Items.Amplifying_Tome, Items.Moonstone_Renewer,
                           Items.Amplifying_Tome, Items.Ardent_Censer, Items.Amplifying_Tome,
                           Items.Staff_of_Flowing_Water, Items.Morellonomicon)
        self.best_friend = "f5"

    def is_attached(self) -> bool:
        """
        Check whether Yuumi is attached
        :return: True if attached, False otherwise
        """
        if self.player_champion.is_alive and self.player_champion.side and self.player_champion.game_in_progress:
            return self.player_champion.get_player_abilities()["W"]["displayName"] == "Change of Plan"

    def handle_client(self) -> None:
        """Handles lobby creation, searching for game, accepting match and reconnect to game"""
        self.is_banned = False
        while True:
            phase = self.client.get_phase()
            if phase == ClientPhases.NONE.value:
                self.client.create_lobby(lobby_type=LobbyTypes.SOLO_DUO)
            elif phase == ClientPhases.LOBBY.value:
                self.client.select_positions(primary=Positions.SUPPORT, secondary=Positions.BOTTOM)
                self.client.start_queue()
            elif phase == ClientPhases.READY_CHECK.value:
                self.client.accept_match()
            elif phase == ClientPhases.END_OF_GAME.value:
                self.client.skip_end_of_game()
            elif phase == ClientPhases.RECONNECT.value:
                self.client.reconnect()
            else:
                return

    def handle_champion_select(self) -> None:
        """Handles champion select"""
        while True:
            if self.client.get_phase() != ClientPhases.CHAMP_SELECT.value:
                return
            if self.client.get_champ_select_info()["timer"]["phase"] == ChampSelectPhases.FINALIZATION.value:
                self.client.select_summoner_spells(spell1=SummonerSpells.HEAL, spell2=SummonerSpells.GHOST)
                self.logger.info("Champion Select completed. Waiting for game to start.")
                return
            elif self.client.get_champ_select_info()["timer"]["phase"] == ChampSelectPhases.BAN_PICK.value:
                if not self.is_banned:
                    self.is_banned = self.client.ban_champion(champs=[ChampionIds.LUX])
                self.client.pick_champion(champs=[ChampionIds.YUUMI])

    def handle_gameplay(self):
        """Handles gameplay once inside a summoners rift game"""
        while True:
            if (self.client.get_phase() != ClientPhases.IN_GAME.value
                    and not is_process_running(self.player_champion.process_name)):
                run_process(process_name="taskkill", args=f'/IM "{self.player_champion.process_name}" /F')
                self.player_champion.release_ally(self.best_friend)
                break
            self.player_champion.lock_on_ally(self.best_friend)
            if not self.is_attached():
                self.player_champion.tactical_retreat(0.7)
                for _ in range(2):  # Can buy multiple items if enough gold
                    self.player_champion.buy_items(self.build_path)

                self.player_champion.lock_on_ally(self.best_friend)
                self.player_champion.go_to_center()
                if not self.is_attached():  # Ensures Yuumi doesn't detach because game remembers w presses
                    self.player_champion.use_spell("w")
                self.player_champion.use_spell("f")
            else:
                self.player_champion.use_spell("e")
                self.player_champion.use_spell("r")
                self.player_champion.use_spell("d")
            self.player_champion.upgrade_ability("r")
            self.player_champion.upgrade_ability("e")
            self.player_champion.upgrade_ability("w")
            self.player_champion.upgrade_ability("q")
