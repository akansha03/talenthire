"""add job search and application indexes

Revision ID: ef525e2bf503
Revises: 
Create Date: 2025-12-17 22:13:45.737553

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef525e2bf503'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# enable extension and create indexes - syntax is to give index name first, then table name and then the column names

def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_index("idx_jobs_location", "jobs", ["job_location"])

    op.create_index("idx_jobs_salary_range", "jobs", ["salary_lower_range", "salary_upper_range"])

    op.create_index("idx_jobs_experience_range", "jobs", ["experience_start", "experience_end"])

    op.create_index("idx_jobs_view_count_desc", "jobs", ["view_count"], postgresql_using="btree", postgresql_ops={"view_count" : "DESC"})

    op.execute("""
        CREATE INDEX idx_jobs_title_trgm
        ON jobs USING GIN (lower(job_title) gin_trgm_ops)
    """)

    op.execute("""
        CREATE INDEX idx_jobs_description_trgm
        ON jobs USING GIN (job_description gin_trgm_ops)
    """)
    
    op.create_index("idx_job_applications_job_id", "job_applications", ["job_id"])

    op.create_index("idx_job_applications_candidate_id", "job_applications", ["candidate_id"])
    

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_job_applications_candidate_id", table_name="job_applications")
    op.drop_index("idx_job_applications_job_id", table_name="job_applications")

    op.execute("DROP INDEX IF EXISTS idx_jobs_description_trgm")
    op.execute("DROP INDEX IF EXISTS idx_jobs_title_trgm")

    op.drop_index("idx_jobs_view_count_desc", table_name="jobs")
    op.drop_index("idx_jobs_experience_range", table_name="jobs")
    op.drop_index("idx_jobs_salary_range", table_name="jobs")
    op.drop_index("idx_jobs_location", table_name="jobs")
