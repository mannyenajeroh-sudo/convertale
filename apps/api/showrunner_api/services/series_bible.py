import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from showrunner_api.models.core import SeriesBible


class SeriesBibleService:
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
        self, project_id: uuid.UUID, name: str, appearance_prompt: str, ref_image_path: str | None = None
    ) -> dict[str, Any]:
        bible = await self.get_or_create(project_id)
        chars = bible.characters_json or {}
        
        char = chars.get(name)
        if char is None:
            char = {
                "appearance_prompt": appearance_prompt,
                "ref_image_path": ref_image_path,
                "locked": False,
            }
            chars[name] = char
        else:
            if not char.get("locked"):
                char["appearance_prompt"] = appearance_prompt
            if ref_image_path is not None:
                char["ref_image_path"] = ref_image_path
                
        # SQLAlchemy needs to know JSON was mutated (if we updated in place, sometimes it doesn't trigger)
        # So we re-assign the dict.
        bible.characters_json = dict(chars)
        await self.db.commit()
        return char

    async def lock_character(self, project_id: uuid.UUID, name: str) -> None:
        bible = await self.get_or_create(project_id)
        chars = bible.characters_json or {}
        if name in chars:
            chars[name]["locked"] = True
            bible.characters_json = dict(chars)
            await self.db.commit()

    async def get_character(self, project_id: uuid.UUID, name: str) -> dict[str, Any] | None:
        bible = await self.get_or_create(project_id)
        return (bible.characters_json or {}).get(name)
