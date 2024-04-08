import configparser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict


@dataclass
class BotConfig:
    """Dataclass containing bot configuration"""
    # TODO Add .cfg file to bot data to alter behaviour from
    lol_base_path: Path = Path("C:\\Riot Games\\League of Legends")
    lock_file_path: Path = lol_base_path / "lockfile"
    game_cfg_path: Path = lol_base_path / "Config" / "game.cfg"
    bot_data_path: Path = Path("C:\\ProgramData\\nunu-bot")
    bot_logs_dir_path: Path = bot_data_path / "logs"
    bot_logs_path: Path = bot_logs_dir_path / "bot-logs.log"
    game_cfg_general: Dict[str, str] = field(
        default_factory=lambda: {"WindowMode": "1", "Height": "768", "Width": "1024"})
    game_cfg_hud: Dict[str, str] = field(default_factory=lambda: {"MinimapScale": "1.0000", "showalliedchat": "1",
                                                                  "shopScale": "1.0000"})
    game_item_shop: Dict[str, str] = field(default_factory=lambda: {
        "NativeOffsetY": "-0.2096", "NativeOffsetX": "-0.2539", "CurrentTab": "0", "InvertDisplayOrder": "0",
        "InventoryPanelPinned": "0", "ConsumablesPanelPinned": "0", "BootsPanelPinned": "0"})
    process_name: Optional[str] = None
    pid: Optional[str] = None
    port: Optional[str] = None
    password: Optional[str] = None
    protocol: Optional[str] = None

    def __post_init__(self):
        self._update_game_cfg()
        self._update_details_from_lockfile()

    def _update_game_cfg(self):
        """Updates game cfg file to desired values"""
        config = configparser.ConfigParser()
        config.read(self.game_cfg_path)
        config["General"].update(self.game_cfg_general)
        config["HUD"].update(self.game_cfg_hud)
        config["ItemShop"].update(self.game_item_shop)

        with open(self.game_cfg_path, "w") as configfile:
            config.write(configfile)

    def _update_details_from_lockfile(self):
        """Update object attributes from lockfile"""
        with open(self.lock_file_path, 'r') as lockfile:
            data = lockfile.readline().split(":")
            self.process_name = data[0]
            self.pid = data[1]
            self.port = data[2]
            self.password = data[3]
            self.protocol = data[4]
