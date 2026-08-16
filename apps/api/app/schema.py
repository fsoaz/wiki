from sqlalchemy import Engine, inspect, text


def upgrade_legacy_auth_sessions(engine: Engine) -> bool:
    """Invalidate legacy raw-token sessions without touching non-session data."""
    inspector = inspect(engine)
    if "auth_sessions" not in inspector.get_table_names():
        return False

    columns = {column["name"] for column in inspector.get_columns("auth_sessions")}
    if "token" not in columns:
        return False

    with engine.begin() as connection:
        connection.execute(text("DROP TABLE auth_sessions"))
    return True
