"""Initial Showrunner schema.

Revision ID: 20260703_0001
Revises:
Create Date: 2026-07-03
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260703_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("clerk_id", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("plan", sa.String(), nullable=False, server_default="free"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("clerk_id"),
    )
    op.create_index("ix_users_clerk_id", "users", ["clerk_id"])

    op.create_table(
        "workspaces",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("clerk_org_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("plan", sa.String(), nullable=False, server_default="free"),
        sa.Column("render_minutes_cap", sa.Integer(), nullable=False, server_default="6"),
        sa.Column("render_minutes_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("clerk_org_id"),
    )
    op.create_index("ix_workspaces_clerk_org_id", "workspaces", ["clerk_org_id"])

    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("concept_prompt", sa.Text(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="created"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_projects_workspace_id", "projects", ["workspace_id"])
    op.create_index("ix_projects_status", "projects", ["status"])

    op.create_table(
        "series_bibles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("logline", sa.Text(), nullable=True),
        sa.Column("themes", postgresql.JSONB(), nullable=True),
        sa.Column("world_json", postgresql.JSONB(), nullable=True),
        sa.Column("characters_json", postgresql.JSONB(), nullable=True),
        sa.Column("style_json", postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_series_bibles_project_id", "series_bibles", ["project_id"])

    op.create_table(
        "episodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("episode_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("outline_json", postgresql.JSONB(), nullable=True),
        sa.Column("script_text", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("assembled_video_url", sa.Text(), nullable=True),
        sa.Column("publish_record_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("project_id", "episode_number", name="uq_episode_number"),
    )
    op.create_index("ix_episodes_project_id", "episodes", ["project_id"])
    op.create_index("ix_episodes_status", "episodes", ["status"])

    op.create_table(
        "scenes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("episode_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scene_number", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("characters_json", postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(["episode_id"], ["episodes.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("episode_id", "scene_number", name="uq_scene_number"),
    )
    op.create_index("ix_scenes_episode_id", "scenes", ["episode_id"])

    op.create_table(
        "shots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("scene_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("shot_number", sa.Integer(), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=True),
        sa.Column("camera_notes", sa.Text(), nullable=True),
        sa.Column("duration_sec", sa.Integer(), nullable=True),
        sa.Column("clip_url", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.ForeignKeyConstraint(["scene_id"], ["scenes.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("scene_id", "shot_number", name="uq_shot_number"),
    )
    op.create_index("ix_shots_scene_id", "shots", ["scene_id"])
    op.create_index("ix_shots_status", "shots", ["status"])

    op.create_table(
        "agent_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("episode_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("agent_name", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("input_json", postgresql.JSONB(), nullable=True),
        sa.Column("output_json", postgresql.JSONB(), nullable=True),
        sa.Column("tokens_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("model", sa.String(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_text", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["episode_id"], ["episodes.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_agent_jobs_project_id", "agent_jobs", ["project_id"])
    op.create_index("ix_agent_jobs_episode_id", "agent_jobs", ["episode_id"])
    op.create_index("ix_agent_jobs_agent_name", "agent_jobs", ["agent_name"])
    op.create_index("ix_agent_jobs_status", "agent_jobs", ["status"])

    op.create_table(
        "assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("episode_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("asset_type", sa.String(), nullable=False),
        sa.Column("oss_url", sa.Text(), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["episode_id"], ["episodes.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_assets_project_id", "assets", ["project_id"])
    op.create_index("ix_assets_episode_id", "assets", ["episode_id"])
    op.create_index("ix_assets_asset_type", "assets", ["asset_type"])

    op.create_table(
        "mcp_connectors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("mcp_url", sa.Text(), nullable=False),
        sa.Column("encrypted_api_key", sa.Text(), nullable=True),
        sa.Column("config_json", postgresql.JSONB(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_mcp_connectors_workspace_id", "mcp_connectors", ["workspace_id"])
    op.create_index("ix_mcp_connectors_name", "mcp_connectors", ["name"])

    op.create_table(
        "publish_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("episode_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("youtube_video_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("analytics_json", postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(["episode_id"], ["episodes.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_publish_records_episode_id", "publish_records", ["episode_id"])
    op.create_index("ix_publish_records_status", "publish_records", ["status"])
    op.create_foreign_key(
        "fk_episodes_publish_record_id",
        "episodes",
        "publish_records",
        ["publish_record_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "usage_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("record_type", sa.String(), nullable=False),
        sa.Column("quantity", sa.Numeric(), nullable=False),
        sa.Column("model", sa.String(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_usage_records_workspace_id", "usage_records", ["workspace_id"])
    op.create_index("ix_usage_records_project_id", "usage_records", ["project_id"])
    op.create_index("ix_usage_records_record_type", "usage_records", ["record_type"])

    op.create_table(
        "clerk_webhook_events",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("clerk_webhook_events")
    op.drop_index("ix_usage_records_record_type", table_name="usage_records")
    op.drop_index("ix_usage_records_project_id", table_name="usage_records")
    op.drop_index("ix_usage_records_workspace_id", table_name="usage_records")
    op.drop_table("usage_records")
    op.drop_constraint("fk_episodes_publish_record_id", "episodes", type_="foreignkey")
    op.drop_index("ix_publish_records_status", table_name="publish_records")
    op.drop_index("ix_publish_records_episode_id", table_name="publish_records")
    op.drop_table("publish_records")
    op.drop_index("ix_mcp_connectors_name", table_name="mcp_connectors")
    op.drop_index("ix_mcp_connectors_workspace_id", table_name="mcp_connectors")
    op.drop_table("mcp_connectors")
    op.drop_index("ix_assets_asset_type", table_name="assets")
    op.drop_index("ix_assets_episode_id", table_name="assets")
    op.drop_index("ix_assets_project_id", table_name="assets")
    op.drop_table("assets")
    op.drop_index("ix_agent_jobs_status", table_name="agent_jobs")
    op.drop_index("ix_agent_jobs_agent_name", table_name="agent_jobs")
    op.drop_index("ix_agent_jobs_episode_id", table_name="agent_jobs")
    op.drop_index("ix_agent_jobs_project_id", table_name="agent_jobs")
    op.drop_table("agent_jobs")
    op.drop_index("ix_shots_status", table_name="shots")
    op.drop_index("ix_shots_scene_id", table_name="shots")
    op.drop_table("shots")
    op.drop_index("ix_scenes_episode_id", table_name="scenes")
    op.drop_table("scenes")
    op.drop_index("ix_episodes_status", table_name="episodes")
    op.drop_index("ix_episodes_project_id", table_name="episodes")
    op.drop_table("episodes")
    op.drop_index("ix_series_bibles_project_id", table_name="series_bibles")
    op.drop_table("series_bibles")
    op.drop_index("ix_projects_status", table_name="projects")
    op.drop_index("ix_projects_workspace_id", table_name="projects")
    op.drop_table("projects")
    op.drop_index("ix_workspaces_clerk_org_id", table_name="workspaces")
    op.drop_table("workspaces")
    op.drop_index("ix_users_clerk_id", table_name="users")
    op.drop_table("users")
