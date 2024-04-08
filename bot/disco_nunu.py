import logging
from time import sleep

from api.client import ClientAPI
from api.player_champion import PlayerChampion
from bot.base_bot import BaseBot
from common.constants import LobbyTypes, Positions, ClientPhases, ChampionIds, ChampSelectPhases, \
    SummonerSpells
from config import BotConfig


class DiscoNunu(BaseBot):
    """Class contains all bot behaviour for DiscoNunu"""

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
                self.client.select_summoner_spells(spell1=SummonerSpells.GHOST, spell2=SummonerSpells.CLEANSE)
                self.logger.info("Champion Select completed. Waiting for game to start.")
                return
            elif self.client.get_champ_select_info()["timer"]["phase"] == ChampSelectPhases.BAN_PICK.value:
                if not self.is_banned:
                    self.is_banned = self.client.ban_champion(champs=[ChampionIds.LUX])
                self.client.pick_champion(champs=[ChampionIds.NUNU, ChampionIds.DRAVEN])

    def handle_gameplay(self):
        """Handles gameplay once inside a summoners rift game"""
        while True:
            if self.client.get_phase() != ClientPhases.IN_GAME.value:
                break
            self.player_champion.lock_camera()
            self.player_champion.go_to_enemy_nexus()
            self.player_champion.use_spell("d")
            self.player_champion.use_spell("f")
            sleep(5)  # Avoid spam
