# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
from dataclasses import dataclass
import json
import typing

# ─────────────────────────────────────────────
#  Storage schemas
# ─────────────────────────────────────────────

@allow_storage
@dataclass
class ProblemRecord:
    id:               u256
    title:            str
    description:      str
    category:         str       # TECHNICAL | BUSINESS | PERSONAL | RESEARCH
    severity:         str       # CRITICAL | HIGH | MEDIUM | LOW
    submitter:        str       # wallet address
    status:           str       # OPEN | SOLVED
    upvote_count:     u256
    problem_summary:  str
    root_cause:       str
    primary_solution: str
    alternatives:     str
    risks:            str
    difficulty:       str       # EASY | MODERATE | COMPLEX
    confidence:       str       # HIGH | MEDIUM | LOW


@allow_storage
@dataclass
class ReanalysisRecord:
    problem_id:       u256
    reanalysis_num:   u256
    context_added:    str
    problem_summary:  str
    root_cause:       str
    primary_solution: str
    alternatives:     str
    risks:            str
    difficulty:       str
    confidence:       str


# ─────────────────────────────────────────────
#  Contract
# ─────────────────────────────────────────────

class ChainSolve(gl.Contract):
    problem_count:     u256
    problems:          TreeMap[u256, ProblemRecord]
    # Use u256 instead of bool — bool is not a safe storage type in GenLayer
    upvote_registry:   TreeMap[str, u256]   # key: "{problem_id}_{address}", value: u256(1) = voted
    # Use str keys for all TreeMaps — u256 keys are less reliable
    reanalysis_counts: TreeMap[str, u256]   # key: str(problem_id)
    reanalyses:        TreeMap[str, ReanalysisRecord]  # key: "{problem_id}_{num}"

    def __init__(self):
        self.problem_count = u256(0)

    # ── WRITE: Submit & Solve ─────────────────────────────────────────

    @gl.public.write
    def solve_problem(self, title: str, description: str, category: str, severity: str) -> None:
        sender     = str(gl.message.sender_address)
        problem_id = self.problem_count

        if severity not in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            severity = "MEDIUM"
        if category not in ["TECHNICAL", "BUSINESS", "PERSONAL", "RESEARCH"]:
            category = "TECHNICAL"

        def nondet() -> str:
            urgency_note = {
                "CRITICAL": "CRITICAL severity — prioritize immediate mitigation above all else.",
                "HIGH":     "HIGH severity — emphasize urgency and direct, fast actions.",
                "MEDIUM":   "MEDIUM severity — balance thoroughness with practicality.",
                "LOW":      "LOW severity — a thoughtful, long-term approach is appropriate.",
            }.get(severity, "")

            prompt = f"""You are ChainSolve, an expert problem-solving AI on a decentralized blockchain.
Analyze the problem below and return a structured, actionable solution.

PROBLEM TITLE: {title}
CATEGORY: {category}
SEVERITY: {severity} - {urgency_note}

DESCRIPTION:
{description}

Return ONLY a valid JSON object - no markdown, no backticks, no preamble:

{{
  "problem_summary":  "<1-2 sentence restatement of the core problem>",
  "root_cause":       "<the most likely underlying cause(s)>",
  "primary_solution": "<detailed, actionable step-by-step recommended solution>",
  "alternatives":     "<2-3 alternative approaches separated by | >",
  "risks":            "<key risks or things that could go wrong>",
  "difficulty":       "<exactly one of: EASY, MODERATE, COMPLEX>",
  "confidence":       "<exactly one of: HIGH, MEDIUM, LOW>"
}}"""

            raw = gl.nondet.exec_prompt(prompt)
            raw = raw.replace("```json", "").replace("```", "").strip()

            try:
                parsed = json.loads(raw)
                required = [
                    "problem_summary", "root_cause", "primary_solution",
                    "alternatives", "risks", "difficulty", "confidence",
                ]
                for k in required:
                    if k not in parsed or not parsed[k]:
                        parsed[k] = "not available"
                if parsed.get("difficulty") not in ["EASY", "MODERATE", "COMPLEX"]:
                    parsed["difficulty"] = "MODERATE"
                if parsed.get("confidence") not in ["HIGH", "MEDIUM", "LOW"]:
                    parsed["confidence"] = "MEDIUM"
            except Exception:
                parsed = {
                    "problem_summary":  description[:200],
                    "root_cause":       "Analysis encountered an error.",
                    "primary_solution": "Please resubmit with more detail.",
                    "alternatives":     "N/A",
                    "risks":            "N/A",
                    "difficulty":       "MODERATE",
                    "confidence":       "LOW",
                }

            return json.dumps(parsed, sort_keys=True)

        result_str = gl.eq_principle.prompt_non_comparative(
            nondet,
            task=(
                "Analyze a user-submitted problem and produce a structured solution "
                "containing: a problem summary, root cause, step-by-step primary solution, "
                "alternative approaches, risks, difficulty rating, and confidence level."
            ),
            criteria=(
                "Must return valid JSON with all 7 keys: problem_summary, root_cause, "
                "primary_solution, alternatives, risks, difficulty, confidence. "
                "difficulty must be exactly EASY, MODERATE, or COMPLEX. "
                "confidence must be exactly HIGH, MEDIUM, or LOW. "
                "Exact wording between validators need not match - only structure and key "
                "fields matter. Judge on quality of reasoning from the problem description."
            ),
        )

        try:
            result = json.loads(result_str)
        except Exception:
            result = {
                "problem_summary":  description[:200],
                "root_cause":       "Consensus parsing encountered an error.",
                "primary_solution": "Please resubmit the problem.",
                "alternatives":     "N/A",
                "risks":            "N/A",
                "difficulty":       "MODERATE",
                "confidence":       "LOW",
            }

        record = ProblemRecord(
            id               = problem_id,
            title            = title,
            description      = description,
            category         = category,
            severity         = severity,
            submitter        = sender,
            status           = "OPEN",
            upvote_count     = u256(0),
            problem_summary  = str(result.get("problem_summary",  "")),
            root_cause       = str(result.get("root_cause",       "")),
            primary_solution = str(result.get("primary_solution", "")),
            alternatives     = str(result.get("alternatives",     "")),
            risks            = str(result.get("risks",            "")),
            difficulty       = str(result.get("difficulty",       "MODERATE")),
            confidence       = str(result.get("confidence",       "MEDIUM")),
        )

        self.problems[problem_id] = record
        self.problem_count = u256(int(self.problem_count) + 1)

    # ── WRITE: Upvote ─────────────────────────────────────────────────

    @gl.public.write
    def upvote_solution(self, problem_id: int) -> None:
        sender   = str(gl.message.sender_address)
        key      = u256(problem_id)
        vote_key = str(problem_id) + "_" + sender

        if key not in self.problems:
            raise Exception("Problem not found")

        if vote_key in self.upvote_registry and int(self.upvote_registry[vote_key]) == 1:
            raise Exception("Already upvoted this problem")

        self.upvote_registry[vote_key] = u256(1)

        r = self.problems[key]
        r.upvote_count = u256(int(r.upvote_count) + 1)
        self.problems[key] = r

    # ── WRITE: Mark as Solved ─────────────────────────────────────────

    @gl.public.write
    def mark_solved(self, problem_id: int) -> None:
        sender = str(gl.message.sender_address)
        key    = u256(problem_id)

        if key not in self.problems:
            raise Exception("Problem not found")

        r = self.problems[key]

        if r.submitter != sender:
            raise Exception("Only the original submitter can mark this as solved")

        r.status = "SOLVED"
        self.problems[key] = r

    # ── WRITE: Re-analyze ────────────────────────────────────────────

    @gl.public.write
    def reanalyze_problem(self, problem_id: int, additional_context: str) -> None:
        key = u256(problem_id)

        if key not in self.problems:
            raise Exception("Problem not found")

        r             = self.problems[key]
        title         = r.title
        description   = r.description
        category      = r.category
        severity      = r.severity
        orig_solution = r.primary_solution

        def nondet() -> str:
            prompt = f"""You are ChainSolve, an expert problem-solving AI on a decentralized blockchain.
A problem has been submitted for RE-ANALYSIS with additional context.

ORIGINAL PROBLEM: {title}
CATEGORY: {category}
SEVERITY: {severity}
ORIGINAL DESCRIPTION: {description}

FIRST ANALYSIS (primary solution):
{orig_solution}

NEW CONTEXT ADDED:
{additional_context}

Return ONLY a valid JSON object - no markdown, no backticks, no preamble:

{{
  "problem_summary":  "<updated restatement incorporating new context>",
  "root_cause":       "<revised root cause if new context changes it>",
  "primary_solution": "<updated step-by-step solution with new information>",
  "alternatives":     "<updated alternatives separated by | >",
  "risks":            "<updated risks considering the new context>",
  "difficulty":       "<exactly one of: EASY, MODERATE, COMPLEX>",
  "confidence":       "<exactly one of: HIGH, MEDIUM, LOW>"
}}"""

            raw = gl.nondet.exec_prompt(prompt)
            raw = raw.replace("```json", "").replace("```", "").strip()

            try:
                parsed = json.loads(raw)
                required = [
                    "problem_summary", "root_cause", "primary_solution",
                    "alternatives", "risks", "difficulty", "confidence",
                ]
                for k in required:
                    if k not in parsed or not parsed[k]:
                        parsed[k] = "not available"
                if parsed.get("difficulty") not in ["EASY", "MODERATE", "COMPLEX"]:
                    parsed["difficulty"] = "MODERATE"
                if parsed.get("confidence") not in ["HIGH", "MEDIUM", "LOW"]:
                    parsed["confidence"] = "MEDIUM"
            except Exception:
                parsed = {
                    "problem_summary":  "Re-analysis encountered an error.",
                    "root_cause":       "Please try again.",
                    "primary_solution": "Please try again.",
                    "alternatives":     "N/A",
                    "risks":            "N/A",
                    "difficulty":       "MODERATE",
                    "confidence":       "LOW",
                }

            return json.dumps(parsed, sort_keys=True)

        result_str = gl.eq_principle.prompt_non_comparative(
            nondet,
            task="Re-analyze a problem using original description plus new context, producing an updated structured solution.",
            criteria=(
                "Must return valid JSON with all 7 keys: problem_summary, root_cause, "
                "primary_solution, alternatives, risks, difficulty, confidence. "
                "difficulty must be exactly EASY, MODERATE, or COMPLEX. "
                "confidence must be exactly HIGH, MEDIUM, or LOW. "
                "Wording need not match exactly - only structure and key fields matter."
            ),
        )

        result = json.loads(result_str)

        # Use str key for reanalysis_counts
        count_key = str(problem_id)
        if count_key in self.reanalysis_counts:
            count = int(self.reanalysis_counts[count_key])
        else:
            count = 0

        reanalysis_key = str(problem_id) + "_" + str(count)

        reanalysis = ReanalysisRecord(
            problem_id       = key,
            reanalysis_num   = u256(count),
            context_added    = additional_context,
            problem_summary  = result.get("problem_summary",  ""),
            root_cause       = result.get("root_cause",       ""),
            primary_solution = result.get("primary_solution", ""),
            alternatives     = result.get("alternatives",     ""),
            risks            = result.get("risks",            ""),
            difficulty       = result.get("difficulty",       "MODERATE"),
            confidence       = result.get("confidence",       "MEDIUM"),
        )

        self.reanalyses[reanalysis_key] = reanalysis
        self.reanalysis_counts[count_key] = u256(count + 1)

    # ── VIEWS ─────────────────────────────────────────────────────────

    @gl.public.view
    def get_problem(self, id: int) -> typing.Any:
        key = u256(id)
        if key not in self.problems:
            return None
        r = self.problems[key]
        return {
            "id":               int(r.id),
            "title":            r.title,
            "description":      r.description,
            "category":         r.category,
            "severity":         r.severity,
            "submitter":        r.submitter,
            "status":           r.status,
            "upvote_count":     int(r.upvote_count),
            "problem_summary":  r.problem_summary,
            "root_cause":       r.root_cause,
            "primary_solution": r.primary_solution,
            "alternatives":     r.alternatives,
            "risks":            r.risks,
            "difficulty":       r.difficulty,
            "confidence":       r.confidence,
        }

    @gl.public.view
    def get_all_problems(self) -> typing.Any:
        results = []
        count   = int(self.problem_count)
        for i in range(count):
            key = u256(i)
            if key in self.problems:
                r = self.problems[key]
                results.append({
                    "id":               int(r.id),
                    "title":            r.title,
                    "description":      r.description,
                    "category":         r.category,
                    "severity":         r.severity,
                    "submitter":        r.submitter,
                    "status":           r.status,
                    "upvote_count":     int(r.upvote_count),
                    "problem_summary":  r.problem_summary,
                    "root_cause":       r.root_cause,
                    "primary_solution": r.primary_solution,
                    "alternatives":     r.alternatives,
                    "risks":            r.risks,
                    "difficulty":       r.difficulty,
                    "confidence":       r.confidence,
                })
        return results

    @gl.public.view
    def get_problem_count(self) -> int:
        return int(self.problem_count)

    @gl.public.view
    def get_reanalysis(self, problem_id: int, reanalysis_num: int) -> typing.Any:
        rkey = str(problem_id) + "_" + str(reanalysis_num)
        if rkey not in self.reanalyses:
            return None
        r = self.reanalyses[rkey]
        return {
            "problem_id":       int(r.problem_id),
            "reanalysis_num":   int(r.reanalysis_num),
            "context_added":    r.context_added,
            "problem_summary":  r.problem_summary,
            "root_cause":       r.root_cause,
            "primary_solution": r.primary_solution,
            "alternatives":     r.alternatives,
            "risks":            r.risks,
            "difficulty":       r.difficulty,
            "confidence":       r.confidence,
        }

    @gl.public.view
    def get_reanalysis_count(self, problem_id: int) -> int:
        count_key = str(problem_id)
        if count_key not in self.reanalysis_counts:
            return 0
        return int(self.reanalysis_counts[count_key])
