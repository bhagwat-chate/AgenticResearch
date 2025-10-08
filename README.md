# 🧠 ResearchFlow: Multi-Agent Research Automation System

ResearchFlow is a **multi-agent AI system** designed for research analysis and automated report generation.  
It orchestrates specialized agents — **Search, Reader, Analyst, and Generator** — that collaborate asynchronously through LangGraph, integrating Retrieval-Augmented Generation (RAG), memory, and external knowledge sources to enable intelligent, autonomous research workflows.

---

## 🚀 Key Features

- **Multi-Agent Collaboration** – Orchestrated via LangGraph for asynchronous coordination.  
- **Research Automation** – Automatically searches, analyzes, and summarizes academic or web content.  
- **Modular Design** – Separate agent layers for search, reading, analysis, and generation.  
- **External Knowledge Integration** – Integrates APIs like Arxiv, Tavily, and Wikipedia.  
- **Memory & Context Management** – Persistent state handling using LangGraph + Redis/PostgreSQL.  
- **RAG + LangChain Integration** – Contextual retrieval and generation for precision.  
- **CI/CD & Cloud Deployment** – Automated workflows via GitHub Actions, Docker, and AWS EC2.

---

## 🏗️ Tech Stack

| Layer | Technologies |
|-------|---------------|
| **Core Frameworks** | LangGraph · CrewAI · LangChain · RAG |
| **Agents** | Search · Reader · Analyst · Generator |
| **Backend** | FastAPI · Structlog · AsyncIO |
| **Data Layer** | Redis · PostgreSQL · AstraDB · S3 |
| **Deployment** | Docker · GitHub Actions · AWS EC2 |
| **Monitoring** | LangSmith · CloudWatch |

---

## 🧩 Project Structure

```
research-flow/
├── src/
│   ├── agents/
│   ├── orchestrator/
│   ├── utils/
│   └── config/
├── tests/
├── docs/
│   ├── 01_Overview/
│   ├── 02_Design/
│   ├── 03_Runtime/
│   ├── 04_Infra_DevOps/
│   ├── 05_Observability_Eval/
│   └── 06_Reference/
├── requirements.txt
├── requirements.lock
├── pyproject.toml
└── README.md
```

---

## ⚙️ Setup Instructions

```bash
# 1️⃣ Create virtual environment
python -m venv venv
source venv/bin/activate   # or .\venv\Scripts\activate

# 2️⃣ Install dependencies
pip install -r requirements.txt

# 3️⃣ Run the orchestrator
python -m src.orchestrator.main
```

---

## 📊 Agent Roles Overview

| Agent | Responsibility |
|--------|----------------|
| 🔍 **Search Agent** | Finds relevant papers, articles, or documents using APIs. |
| 📖 **Reader Agent** | Parses and extracts structured insights from sources. |
| 🧠 **Analyst Agent** | Synthesizes patterns, key findings, and arguments. |
| ✍️ **Generator Agent** | Creates cohesive research summaries or reports. |

---

## 🌐 Deployment Pipeline

- **CI/CD:** GitHub Actions automates testing, linting, Docker builds, and EC2 deployment.  
- **Dockerized Runtime:** Each agent and orchestrator runs as an independent container.  
- **Monitoring:** Integrated with LangSmith and CloudWatch for metrics and logs.

---

## 🧾 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

### 👤 Author
**Bhagwat Chate**  
Lead Python (AI/ML) Engineer · GenAI | LLMOps | Multi-Agent Architect  
[GitHub: bhagwat-chate](https://github.com/bhagwat-chate) · [LinkedIn: ai-with-bhagwat-chate](https://www.linkedin.com/in/ai-with-bhagwat-chate)
