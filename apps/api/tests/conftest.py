import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def api_test_database(tmp_path, monkeypatch):
    monkeypatch.setenv("WIKIAI_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")

    from app import config as config_module
    from app import database as database_module
    from app import db_models  # noqa: F401

    config_module.settings = config_module.Settings()
    database_module.engine.dispose()
    database_module.engine = database_module.create_engine(
        config_module.settings.database_url,
        future=True,
        connect_args={"check_same_thread": False},
    )
    database_module.SessionLocal.configure(bind=database_module.engine)
    database_module.Base.metadata.create_all(bind=database_module.engine)

    from app.seed import seed_articles, seed_users

    session = database_module.SessionLocal()
    try:
        seed_users(session)
        seed_articles(session)
    finally:
        session.close()

    yield

    database_module.engine.dispose()
