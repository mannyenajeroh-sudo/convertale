from typing import Any

from showrunner_api.infra.neo4j_driver import neo4j_client


class GraphMemoryService:
    """Typed Neo4j boundary. Raw Cypher stays in this service layer."""

    async def verify_connectivity(self) -> bool:
        return await neo4j_client.verify_connectivity()

    async def get_character_facts(
        self, project_id: str, character_id: str, before_episode_n: int | None = None
    ) -> list[dict[str, Any]]:
        query = """
        MATCH (:Project {id: $project_id})-[:HAS_CHARACTER]->(c:Character {id: $character_id})
        OPTIONAL MATCH (c)-[:ESTABLISHED]->(f:Fact)
        WHERE $before_episode_n IS NULL OR f.established_episode < $before_episode_n
        RETURN f
        """
        async with neo4j_client.driver.session(database=neo4j_client.database) as session:
            result = await session.run(
                query,
                project_id=project_id,
                character_id=character_id,
                before_episode_n=before_episode_n,
            )
            return [record["f"] for record in await result.data()]

    async def get_world_rules(self, project_id: str) -> list[dict[str, Any]]:
        query = "MATCH (:Project {id: $project_id})-[:HAS_RULE]->(r:WorldRule) RETURN r"
        async with neo4j_client.driver.session(database=neo4j_client.database) as session:
            result = await session.run(query, project_id=project_id)
            return [record["r"] for record in await result.data()]

    async def find_similar_scenes(
        self, embedding: list[float], project_id: str, limit: int = 5
    ) -> list[dict[str, Any]]:
        query = """
        CALL db.index.vector.queryNodes('scene_embeddings', $limit, $embedding)
        YIELD node, score
        MATCH (node)-[:PART_OF]->(:Episode)-[:PART_OF_PROJECT]->(:Project {id: $project_id})
        RETURN node, score
        ORDER BY score DESC
        """
        async with neo4j_client.driver.session(database=neo4j_client.database) as session:
            result = await session.run(
                query, embedding=embedding, project_id=project_id, limit=limit
            )
            return await result.data()

    async def record_fact(
        self,
        project_id: str,
        subject_node_id: str,
        relationship: str,
        object_node_id: str,
        episode_n: int,
    ) -> None:
        query = """
        MATCH (p:Project {id: $project_id})
        MATCH (subject {id: $subject_node_id})
        MATCH (object {id: $object_node_id})
        CREATE (fact:Fact {
          id: randomUUID(),
          statement: $relationship,
          confidence: 1.0,
          established_episode: $episode_n
        })
        CREATE (subject)-[:ESTABLISHED]->(fact)
        CREATE (fact)-[:ABOUT]->(object)
        """
        async with neo4j_client.driver.session(database=neo4j_client.database) as session:
            await session.run(
                query,
                project_id=project_id,
                subject_node_id=subject_node_id,
                relationship=relationship,
                object_node_id=object_node_id,
                episode_n=episode_n,
            )
