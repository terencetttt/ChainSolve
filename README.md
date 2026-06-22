# DYOR Tool

> The internet's first on-chain AI project verifier. Permanent, trustless crypto research.

Built on [GenLayer](https://genlayer.com) — Intelligent Contracts that read the web and reason with AI.

---

## What It Does

Paste a crypto project name, website URL, and optional GitHub link. The AI fetches live data from 3 independent sources, scores the project across 5 dimensions, and writes a permanent verdict on-chain that nobody can delete or change.

---

## Features

| Feature | Description |
|---------|-------------|
| Project analysis | AI fetches website + DuckDuckGo news + GitHub API |
| 5-dimension scorecard | Team, Technology, Promises, Community, Security (0–10 each) |
| Verdict label | SAFE (36–50) · CAUTION (21–35) · RED FLAG (0–20) |
| Evidence trail | Specific red flags and positives from the AI |
| Project type scoring | DeFi, NFT, Meme, Infrastructure — scoring criteria adjust per type |
| Project registry | Browse every analyzed project, sorted by score |
| Analysis history | Re-analyze anytime — old verdicts preserved on-chain |
| Side-by-side comparison | Compare two projects' full scorecards |

---

## Project Structure

```
dyor-tool/
├── contracts/
│   └── dyor_tool.py          ← GenLayer Intelligent Contract
└── app/
    ├── src/
    │   ├── main.ts
    │   └── App.vue            ← Complete dApp (all views + logic)
    ├── index.html
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    └── .env.example
```

---

## Setup

### 1. Deploy the contract

In GenLayer Studio (`http://localhost:8080`), paste `contracts/dyor_tool.py` and deploy. Copy the contract address.

Or via CLI:
```bash
npm install -g @genlayer/cli
genlayer init && genlayer up
genlayer deploy contracts/dyor_tool.py
```

### 2. Configure the frontend

```bash
cd app
cp .env.example .env
# Edit .env and paste your contract address
```

### 3. Run

```bash
npm install
npm run dev
```

Open `http://localhost:5173`.

---

## Contract API

### Write
| Method | Args | Description |
|--------|------|-------------|
| `analyze_project` | `name, project_type, website_url, github_url` | Full AI analysis |
| `request_reanalysis` | `project_name` | Re-run analysis on existing project |

### View
| Method | Args | Returns |
|--------|------|---------|
| `get_project` | `project_name` | Latest analysis + metadata |
| `get_analysis_history` | `project_name` | All past verdicts |
| `get_all_projects` | — | Registry summary list |
| `compare_projects` | `name1, name2` | Both projects' full data |
| `get_project_count` | — | Total projects analyzed |

---

## How the AI Scores

Each validator independently:
1. Fetches the project website
2. Searches DuckDuckGo for news and reviews
3. Queries the GitHub API for code activity
4. Passes all data to an LLM with type-specific scoring instructions
5. Returns structured JSON with 5 scores + evidence

All validators must agree (Equivalence Principle) before the result is written on-chain.

### Scoring criteria by project type

- **DeFi** — full standard analysis across all 5 dimensions
- **NFT** — tech score adjusted (no GitHub expected), community weighted higher
- **Meme** — promise/team scores adjusted (anonymity acceptable), community is primary
- **Infrastructure** — tech score critical, team must be doxxed, multiple audits expected

---

## License

MIT
