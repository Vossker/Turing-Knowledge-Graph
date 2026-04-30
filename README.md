# Alan Turing Knowledge Graph

本项目构建了一个以 **Alan Turing（艾伦·图灵）** 为核心的知识图谱系统。项目从互联网公开资料中采集与图灵相关的文本，通过实体抽取、实体规范化、语义消歧、关系抽取等步骤，自动生成结构化三元组，并将结果写入 Neo4j 图数据库，最终实现图谱查询与可视化展示。

本项目不是基于手工编写 CSV 文件导入图数据库，而是以“互联网文本 → 信息抽取 → 语义消歧 → 关系抽取 → Neo4j 入库 → 图谱可视化”为完整流程构建知识图谱。

---

## 1. 项目目标

本项目旨在围绕 Alan Turing 构建一个小型主题知识图谱，用于组织和分析图灵相关的人物、机构、地点、论文、理论概念、机器系统和历史事件之间的关系。

系统希望能够回答如下问题：

1. Alan Turing 的重要理论贡献有哪些？
2. 图灵与哪些机构、人物、事件有关？
3. Turing Machine、Turing Test、Computability、Artificial Intelligence 之间有什么关系？
4. 图灵在密码学、人工智能和计算机科学中的贡献如何体现？
5. 图灵相关知识能否以图结构方式进行路径查询和可视化展示？

---

## 2. 技术路线

项目整体流程如下：

```text
互联网资料采集
    ↓
网页正文抽取与清洗
    ↓
句子切分
    ↓
实体抽取
    ↓
实体规范化与语义消歧
    ↓
关系抽取
    ↓
三元组生成
    ↓
Neo4j 图数据库存储
    ↓
Cypher 查询与图谱可视化
```

## 3. 项目特点

本项目主要包含以下特点：

1. 自动化文本采集  
   从互联网公开资料中采集图灵相关文本，而非完全手工录入数据。
2. 实体抽取  
   结合 spaCy 通用命名实体识别与领域词典，抽取人物、机构、地点、论文、概念、机器和事件等实体。
3. 语义消歧  
   通过别名字典、上下文规则和字符串相似度方法，对实体进行规范化处理。例如：

   ```text
   Turing → Alan Turing
   Alan Mathison Turing → Alan Turing
   NPL → National Physical Laboratory
   ACE → Automatic Computing Engine
   Imitation Game → Turing Test
   ```

4. 关系抽取  
   基于规则模板从句子中识别实体间关系，如 AUTHORED、PROPOSED、WORKED_AT、DESIGNED 等。
5. 证据保留  
   每条关系都保留来源句子、来源文档、抽取方法和置信度，便于人工验证和结果追溯。
6. Neo4j 存储与可视化  
   使用 Neo4j 存储图结构数据，并通过 Cypher 查询和 PyVis 生成交互式 HTML 图谱。

## 4. 知识图谱本体设计

### 4.1 节点类型

本项目定义了以下节点类型：

| 节点类型 | 含义 | 示例 |
| --- | --- | --- |
| Person | 人物 | Alan Turing, Alonzo Church, Joan Clarke |
| Organization | 机构 | Bletchley Park, King's College Cambridge |
| Place | 地点 | London, Cambridge, Wilmslow |
| Work | 论文、著作或档案材料 | On Computable Numbers |
| Concept | 理论概念 | Turing Machine, Turing Test |
| Machine | 机器或系统 | Enigma, Bombe, Automatic Computing Engine |
| Event | 历史事件 | World War II Codebreaking |
| Field | 学科领域 | Artificial Intelligence, Computer Science |

### 4.2 关系类型

本项目定义了以下关系类型：

| 关系类型 | 含义 |
| --- | --- |
| BORN_IN | 出生于 |
| DIED_IN | 去世于 |
| STUDIED_AT | 就读于 |
| WORKED_AT | 工作于 |
| AUTHORED | 撰写或发表 |
| PROPOSED | 提出 |
| DESIGNED | 设计 |
| CONTRIBUTED_TO | 贡献于 |
| COLLABORATED_WITH | 合作 |
| RELATED_TO | 相关 |
| INFLUENCED | 影响 |
| PARTICIPATED_IN | 参与 |
| LOCATED_IN | 位于 |

## 5. 项目目录结构

```text
turing_kg_project/
│
├── data/
│   ├── raw/
│   │   ├── source_1.txt
│   │   ├── source_2.txt
│   │   └── source_3.txt
│   │
│   └── processed/
│       ├── sentences.json
│       ├── entities_raw.json
│       ├── entities_normalized.json
│       ├── triples_raw.json
│       └── triples_final.json
│
├── scripts/
│   ├── 01_crawl.py
│   ├── 02_preprocess.py
│   ├── 03_ner.py
│   ├── 04_disambiguation.py
│   ├── 05_relation_extraction.py
│   ├── 06_import_neo4j.py
│   └── 07_visualize.py
│
├── output/
│   └── turing_knowledge_graph.html
│
├── requirements.txt
└── README.md
```

## 6. 环境依赖

### 6.1 Python 环境

建议使用：

```text
Python 3.10+
```

安装依赖：

```bash
pip install -r requirements.txt
```

如果没有 requirements.txt，可以手动安装：

```bash
pip install requests beautifulsoup4 trafilatura spacy neo4j pandas tqdm rapidfuzz networkx pyvis
python -m spacy download en_core_web_sm
```

### 6.2 requirements.txt 示例

```text
requests
beautifulsoup4
trafilatura
spacy
neo4j
pandas
tqdm
rapidfuzz
networkx
pyvis
```

安装 spaCy 英文模型：

```bash
python -m spacy download en_core_web_sm
```

### 6.3 Neo4j 环境

需要安装：

```text
Neo4j Desktop 或 Neo4j Community Server
```

默认连接配置：

| 项 | 值 |
| --- | --- |
| URI | bolt://localhost:7687 |
| User | neo4j |
| Password | 请修改为自己的 Neo4j 密码 |
| Database | neo4j |

在 scripts/06_import_neo4j.py 和 scripts/07_visualize.py 中修改：

```python
URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "你的密码"
DATABASE = "neo4j"
```

## 7. 数据来源

本项目可使用以下公开网页作为原始资料来源：

| 数据源 | 内容 |
| --- | --- |
| Britannica | Alan Turing 生平与贡献 |
| Stanford Encyclopedia of Philosophy | Turing Machine、可计算性等理论内容 |
| Turing Digital Archive | 图灵相关档案资料 |
| Cambridge ArchiveSearch | 图灵论文与历史档案 |

可在 scripts/01_crawl.py 中维护待采集 URL 列表：

```python
URLS = [
    "https://www.britannica.com/biography/Alan-Turing",
    "https://plato.stanford.edu/entries/turing-machine/",
    "https://plato.stanford.edu/entries/turing/",
    "https://turingarchive.kings.cam.ac.uk/node/2",
]
```

## 8. 运行流程

### 8.1 第一步：采集网页文本

```bash
python scripts/01_crawl.py
```

输出结果：

```text
data/raw/source_1.txt
data/raw/source_2.txt
data/raw/source_3.txt
...
```

该步骤会从指定 URL 中抓取网页正文，并保存为本地文本文件。

### 8.2 第二步：文本预处理与句子切分

```bash
python scripts/02_preprocess.py
```

输出结果：

```text
data/processed/sentences.json
```

该步骤会对原始文本进行句子切分，为后续实体抽取和关系抽取提供输入。

### 8.3 第三步：实体抽取

```bash
python scripts/03_ner.py
```

输出结果：

```text
data/processed/entities_raw.json
```

该步骤结合 spaCy NER 和领域词典识别实体，包括人物、机构、地点、论文、概念、机器等。

### 8.4 第四步：实体规范化与语义消歧

```bash
python scripts/04_disambiguation.py
```

输出结果：

```text
data/processed/entities_normalized.json
```

该步骤会将不同写法的同一实体进行合并，并根据上下文规则处理歧义实体。

示例：

```text
Turing → Alan Turing
NPL → National Physical Laboratory
ACE → Automatic Computing Engine
Imitation Game → Turing Test
```

### 8.5 第五步：关系抽取

```bash
python scripts/05_relation_extraction.py
```

输出结果：

```text
data/processed/triples_raw.json
data/processed/triples_final.json
```

该步骤会根据实体共现和触发词模板抽取关系三元组。

三元组格式示例：

```json
{
  "head": "Alan Turing",
  "head_label": "Person",
  "relation": "PROPOSED",
  "tail": "Turing Machine",
  "tail_label": "Concept",
  "sentence": "Turing machines were first described by Alan Turing in 1936-7.",
  "source": "source_2.txt",
  "confidence": 0.95,
  "method": "curated_rule"
}
```

### 8.6 第六步：导入 Neo4j

确保 Neo4j 数据库已经启动，然后执行：

```bash
python scripts/06_import_neo4j.py
```

该步骤会将 triples_final.json 中的实体和关系写入 Neo4j。

导入完成后，可以在 Neo4j Browser / Query 中执行：

```cypher
MATCH (n)
RETURN labels(n) AS labels, count(n) AS count;
```

查看各类节点数量。

### 8.7 第七步：生成图谱可视化 HTML

```bash
python scripts/07_visualize.py
```

输出结果：

```text
output/turing_knowledge_graph.html
```

打开该 HTML 文件，即可查看可交互的图谱可视化结果。

## 9. Neo4j 查询示例

### 9.1 查看 Alan Turing 的一跳关系

```cypher
MATCH path = (:Person {name: "Alan Turing"})-[r]-(n)
RETURN path;
```

### 9.2 查看 Alan Turing 发表过的作品

```cypher
MATCH (:Person {name: "Alan Turing"})-[:AUTHORED]->(w:Work)
RETURN w.name AS work;
```

### 9.3 查看 Alan Turing 提出的概念

```cypher
MATCH (:Person {name: "Alan Turing"})-[:PROPOSED]->(c:Concept)
RETURN c.name AS concept;
```

### 9.4 查看图灵与人工智能之间的路径

```cypher
MATCH path = (:Person {name: "Alan Turing"})-[*1..3]-(:Field {name: "Artificial Intelligence"})
RETURN path;
```

### 9.5 查看关系证据句

```cypher
MATCH (:Person {name: "Alan Turing"})-[r]->(n)
RETURN type(r) AS relation,
       n.name AS target,
       r.confidence AS confidence,
       r.evidence AS evidence
ORDER BY confidence DESC;
```

### 9.6 查看关系类型统计

```cypher
MATCH ()-[r]->()
RETURN type(r) AS relation, count(r) AS count
ORDER BY count DESC;
```

## 10. 实体消歧方法说明

本项目采用三类方法进行实体消歧：

### 10.1 别名字典

将同一实体的不同写法统一为标准名称。

示例：

```text
Alan Mathison Turing → Alan Turing
A. M. Turing → Alan Turing
NPL → National Physical Laboratory
ACE → Automatic Computing Engine
```

### 10.2 上下文规则

根据实体所在句子的上下文判断实体类型和真实含义。

示例：

1. 当 Church 与 lambda calculus、computability 或 Turing 同句出现时，判定为人物 Alonzo Church。
2. 当 Turing Machine 出现时，将其类型判定为 Concept，而不是普通机器。
3. 当 ACE 与 computer、NPL 或 engine 同句出现时，判定为 Automatic Computing Engine。

### 10.3 字符串相似度

使用 rapidfuzz 对实体名称进行相似度计算，辅助合并拼写相近的实体。

## 11. 关系抽取方法说明

本项目使用基于规则模板的关系抽取方法。

系统首先对句子进行实体识别，然后根据实体类型和触发词抽取关系。

示例规则：

| 触发词 | 实体类型组合 | 关系 |
| --- | --- | --- |
| born in, was born in | Person + Place | BORN_IN |
| died in, died at | Person + Place | DIED_IN |
| studied at, educated at | Person + Organization | STUDIED_AT |
| worked at, joined | Person + Organization | WORKED_AT |
| wrote, published, authored | Person + Work | AUTHORED |
| proposed, introduced, described | Person + Concept | PROPOSED |
| designed, developed | Person + Machine | DESIGNED |
| contributed to, foundations of | Person + Field | CONTRIBUTED_TO |

每条关系会保存以下信息：

| 字段 | 含义 |
| --- | --- |
| head | 头实体 |
| relation | 关系类型 |
| tail | 尾实体 |
| source | 来源文档 |
| evidence | 证据句 |
| confidence | 置信度 |
| method | 抽取方法 |

## 12. 可视化结果

本项目提供两种可视化方式：

### 12.1 Neo4j Browser / Query 可视化

在 Neo4j 中执行：

```cypher
MATCH path = (:Person {name: "Alan Turing"})-[*1..2]-(n)
RETURN path
LIMIT 100;
```

即可在 Graph 视图中查看知识图谱。

### 12.2 PyVis HTML 可视化

运行：

```bash
python scripts/07_visualize.py
```

生成：

```text
output/turing_knowledge_graph.html
```

可在浏览器中打开该文件查看交互式图谱。

## 13. 项目输出

项目最终输出包括：

1. 原始网页文本
2. 句子切分结果
3. 原始实体抽取结果
4. 实体规范化与消歧结果
5. 关系三元组结果
6. Neo4j 图数据库
7. Cypher 查询结果
8. HTML 可视化图谱
