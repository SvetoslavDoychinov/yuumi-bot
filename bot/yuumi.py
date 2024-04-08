from time import sleep

from bot.base_bot import BaseBot
from common.constants import ClientPhases, LobbyTypes, Positions, ChampSelectPhases, SummonerSpells, ChampionIds, Items


class YuumiBot(BaseBot):
    """Class contains all bot behaviour for DiscoNunu"""

    def is_attached(self) -> bool:
        """
        Check whether Yuumi is attached
        :return: True if attached, False otherwise
        """
        attached = False
        if self.player_champion.is_alive and self.player_champion.side and self.player_champion.game_in_progress:
            attached = self.player_champion.get_player_abilities()["W"]["displayName"] == "Change of Plan"
        return attached

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
            if self.client.get_phase() != ClientPhases.IN_GAME.value:
                break
            self.player_champion.go_to_ally("f4")
            if not self.is_attached():
                self.player_champion.buy_items((Items.World_Atlas, Items.Dream_Maker, Items.Moonstone_Renewer,
                                                Items.Ardent_Censer, Items.Staff_of_Flowing_Water,
                                                Items.Morellonomicon))
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
            sleep(5)  # Avoid spam
