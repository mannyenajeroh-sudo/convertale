import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from showrunner_api.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String)
    plan: Mapped[str] = mapped_column(String, default="free", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_org_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    plan: Mapped[str] = mapped_column(String, default="free", nullable=False)
    render_minutes_cap: Mapped[int] = mapped_column(Integer, default=6, nullable=False)
    render_minutes_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    projects: Mapped[list["Project"]] = relationship(back_populates="workspace")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str | None] = mapped_column(String)
    concept_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String, default="created", nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    workspace: Mapped[Workspace] = relationship(back_populates="projects")


class SeriesBible(Base):
    __tablename__ = "series_bibles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str | None] = mapped_column(String)
    logline: Mapped[str | None] = mapped_column(Text)
    themes: Mapped[dict | list | None] = mapped_column(JSONB)
    world_json: Mapped[dict | list | None] = mapped_column(JSONB)
    characters_json: Mapped[dict | list | None] = mapped_column(JSONB)
    style_json: Mapped[dict | list | None] = mapped_column(JSONB)
    # NOTE: the fields below were being written by SeriesBibleService
    # (props, locations, plot_threads, episodes) but did not exist on this
    # model, so every SeriesBibleService.get_or_create() call raised
    # TypeError: invalid keyword argument. Added here so the ORM model and
    # the service layer agree on the schema.
    props: Mapped[dict | list | None] = mapped_column(JSONB, default=list)
    locations: Mapped[dict | list | None] = mapped_column(JSONB, default=list)
    plot_threads: Mapped[dict | list | None] = mapped_column(JSONB, default=list)
    episodes: Mapped[dict | list | None] = mapped_column(JSONB, default=list)


class Episode(Base):
    __tablename__ = "episodes"
    __table_args__ = (UniqueConstraint("project_id", "episode_number", name="uq_episode_number"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    episode_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str | None] = mapped_column(String)
    outline_json: Mapped[dict | list | None] = mapped_column(JSONB)
    script_text: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String, default="pending", nullable=False, index=True)
    assembled_video_url: Mapped[str | None] = mapped_column(Text)
    publish_record_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)


class Scene(Base):
    __tablename__ = "scenes"
    __table_args__ = (UniqueConstraint("episode_id", "scene_number", name="uq_scene_number"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    episode_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("episodes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    scene_number: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String)
    characters_json: Mapped[dict | list | None] = mapped_column(JSONB)


class Shot(Base):
    __tablename__ = "shots"
    __table_args__ = (UniqueConstraint("scene_id", "shot_number", name="uq_shot_number"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scene_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scenes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    shot_number: Mapped[int] = mapped_column(Integer, nullable=False)
    prompt: Mapped[str | None] = mapped_column(Text)
    camera_notes: Mapped[str | None] = mapped_column(Text)
    duration_sec: Mapped[int | None] = mapped_column(Integer)
    clip_url: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String, default="pending", nullable=False, index=True)


class AgentJob(Base):
    __tablename__ = "agent_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    episode_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("episodes.id", ondelete="SET NULL"), index=True
    )
    agent_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String, default="pending", nullable=False, index=True)
    input_json: Mapped[dict | list | None] = mapped_column(JSONB)
    output_json: Mapped[dict | list | None] = mapped_column(JSONB)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    model: Mapped[str | None] = mapped_column(String)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_text: Mapped[str | None] = mapped_column(Text)


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    episode_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("episodes.id", ondelete="SET NULL"), index=True
    )
    asset_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    oss_url: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict | list | None] = mapped_column(JSONB)


class McpConnector(Base):
    __tablename__ = "mcp_connectors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    mcp_url: Mapped[str] = mapped_column(Text, nullable=False)
    encrypted_api_key: Mapped[str | None] = mapped_column(Text)
    config_json: Mapped[dict | list | None] = mapped_column(JSONB)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class PublishRecord(Base):
    __tablename__ = "publish_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    episode_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("episodes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    youtube_video_id: Mapped[str | None] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="pending", nullable=False, index=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    analytics_json: Mapped[dict | list | None] = mapped_column(JSONB)


class UsageRecord(Base):
    __tablename__ = "usage_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), index=True
    )
    record_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(Numeric, nullable=False)
    model: Mapped[str | None] = mapped_column(String)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ClerkWebhookEvent(Base):
    __tablename__ = "clerk_webhook_events"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    episode_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("episodes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

