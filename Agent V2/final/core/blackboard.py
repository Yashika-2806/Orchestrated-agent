"""
[Shared Local Context Cache & Blackboard (I-A2A Bus)]

Provides an in-memory, thread-safe blackboard key-value cache and a
Strict Schema Contract for Inter-Agent Communication (I-A2A).

Agents publish findings directly to the Blackboard slots upon completion,
allowing other agents to execute sub-millisecond schema queries without
triggering slow LLM round-trips or token inflation.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict, field
import threading
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# --- STRICT SCHEMA CONTRACTS ---

@dataclass
class A2ASkillQuery:
    """
    Lightweight, strictly-typed JSON schema query for inter-agent skill validation.
    Example: {"query_type": "skill_validation", "skill": "React", "min_commits": 5}
    """
    query_type: str = "skill_validation"
    skill: str = ""
    target_agent: str = "github"  # 'github', 'cp', or 'all'
    min_commits: int = 1
    min_repos: int = 1

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class A2ASkillResponse:
    """
    Lightweight, strictly-typed response schema returned from Blackboard lookups.
    """
    skill: str
    status: str  # 'STRONGLY_VERIFIED', 'PARTIALLY_VERIFIED', 'UNVERIFIED_CLAIM'
    commit_weight: float = 0.0
    repo_count: int = 0
    cp_solved_count: int = 0
    proof_sources: List[str] = field(default_factory=list)
    details: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


# --- SHARED BLACKBOARD MEMORY STORE ---

class SharedBlackboard:
    """
    In-memory key-value blackboard cache for inter-agent findings and context.
    Enables zero-latency memory-based cross-agent lookups.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._slots = {
            "github": {},
            "resume": {},
            "cp": {},
            "metadata": {}
        }
        self._query_log: List[dict] = []

    def publish(self, slot_name: str, data: Dict[str, Any]) -> None:
        """
        Publishes structured findings from an agent into its dedicated blackboard slot.
        """
        with self._lock:
            if slot_name in self._slots:
                self._slots[slot_name] = data
                logging.info(f"[Blackboard] Slot '{slot_name}' updated with {len(data)} top-level fields.")

    def publish_github_findings(self, data: Dict[str, Any]) -> None:
        self.publish("github", data)

    def publish_resume_findings(self, data: Dict[str, Any]) -> None:
        self.publish("resume", data)

    def publish_cp_findings(self, data: Dict[str, Any]) -> None:
        self.publish("cp", data)

    def query_skill_validation(self, query_data: dict) -> dict:
        """
        Executes an instant sub-millisecond schema-validated skill query against the Blackboard cache.
        
        Args:
            query_data: Dict adhering to A2ASkillQuery schema (e.g. {"query_type": "skill_validation", "skill": "React"})
            
        Returns:
            Dict adhering to A2ASkillResponse schema.
        """
        query = A2ASkillQuery(
            query_type=query_data.get("query_type", "skill_validation"),
            skill=query_data.get("skill", ""),
            target_agent=query_data.get("target_agent", "all"),
            min_commits=query_data.get("min_commits", 1),
            min_repos=query_data.get("min_repos", 1)
        )

        skill_lower = query.skill.lower().strip()
        proof_sources = []
        repo_count = 0
        commit_weight = 0.0
        cp_solved = 0

        with self._lock:
            gh_data = self._slots.get("github", {})
            cp_data = self._slots.get("cp", {})

        # 1. Inspect GitHub Slot
        if gh_data.get("status") == "success":
            top_tech = gh_data.get("narrative_context", {}).get("top_technologies", [])
            recent_repos = gh_data.get("narrative_context", {}).get("recent_focus_areas", [])

            # Check top technologies
            for tech in top_tech:
                if skill_lower in tech.lower() or tech.lower() in skill_lower:
                    proof_sources.append("GitHub Technologies")
                    commit_weight += 50.0
                    repo_count += 1

            # Check recent repos
            for repo in recent_repos:
                lang = (repo.get("primary_language") or "").lower()
                name = (repo.get("name") or "").lower()
                desc = (repo.get("description") or "").lower()

                if skill_lower in lang or skill_lower in name or skill_lower in desc:
                    repo_count += 1
                    commit_weight += 20.0
                    if "GitHub Repositories" not in proof_sources:
                        proof_sources.append("GitHub Repositories")

        # 2. Inspect CP Slot
        if cp_data.get("status") == "success":
            sub_scores = cp_data.get("sub_scores", {})
            for platform, stats in sub_scores.items():
                if isinstance(stats, dict) and "solved_count" in stats:
                    cp_solved += stats.get("solved_count", 0)

            cp_keywords = ["problem solving", "dsa", "data structures", "algorithms", "cpp", "c++", "python", "java"]
            if any(kw in skill_lower for kw in cp_keywords) and cp_solved > 50:
                proof_sources.append(f"CP Platforms ({cp_solved} Solved)")

        # 3. Determine Verification Status
        if len(proof_sources) >= 2 or repo_count >= 2 or (commit_weight >= 50.0 and cp_solved >= 100):
            status = "STRONGLY_VERIFIED"
            details = f"Strong evidence found across {', '.join(proof_sources)}. Repo count: {repo_count}."
        elif len(proof_sources) >= 1 or repo_count >= 1:
            status = "PARTIALLY_VERIFIED"
            details = f"Partial evidence found in {', '.join(proof_sources)}. Repo count: {repo_count}."
        else:
            status = "UNVERIFIED_CLAIM"
            details = f"No code commits or contest activity found matching skill '{query.skill}'."

        response = A2ASkillResponse(
            skill=query.skill,
            status=status,
            commit_weight=round(commit_weight, 2),
            repo_count=repo_count,
            cp_solved_count=cp_solved,
            proof_sources=proof_sources,
            details=details
        )

        resp_dict = response.to_dict()

        with self._lock:
            self._query_log.append({
                "query": query.to_dict(),
                "response": resp_dict
            })

        return resp_dict

    def get_snapshot(self) -> Dict[str, Any]:
        """
        Returns a typed, complete snapshot of all published blackboard slots and query logs.
        """
        with self._lock:
            return {
                "slots": self._slots.copy(),
                "query_log": self._query_log.copy()
            }
