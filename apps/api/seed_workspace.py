
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from showrunner_api.config import get_settings

async def seed():
    settings = get_settings()
    # Pass the database url string directly
    engine = create_async_engine(str(settings.database_url))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        query = text("""
            INSERT INTO workspaces (id, clerk_org_id, name, plan, render_minutes_cap, render_minutes_used)
            VALUES (\x2700000000-0000-0000-0000-000000000001\x27, \x27mock_org_id\x27, \x27Default Workspace\x27, \x27free\x27, 6, 0)
            ON CONFLICT (id) DO NOTHING;
        """)
        await session.execute(query)
        await session.commit()
    print("Successfully injected workspace placeholder into Neon DB!")

asyncio.run(seed())

