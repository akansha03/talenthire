"""add job location as search index

Revision ID: 8fa23a7f88ee
Revises: ef525e2bf503
Create Date: 2025-12-19 11:57:07.796607

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# anytime you call alembic downgrade -1 below downgrade function is called - also one more thing that if there is an existing index changed
# then in rollback (downgrade) - change it to the previous version index

# revision identifiers, used by Alembic.
revision: str = '8fa23a7f88ee'
down_revision: Union[str, Sequence[str], None] = 'ef525e2bf503'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.drop_index("idx_jobs_location", table_name="jobs")

    op.execute("""
        CREATE INDEX idx_jobs_location_gin
        ON jobs USING GIN (job_location gin_trgm_ops)
    """)
    op.create_index("idx_job_status", "jobs", ["status"])


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS idx_jobs_location_gin")
    op.execute("DROP INDEX IF EXISTS idx_job_status")
    op.create_index("idx_jobs_location", "jobs", ["job_location"])
    
