"""ORM models package.

Re-exports every mapped class from ``core.py`` so callers can write
``from showrunner_api.models import Project`` etc. Previously this
``__init__.py`` did not exist, which made every such import fail with
``ImportError: cannot import name 'X' from 'showrunner_api.models'``
(implicit namespace packages don't expose submodule attributes at the
package level without an explicit re-export).
"""

from showrunner_api.models.base import Base
from showrunner_api.models.core import (
    AgentJob,
    Asset,
    ClerkWebhookEvent,
    Episode,
    Lead,
    McpConnector,
    Project,
    PublishRecord,
    Scene,
    SeriesBible,
    Shot,
    UsageRecord,
    User,
    Workspace,
)

__all__ = [
    "Base",
    "User",
    "Workspace",
    "Project",
    "SeriesBible",
    "Episode",
    "Scene",
    "Shot",
    "AgentJob",
    "Asset",
    "McpConnector",
    "PublishRecord",
    "UsageRecord",
    "ClerkWebhookEvent",
    "Lead",
]
