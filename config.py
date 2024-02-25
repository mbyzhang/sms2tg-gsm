from typing import Optional, List
from dataclasses import dataclass, field
from dataclass_wizard import YAMLWizard
import yaml

@dataclass
class TelegramConfig(YAMLWizard):
    bot_token: str
    chat_ids: List[str]

@dataclass
class ModemConfig(YAMLWizard):
    port: str
    baudrate: int = 115200
    pin: Optional[str] = None

@dataclass
class Config(YAMLWizard):
    modem: ModemConfig
    telegram: TelegramConfig
    db_filename: Optional[str] = None

def load_config(filename: str) -> Config:
    return Config.from_yaml_file(filename)
