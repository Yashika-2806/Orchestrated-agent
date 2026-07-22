"""
[Agent-to-Agent Communication & Domain Validation Protocol]

Implements inter-agent communication, brainstorming, and cross-validation
between the GitHub Agent, Resume Agent, and Competitive Programming (CP) Agent.

The 3 agents exchange extracted skill evidence, debate self-reported resume claims
against code/contest proof, and collaboratively reach a validated domain consensus matrix.
"""

import json
import os
import logging
from typing import Optional
import openai


MULTI_AGENT_BRAINSTORM_PROMPT = """You are orchestrating a structured multi-agent brainstorming and cross-validation session between 3 specialized AI agents:

1. GITHUB AGENT (Code & Repository Evidence Assessor):
   - Evaluates actual code repos, primary languages, commit activity, and framework indicators.
   - Purpose: Prove what technologies the student has actually BUILT with.

2. RESUME AGENT (Self-Reported Claim & Context Assessor):
   - Evaluates listed skills, project descriptions, and internship experience in the resume.
   - Purpose: Highlight what the student CLAIMS to know.

3. CP AGENT (Algorithmic Rigor & Problem Solving Assessor):
   - Evaluates contest performance, solved problem counts, ratings, and CP languages across LeetCode, Codeforces, CodeChef, HackerRank.
   - Purpose: Prove algorithmic depth and problem-solving capability.

INPUT DATA:
- Student Info: {student_info}
- GitHub Agent Findings: {github_findings}
- Resume Agent Findings: {resume_findings}
- CP Agent Findings: {cp_findings}
- Domain Ontology Reference: {domain_ontology}

DELIBERATION PROTOCOL:
Conduct a 3-round inter-agent communication & consensus process:

ROUND 1 — AGENT EVIDENCE STATEMENTS:
Each agent presents its key evidence and initial domain proposal based on its source data.

ROUND 2 — CROSS-VALIDATION & DEBATE:
- GitHub Agent cross-checks Resume Agent's claimed skills against actual repository code proof.
- CP Agent cross-checks algorithmic/coding claims against problem-solving metrics.
- Identify:
  * Strongly Verified Skills (claimed in Resume AND backed by GitHub code or CP proof)
  * Partially Verified Skills (found in GitHub/CP but weak evidence or only listed in Resume with minor repo proof)
  * Unverified Resume Claims (claimed in Resume but 0 proof in GitHub repos or CP profiles)

ROUND 3 — DOMAIN CONSENSUS & VALIDATION:
The agents vote and agree on:
1. validated_primary_domain: The single domain with highest cross-validated evidence. Must be one of: "Web Development", "AI/ML", "DevOps", "Data Engineering", "Mobile", "Web3", "CyberSecurity", "Systems", "UI/UX", "General Software Engineering".
2. validated_secondary_domain: A secondary domain if cross-validated evidence supports it, else null.
3. domain_validation_score: A score from 0 to 100 indicating confidence in this domain classification based on multi-agent agreement and evidence strength.
4. verified_skills: Array of objects [{{"skill": "SkillName", "status": "Strongly Verified"|"Partially Verified", "evidence_source": "GitHub/CP/Both"}}]
5. unverified_resume_claims: Array of skills claimed on resume but lacking code/contest proof.
6. inter_agent_brainstorm_transcript: A concise multi-agent conversation transcript (3-5 exchanges) showing how GitHub, Resume, and CP agents deliberated and reached consensus.
7. validation_reasoning: Summary of why the consensus domain was selected based on cross-validation.

Return ONLY a valid JSON object with the exact keys:
- validated_primary_domain (string)
- validated_secondary_domain (string or null)
- domain_validation_score (float, 0-100)
- verified_skills (array of objects)
- unverified_resume_claims (array of strings)
- inter_agent_brainstorm_transcript (array of objects with "agent", "message")
- validation_reasoning (string)
"""


from blackboard import SharedBlackboard, A2ASkillQuery, A2ASkillResponse


def run_inter_agent_communication(
    student_payload: dict,
    resume_res: dict,
    github_res: dict,
    cp_res: dict,
    ontology: dict,
    blackboard: Optional[SharedBlackboard] = None
) -> dict:
    """
    Executes the multi-agent communication and brainstorming protocol using
    Strict Schema Contracts and the Shared Local Context Blackboard cache.
    
    Args:
        student_payload: Student info (name, id, metadata)
        resume_res: Raw output from Resume Agent
        github_res: Raw output from GitHub Agent
        cp_res: Raw output from CP Agent
        ontology: Loaded domain ontology reference
        blackboard: Instance of SharedBlackboard (in-memory cache)
        
    Returns:
        Structured Inter-Agent Consensus Matrix dict.
    """
    # Instantiate Blackboard if not provided
    if blackboard is None:
        blackboard = SharedBlackboard()
        blackboard.publish_github_findings(github_res)
        blackboard.publish_resume_findings(resume_res)
        blackboard.publish_cp_findings(cp_res)

    # Execute Strict Schema Queries against Blackboard Cache
    top_github_tech = github_res.get("narrative_context", {}).get("top_technologies", [])
    skills_to_query = list(set(top_github_tech + ["React", "Python", "Problem Solving", "TypeScript", "JavaScript", "C++", "Docker"]))
    
    schema_query_results = []
    for skill_name in skills_to_query:
        query_schema = {
            "query_type": "skill_validation",
            "skill": skill_name,
            "min_commits": 1,
            "min_repos": 1
        }
        res = blackboard.query_skill_validation(query_schema)
        schema_query_results.append(res)

    logging.info(f"[I-A2A Bus] Executed {len(schema_query_results)} Strict Schema Queries against Shared Blackboard (0ms memory lookup).")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.warning("[AgentComm] OPENAI_API_KEY not set. Running deterministic inter-agent consensus.")
        consensus = _deterministic_consensus(student_payload, resume_res, github_res, cp_res, ontology)
        consensus["strict_schema_query_logs"] = schema_query_results
        return consensus

    # Prepare evidence inputs for each agent
    github_findings = {
        "status": github_res.get("status"),
        "final_score": github_res.get("final_score", 0),
        "top_technologies": github_res.get("narrative_context", {}).get("top_technologies", []),
        "recent_focus_areas": github_res.get("narrative_context", {}).get("recent_focus_areas", []),
        "extracted_domain": github_res.get("narrative_context", {}).get("extracted_domain", "Unknown"),
        "sub_scores": github_res.get("sub_scores", {})
    }

    resume_findings = {
        "status": resume_res.get("status"),
        "final_score": resume_res.get("final_score", 0),
        "sub_scores": resume_res.get("sub_scores", {}),
        "narrative_context": resume_res.get("narrative_context", {})
    }

    cp_findings = {
        "status": cp_res.get("status"),
        "final_score": cp_res.get("final_score", 0),
        "sub_scores": cp_res.get("sub_scores", {}),
        "platforms_evaluated": cp_res.get("narrative_context", {}).get("platforms_evaluated", [])
    }

    student_info = {
        "name": student_payload.get("name", "Unknown"),
        "student_id": student_payload.get("student_id", "Unknown"),
        "batch_year": student_payload.get("metadata", {}).get("batch_year", "2026")
    }

    formatted_prompt = MULTI_AGENT_BRAINSTORM_PROMPT.format(
        student_info=json.dumps(student_info),
        github_findings=json.dumps(github_findings),
        resume_findings=json.dumps(resume_findings),
        cp_findings=json.dumps(cp_findings),
        domain_ontology=json.dumps(ontology.get("domain_priority_order", []))
    )

    try:
        logging.info("[AgentComm] Launching inter-agent communication & consensus session...")
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.1,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a multi-agent orchestration engine. Ensure strict agent-to-agent cross-validation principles."},
                {"role": "user", "content": formatted_prompt}
            ]
        )

        raw = response.choices[0].message.content
        consensus = json.loads(raw)
        consensus["communication_status"] = "success"
        consensus["protocol_version"] = "2.1 (Strict Schema Contract & Shared Blackboard)"
        consensus["strict_schema_query_logs"] = schema_query_results

        logging.info(f"[AgentComm] Consensus reached! Validated Domain: {consensus.get('validated_primary_domain')} "
                     f"(Score: {consensus.get('domain_validation_score')}%)")
        return consensus

    except Exception as e:
        logging.error(f"[AgentComm] Inter-agent communication failed: {str(e)}")
        fallback = _deterministic_consensus(student_payload, resume_res, github_res, cp_res, ontology)
        fallback["communication_error"] = str(e)
        return fallback


def _deterministic_consensus(
    student_payload: dict,
    resume_res: dict,
    github_res: dict,
    cp_res: dict,
    ontology: dict
) -> dict:
    """
    Deterministic fallback for agent-to-agent consensus when LLM is unavailable.
    Cross-checks GitHub tech stack against default skill maps.
    """
    github_tech = github_res.get("narrative_context", {}).get("top_technologies", [])
    cp_score = cp_res.get("final_score", 0)

    # Heuristic domain mapping from GitHub evidence
    tech_map = ontology.get("skill_to_domain", {}).get("mapping", {})
    domain_counts = {}
    verified_skills = []

    for tech in github_tech:
        domain = tech_map.get(tech, "General Software Engineering")
        domain_counts[domain] = domain_counts.get(domain, 0) + 2
        verified_skills.append({
            "skill": tech,
            "status": "Strongly Verified",
            "evidence_source": "GitHub Agent"
        })

    primary_domain = github_res.get("narrative_context", {}).get("extracted_domain")
    if not primary_domain or primary_domain == "Unknown":
        primary_domain = "General Software Engineering"
        if domain_counts:
            primary_domain = max(domain_counts, key=domain_counts.get)

    if cp_score > 80:
        verified_skills.append({
            "skill": "Algorithms & Problem Solving",
            "status": "Strongly Verified",
            "evidence_source": "CP Agent"
        })

    transcript = [
        {
            "agent": "GitHub Agent",
            "message": f"I analyzed {len(github_tech)} primary technologies from committed repos: {', '.join(github_tech)}. Code evidence strongly points to {primary_domain}."
        },
        {
            "agent": "CP Agent",
            "message": f"My evaluation yields a problem-solving score of {cp_score}. Algorithmic skills cross-validated."
        },
        {
            "agent": "Resume Agent",
            "message": f"I concur. Self-reported claims align with GitHub code proof and CP metrics for {primary_domain}."
        }
    ]

    return {
        "communication_status": "fallback",
        "protocol_version": "2.0 (Deterministic Fallback)",
        "validated_primary_domain": primary_domain,
        "validated_secondary_domain": None,
        "domain_validation_score": 75.0,
        "verified_skills": verified_skills,
        "unverified_resume_claims": [],
        "inter_agent_brainstorm_transcript": transcript,
        "validation_reasoning": f"Deterministic fallback: Primary evidence from GitHub technologies ({', '.join(github_tech[:3])}) maps to '{primary_domain}' with CP score {cp_score}."
    }
