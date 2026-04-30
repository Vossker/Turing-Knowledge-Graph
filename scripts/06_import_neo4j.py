import json
from pathlib import Path
from neo4j import GraphDatabase

PROJECT_ROOT = Path(__file__).resolve().parent
if PROJECT_ROOT.name == "scripts":
    PROJECT_ROOT = PROJECT_ROOT.parent

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "12345678"
DATABASE = "neo4j"

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

ALLOWED_LABELS = {
    "Person",
    "Organization",
    "Place",
    "Work",
    "Concept",
    "Machine",
    "Event",
    "Field",
}

ALLOWED_RELATIONS = {
    "BORN_IN",
    "DIED_IN",
    "STUDIED_AT",
    "WORKED_AT",
    "AUTHORED",
    "PROPOSED",
    "DESIGNED",
    "CONTRIBUTED_TO",
    "COLLABORATED_WITH",
    "RELATED_TO",
    "INFLUENCED",
    "PARTICIPATED_IN",
    "LOCATED_IN",
}


def safe_label(label: str) -> str:
    return label if label in ALLOWED_LABELS else "Entity"


def safe_relation(rel: str) -> str:
    return rel if rel in ALLOWED_RELATIONS else "RELATED_TO"


def initialize_schema(tx):
    tx.run("""
    CREATE CONSTRAINT entity_name_unique IF NOT EXISTS
    FOR (n:Entity)
    REQUIRE n.name IS UNIQUE
    """)


def create_entity(tx, name, label):
    label = safe_label(label)
    query = f"""
    MERGE (n:Entity:{label} {{name: $name}})
    SET n.label = $label
    RETURN n
    """
    tx.run(query, name=name, label=label)


def create_relation(tx, triple):
    head_label = safe_label(triple["head_label"])
    tail_label = safe_label(triple["tail_label"])
    rel = safe_relation(triple["relation"])

    query = f"""
    MERGE (h:Entity:{head_label} {{name: $head}})
    SET h.label = $head_label
    MERGE (t:Entity:{tail_label} {{name: $tail}})
    SET t.label = $tail_label
    MERGE (h)-[r:{rel}]->(t)
    SET r.confidence = $confidence,
        r.source = $source,
        r.evidence = $sentence,
        r.method = $method
    RETURN h, r, t
    """

    tx.run(
        query,
        head=triple["head"],
        tail=triple["tail"],
        head_label=head_label,
        tail_label=tail_label,
        confidence=float(triple.get("confidence", 0.7)),
        source=triple.get("source", ""),
        sentence=triple.get("sentence", ""),
        method=triple.get("method", "")
    )


triples = json.loads((PROCESSED_DIR / "triples_final.json").read_text(encoding="utf-8"))

with driver.session(database=DATABASE) as session:
    session.execute_write(initialize_schema)
    for t in triples:
        session.execute_write(create_entity, t["head"], t["head_label"])
        session.execute_write(create_entity, t["tail"], t["tail_label"])
        session.execute_write(create_relation, t)

driver.close()

print("Imported triples to Neo4j:", len(triples))
