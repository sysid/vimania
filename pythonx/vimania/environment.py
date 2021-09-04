"""Default environment
Edit service environment to override
"""
################################################################################
# Base Environment
################################################################################
import logging
from pathlib import Path

from pydantic import BaseSettings

_log = logging.getLogger("vimania-plugin.environment")
ROOT_DIR = Path(__file__).parent.absolute()


class Environment(BaseSettings):
    log_level: str = "INFO"
    tw_vimania_db_url: str = f"sqlite:///{ROOT_DIR}/db/todos.db"

    @property
    def dbfile(self):
        return f"{self.tw_vimania_db_url.split('sqlite:///')[-1]}"


config = Environment()
_ = None
