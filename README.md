# ⬡ ChainSolve

**Decentralized AI Problem Solver on GenLayer Bradbury Testnet**

Submit any problem. Multiple independent AI validators reach consensus on the solution. Sealed on-chain permanently.

🌐 **Live:** [chain-solve.vercel.app](https://chain-solve.vercel.app)

---

## What Is ChainSolve?

ChainSolve is a dApp that turns problem-solving into a verifiable, decentralized process. When you submit a problem, GenLayer's independent AI validators each analyze it separately, then reach consensus on a structured solution before committing it to Bradbury chain.

This isn't one AI giving you an answer. It's multiple independent validators agreeing on an answer — and sealing it permanently on-chain so anyone can verify it, forever.

---

## How It Works

```
User submits problem
        ↓
GenLayer validators each run independent LLM analysis
        ↓
prompt_non_comparative reaches consensus (~3–5 min on Bradbury)
        ↓
Solution sealed permanently on-chain
        ↓
Anyone can view, verify, upvote, or re-analyze
```

Every solution contains:

| Field | Description |
|---|---|
| `problem_summary` | AI restatement of the core problem |
| `root_cause` | Most likely underlying cause |
| `primary_solution` | Step-by-step actionable fix |
| `alternatives` | 2–3 other approaches |
| `risks` | What could go wrong |
| `difficulty` | EASY / MODERATE / COMPLEX |
| `confidence` | HIGH / MEDIUM / LOW |

---

## Features

- **Submit any problem** — Technical, Business, Personal, or Research; four severity levels
- **Live consensus tracker** — 5-stage progress display while validators work
- **Solution archive** — browse all problems with filters by category, severity, and status
- **Upvotes** — community signals which solutions are most useful
- **Mark as Solved** — submitters can confirm a solution worked in practice
- **Re-analysis** — add new context and trigger a fresh consensus with updated information
- **Re-analysis history** — every update is preserved on-chain

---

## Tech Stack

| Layer | Technology |
|---|---|
| Smart contract | Python Intelligent Contract (GenLayer) |
| Equivalence principle | `prompt_non_comparative` |
| Frontend | Vue 3 + TypeScript |
| Blockchain SDK | genlayer-js v1.1.8 |
| Deployment | Vercel |
| Network | GenLayer Bradbury Testnet (Chain ID: 4221) |

---

## Contract Details

- **Address:** `0xf07dFAE9fE1EF9f0657fC49A98476464BEd6B096`
- **Network:** GenLayer Bradbury Testnet
- **RPC:** `https://rpc-bradbury.genlayer.com`
- **Explorer:** [View on GenExplorer](https://explorer-bradbury.genlayer.com/contracts/0xf07dFAE9fE1EF9f0657fC49A98476464BEd6B096)

### Contract Functions

**Write (AI consensus)**
- `solve_problem(title, description, category, severity)` — submit and solve a problem
- `reanalyze_problem(problem_id, additional_context)` — re-run AI with new context

**Write (instant)**
- `upvote_solution(problem_id)` — upvote a solution (one per address)
- `mark_solved(problem_id)` — mark your own problem as resolved

**Read**
- `get_problem(id)` — fetch a single problem + solution
- `get_all_problems()` — fetch the full archive
- `get_problem_count()` — total problems on-chain
- `get_reanalysis(problem_id, num)` — fetch a re-analysis record
- `get_reanalysis_count(problem_id)` — how many re-analyses exist

---

## Local Development

### Prerequisites
- Node.js 18+
- Rabby or MetaMask wallet
- GEN testnet tokens from [faucet.genlayer.com](https://faucet.genlayer.com)

### Setup

```bash
git clone https://github.com/terencetttt/ChainSolve.git
cd ChainSolve
npm install
```

Create a `.env` file:
```
VITE_CONTRACT_ADDRESS=0xf07dFAE9fE1EF9f0657fC49A98476464BEd6B096
```

```bash
npm run dev
```

Open `http://localhost:5173`, connect your wallet, and submit a problem.

---

## Key Technical Decisions

**Why `prompt_non_comparative` instead of `strict_eq`?**
`strict_eq` requires byte-for-byte identical outputs across all validators. Since each validator runs its own independent LLM call, free-text fields (solutions, reasoning) will always differ slightly in wording. `prompt_non_comparative` lets validators judge whether the leader's output meets stated criteria — tolerating wording differences while enforcing structure and quality.

**Why no web fetching in the contract?**
External fetches inside `nondet()` blocks introduce reliability risk: validators hitting the same URL independently can get different responses due to caching, CAPTCHAs, or regional routing — causing legitimate `UNDETERMINED` outcomes. ChainSolve's AI reasoning is grounded in the problem description itself, which all validators have identically.

**Why `u256` instead of `bool` in storage?**
GenLayer Python contracts do not reliably support `bool` as a TreeMap value type. The upvote registry uses `u256(1)` to represent a cast vote.

---

## Built By

[@terencetttt](https://github.com/terencetttt) — building on GenLayer Bradbury as part of the GenLayer Developer Program.

Part of a series: [GenZa](https://github.com/terencetttt/GenZa) · [Ghaza Court](https://github.com/terencetttt/Ghaza-Court) · **ChainSolve**
