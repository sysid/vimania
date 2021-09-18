import logging
import os
from pathlib import Path

import pytest
from aiosql import aiosql
from alembic import command
from alembic.config import Config

from vimania.db.dal import DAL
from vimania.environment import config

_log = logging.getLogger(__name__)
log_fmt = r"%(asctime)-15s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s"
datefmt = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(format=log_fmt, level=logging.DEBUG, datefmt=datefmt)


@pytest.fixture()
def init_db():
    # TWBM_DB_URL=sqlite:///test/tests_data/bm_test.db
    dsn = os.environ.get("TW_VIMANIA_DB_URL", "sqlite:///tests/data/vimania_todos_test.db")
    (Path(__file__).parent / "data/vimania_todos_test.db").unlink(missing_ok=True)
    alembic_root = Path(__file__).parent.parent / "pythonx/vimania/db"

    alembic_cfg = Config(str(alembic_root / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(alembic_root / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", dsn)

    command.upgrade(alembic_cfg, "head")
    _ = None


@pytest.fixture()
def dal(init_db):
    dal = DAL(env_config=config)
    with dal as dal:
        sql_files_path = Path(__file__).parent.absolute() / "sql"
        aiosql_queries = aiosql.from_path(f"{sql_files_path}", "sqlite3")
        aiosql_queries.load_testdata(dal.conn.connection)
        dal.conn.connection.commit()
        yield dal
