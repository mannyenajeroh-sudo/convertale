import os
import redis
from neo4j import GraphDatabase

# Configuration (Ensure these match your .env or environment variables)
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

def check_redis():
    print("--- Checking Redis ---")
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, socket_connect_timeout=5)
        r.ping()
        print("✅ Redis is reachable.")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")

def check_neo4j():
    print("\n--- Checking Neo4j ---")
    try:
        with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
            driver.verify_connectivity()
            print("✅ Neo4j is reachable.")
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")

if __name__ == "__main__":
    check_redis()
    check_neo4j()