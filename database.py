from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "你的密码"
DATABASE = "neo4j"

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


def run_query(query, parameters=None):
    with driver.session(database=DATABASE) as session:
        return session.run(query, parameters or {}).data()


# 清空旧图谱，谨慎使用
run_query("MATCH (n) DETACH DELETE n")

# 创建唯一约束
run_query("""
CREATE CONSTRAINT entity_name_unique IF NOT EXISTS
FOR (n:Entity)
REQUIRE n.name IS UNIQUE
""")