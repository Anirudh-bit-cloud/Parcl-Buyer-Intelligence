"""Unit and integration test verifying Alembic migrations and database seeding from scratch."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from apps.api.config import api_settings


def test_alembic_clean_upgrade_and_downgrade(tmp_path: Path) -> None:
    """Verify clean SQLite database -> alembic upgrade head -> verify tables -> downgrade base."""
    test_db_file = tmp_path / "fresh_migration_test.db"
    test_db_url = f"sqlite:///{test_db_file.as_posix()}"

    alembic_ini_path = api_settings.project_root / "alembic.ini"
    assert alembic_ini_path.exists(), "alembic.ini must exist in project root"

    alembic_cfg = Config(str(alembic_ini_path))
    alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)

    # 1. Upgrade from zero to head
    command.upgrade(alembic_cfg, "head")

    # 2. Inspect created tables
    engine = create_engine(test_db_url)
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    expected_tables = {"clients", "properties", "client_features", "audit_logs", "export_jobs"}
    for tbl in expected_tables:
        assert tbl in table_names, f"Table {tbl} must be created by alembic upgrade head"

    # Verify audit_logs has hash chain columns
    audit_cols = {col["name"] for col in inspector.get_columns("audit_logs")}
    assert "prev_hash" in audit_cols, "audit_logs must have prev_hash column"
    assert "entry_hash" in audit_cols, "audit_logs must have entry_hash column"

    # 3. Test downgrade to base
    command.downgrade(alembic_cfg, "base")
    inspector_post_downgrade = inspect(engine)
    remaining_tables = set(inspector_post_downgrade.get_table_names())
    for tbl in expected_tables:
        assert tbl not in remaining_tables, f"Table {tbl} should be dropped after downgrade to base"
