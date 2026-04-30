from neo4j import GraphDatabase
from pyvis.network import Network
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if PROJECT_ROOT.name == "scripts":
    PROJECT_ROOT = PROJECT_ROOT.parent

OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "turing_knowledge_graph.html"

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "12345678"
DATABASE = "neo4j"

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

query = """
MATCH path = (:Person {name: "Alan Turing"})-[r*1..2]-(n)
UNWIND relationships(path) AS rel
WITH DISTINCT rel
MATCH (a)-[rel]->(b)
RETURN a.name AS source,
       labels(a) AS source_labels,
       type(rel) AS relation,
       b.name AS target,
       labels(b) AS target_labels,
       rel.confidence AS confidence
LIMIT 200
"""

with driver.session(database=DATABASE) as session:
    rows = session.run(query).data()

driver.close()

color_map = {
    "Person": "#8dd3c7",
    "Organization": "#ffffb3",
    "Place": "#bebada",
    "Work": "#fb8072",
    "Concept": "#80b1d3",
    "Machine": "#fdb462",
    "Event": "#b3de69",
    "Field": "#fccde5",
    "Entity": "#d9d9d9",
}


def main_label(labels):
    for label in labels:
        if label != "Entity":
            return label
    return "Entity"


def normalize_html_layout(html_path: Path) -> None:
    html = html_path.read_text(encoding="utf-8")
    html = html.replace(
        """        <style type="text/css">

             #mynetwork {
                 width: 100%;
                 height: 800px;
                 background-color: #ffffff;
                 border: 1px solid lightgray;
                 position: relative;
                 float: left;
             }

             

             

             
        </style>
""",
        """        <style type="text/css">
             html, body {
                 width: 100%;
                 height: 100%;
                 margin: 0;
                 padding: 0;
                 overflow: hidden;
                 background-color: #ffffff;
             }

             #mynetwork {
                 width: 100vw;
                 height: 100vh;
                 background-color: #ffffff;
                 border: 0;
                 position: relative;
                 display: block;
             }
        </style>
"""
    )
    html = html.replace(
        """    <body>
        <div class="card" style="width: 100%">
            
            
            <div id="mynetwork" class="card-body"></div>
        </div>
""",
        """    <body>
        <div id="mynetwork"></div>
"""
    )
    html_path.write_text(html, encoding="utf-8")


net = Network(height="800px", width="100%", directed=True, notebook=False)

for row in rows:
    s_label = main_label(row["source_labels"])
    t_label = main_label(row["target_labels"])

    net.add_node(
        row["source"],
        label=row["source"],
        title=s_label,
        color=color_map.get(s_label, "#d9d9d9")
    )

    net.add_node(
        row["target"],
        label=row["target"],
        title=t_label,
        color=color_map.get(t_label, "#d9d9d9")
    )

    net.add_edge(
        row["source"],
        row["target"],
        label=row["relation"],
        title=f"confidence={row.get('confidence')}"
    )

net.repulsion(node_distance=180, spring_length=200)
net.show(str(OUTPUT_FILE), notebook=False)
normalize_html_layout(OUTPUT_FILE)

print(f"Saved: {OUTPUT_FILE}")
