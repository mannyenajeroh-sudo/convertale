"""Add leads table and missing SeriesBible fields.

Revision ID: 20260716_0002
Revises: 20260703_0001
Create Date: 2026-07-16

The `Lead` ORM model (used by GateDeliveryAgent for the Cliffhanger
email-capture gate) had no corresponding migration at all, so
`/api/gate/unlock` would fail at runtime with
`relation "leads" does not exist` the first time anyone used it.

`SeriesBibleService.get_or_create()` also writes `props`, `locations`,
`plot_threads`, and `episodes` onto `SeriesBible`, none of which existed
as columns — every call raised `TypeError: invalid keyword argument`.
Both are fixed here.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260716_0002"
down_revision: str | None = "20260703_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "episode_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("episodes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column(
            "captured_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_leads_project_id", "leads", ["project_id"])
    op.create_index("ix_leads_episode_id", "leads", ["episode_id"])
    op.create_index("ix_leads_email", "leads", ["email"])

    op.add_column("series_bibles", sa.Column("props", postgresql.JSONB(), nullable=True))
    op.add_column("series_bibles", sa.Column("locations", postgresql.JSONB(), nullable=True))
    op.add_column("series_bibles", sa.Column("plot_threads", postgresql.JSONB(), nullable=True))
    op.add_column("series_bibles", sa.Column("episodes", postgresql.JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column("series_bibles", "episodes")
    op.drop_column("series_bibles", "plot_threads")
    op.drop_column("series_bibles", "locations")
    op.drop_column("series_bibles", "props")

    op.drop_index("ix_leads_email", table_name="leads")
    op.drop_index("ix_leads_episode_id", table_name="leads")
    op.drop_index("ix_leads_project_id", table_name="leads")
    op.drop_table("leads")
