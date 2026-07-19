"""One-off script to provision Neo4j AuraDB constraints and vector indexes.

Run with: `python scripts/init_neo4j.py` (requires NEO4J_URI, NEO4J_USERNAME,
NEO4J_PASSWORD in the environment).
"""

import os
import sys

from neo4j import GraphDatabase

# NOTE: previously read os.getenv("NEO4J_USER"), but every other part of the
# project (config.py, .env.example) uses NEO4J_USERNAME. That mismatch meant
# `username` was always None here, so the script would auth-fail the moment
# anyone ran it against a real Aura instance requiring credentials.
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


def create_constraints(tx):
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Character) REQUIRE c.id IS UNIQUE")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (l:Location) REQUIRE l.id IS UNIQUE")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Scene) REQUIRE s.id IS UNIQUE")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Episode) REQUIRE e.id IS UNIQUE")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE")


def create_vector_indexes(tx):
    tx.run("""CREATE VECTOR INDEX character_embeddings IF NOT EXISTS
        FOR (c:Character) ON (c.embedding)
        OPTIONS {indexConfig: {`vector.dimensions`: 1536, `vector.similarity_function`: 'cosine'}}""")
    tx.run("""CREATE VECTOR INDEX scene_embeddings IF NOT EXISTS
        FOR (s:Scene) ON (s.embedding)
        OPTIONS {indexConfig: {`vector.dimensions`: 1536, `vector.similarity_function`: 'cosine'}}""")
    tx.run("""CREATE VECTOR INDEX location_embeddings IF NOT EXISTS
        FOR (l:Location) ON (l.embedding)
        OPTIONS {indexConfig: {`vector.dimensions`: 1536, `vector.similarity_function`: 'cosine'}}""")


def main() -> int:
    if not NEO4J_URI or not NEO4J_PASSWORD:
        print("NEO4J_URI and NEO4J_PASSWORD must be set in the environment.", file=sys.stderr)
        return 1

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    try:
        with driver.session() as session:
            session.execute_write(create_constraints)
            session.execute_write(create_vector_indexes)
        print("Neo4j constraints and vector indexes created.")
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
