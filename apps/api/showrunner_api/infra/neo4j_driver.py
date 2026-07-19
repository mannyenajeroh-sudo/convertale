from neo4j import AsyncDriver, AsyncGraphDatabase

from showrunner_api.config import get_settings


class Neo4jClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.database = settings.neo4j_database
        self._driver: AsyncDriver | None = None
        if settings.neo4j_uri and settings.neo4j_password:
            self._driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_username, settings.neo4j_password),
            )

    @property
    def driver(self) -> AsyncDriver:
        if self._driver is None:
            raise RuntimeError("Neo4j is not configured")
        return self._driver

    async def verify_connectivity(self) -> bool:
        await self.driver.verify_connectivity()
        return True

    async def close(self) -> None:
        if self._driver:
            await self._driver.close()


neo4j_client = Neo4jClient()
