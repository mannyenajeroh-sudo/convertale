import uuid
from typing import Any, Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from showrunner_api.models.core import SeriesBible

CharacterSlot = Literal["primary", "secondary"]
LockSource = Literal["user_upload", "auto_bootstrap"]


class SeriesBibleService:
    """Owns the per-project SeriesBible row, including the character-lock
    scaffolding used to keep a character's face/appearance consistent across
    an episode's shots and across episodes.

    Supports up to two independently-lockable, named character slots:
    "primary" (the protagonist) and "secondary" (optional — e.g. a sidekick
    or antagonist). Each slot tracks:
      - name: the character's name, used to match storyboard/routing output
        against this slot (see storyboard.py's "characters_in_shot" field).
      - appearance_prompt: text description, used for t2v generation before
        a lock exists and as VL judge context afterwards.
      - ref_image_path: path to a locked reference still image, used both by
        VideoRoutingAgent (i2v conditioning) and VisualCriticAgent (identity
        judging).
      - locked: bool — whether ref_image_path should be treated as an
        authoritative identity anchor.
      - lock_source: "user_upload" (locked via the character-upload endpoint,
        the intentionally chosen face) or "auto_bootstrap" (system extracted
        a still from the first successfully rendered shot and locked it there
        so later shots in the same episode stay consistent, absent a user
        upload). Routing/critic don't currently branch on this value, but it
        is preserved so a future "re-roll only unlocked/auto characters"
        feature doesn't have to guess how a lock was obtained.

    Method signatures are kept backward-compatible (same required
    positional/keyword args as before); slot/lock_source are additive
    optional kwargs.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create(self, project_id: uuid.UUID, title: str = "") -> SeriesBible:
        result = await self.db.execute(select(SeriesBible).where(SeriesBible.project_id == project_id))
        bible = result.scalars().first()
        if not bible:
            bible = SeriesBible(
                project_id=project_id,
                title=title,
                characters_json={},
                props=[],
                locations=[],
                plot_threads=[],
                episodes=[],
            )
            self.db.add(bible)
            await self.db.flush()
        return bible

    async def upsert_character(
        self,
        project_id: uuid.UUID,
        name: str,
        appearance_prompt: str,
        ref_image_path: str | None = None,
        slot: CharacterSlot | None = None,
    ) -> dict[str, Any]:
        """Create or update a character by name. If `slot` is omitted, infers
        "primary" for the first character ever added to this bible and
        "secondary" for the next, so existing callers (e.g. campaigns.py
        seeding a protagonist) don't need to know about slots at all.
        """
        bible = await self.get_or_create(project_id)
        chars = bible.characters_json or {}

        char = chars.get(name)
        if char is None:
            if slot is None:
                taken_slots = {c.get("slot") for c in chars.values() if isinstance(c, dict)}
                slot = "primary" if "primary" not in taken_slots else "secondary"
            char = {
                "slot": slot,
                "appearance_prompt": appearance_prompt,
                "ref_image_path": ref_image_path,
                "locked": False,
                "lock_source": None,
            }
            chars[name] = char
        else:
            if not char.get("locked"):
                char["appearance_prompt"] = appearance_prompt
            if ref_image_path is not None:
                char["ref_image_path"] = ref_image_path
            if slot is not None:
                char["slot"] = slot
            char.setdefault("lock_source", None)

        # SQLAlchemy needs to know JSON was mutated (if we updated in place, sometimes it doesn't trigger)
        # So we re-assign the dict.
        bible.characters_json = dict(chars)
        await self.db.commit()
        return char

    async def lock_character(
        self,
        project_id: uuid.UUID,
        name: str,
        ref_image_path: str | None = None,
        lock_source: LockSource = "user_upload",
    ) -> dict[str, Any] | None:
        """Locks a character's identity to a reference still. If the
        character doesn't exist yet, creates it first (this is what makes
        the upload endpoint a one-call "create + lock" operation)."""
        bible = await self.get_or_create(project_id)
        chars = bible.characters_json or {}

        char = chars.get(name)
        if char is None:
            taken_slots = {c.get("slot") for c in chars.values() if isinstance(c, dict)}
            char = {
                "slot": "primary" if "primary" not in taken_slots else "secondary",
                "appearance_prompt": "",
                "ref_image_path": None,
                "locked": False,
                "lock_source": None,
            }
            chars[name] = char

        char["locked"] = True
        char["lock_source"] = lock_source
        if ref_image_path is not None:
            char["ref_image_path"] = ref_image_path

        bible.characters_json = dict(chars)
        await self.db.commit()
        return char

    async def unlock_character(self, project_id: uuid.UUID, name: str) -> None:
        bible = await self.get_or_create(project_id)
        chars = bible.characters_json or {}
        if name in chars:
            chars[name]["locked"] = False
            chars[name]["lock_source"] = None
            bible.characters_json = dict(chars)
            await self.db.commit()

    async def get_character(self, project_id: uuid.UUID, name: str) -> dict[str, Any] | None:
        bible = await self.get_or_create(project_id)
        return (bible.characters_json or {}).get(name)

    async def get_character_by_slot(
        self, project_id: uuid.UUID, slot: CharacterSlot
    ) -> tuple[str, dict[str, Any]] | None:
        """Returns (name, character_dict) for whichever character currently
        occupies `slot`, or None if that slot is empty."""
        bible = await self.get_or_create(project_id)
        for name, char in (bible.characters_json or {}).items():
            if isinstance(char, dict) and char.get("slot") == slot:
                return name, char
        return None

    async def list_characters(self, project_id: uuid.UUID) -> dict[str, dict[str, Any]]:
        bible = await self.get_or_create(project_id)
        return dict(bible.characters_json or {})

    async def get_locked_reference_images(self, project_id: uuid.UUID) -> dict[str, str]:
        """Returns {character_name: ref_image_path} for every currently
        locked character that has a reference image on disk. Used by
        VideoRoutingAgent to decide which shots get i2v conditioning and by
        VisualCriticAgent as the drift-guardrail anchor set."""
        chars = await self.list_characters(project_id)
        out: dict[str, str] = {}
        for name, char in chars.items():
            if isinstance(char, dict) and char.get("locked") and char.get("ref_image_path"):
                out[name] = char["ref_image_path"]
        return out

    async def set_character_slot(
        self,
        project_id: uuid.UUID,
        slot: CharacterSlot,
        name: str,
        ref_image_path: str,
        appearance_prompt: str = "",
    ) -> dict[str, Any]:
        """Used by the character-upload endpoint: assigns `name` to `slot`
        and locks it to `ref_image_path`, in one call. If a *different*
        character was previously occupying this slot, it's removed first —
        a slot re-upload should replace, not duplicate, whoever was there
        (e.g. the user decides "the sidekick" is actually named differently
        and re-uploads)."""
        bible = await self.get_or_create(project_id)
        chars = bible.characters_json or {}

        stale = [n for n, c in chars.items() if isinstance(c, dict) and c.get("slot") == slot and n != name]
        for n in stale:
            del chars[n]

        chars[name] = {
            "slot": slot,
            "appearance_prompt": appearance_prompt,
            "ref_image_path": ref_image_path,
            "locked": True,
            "lock_source": "user_upload",
        }
        bible.characters_json = dict(chars)
        await self.db.commit()
        return chars[name]
