"""
[2.6] LLM Career Semantic Synthesizer & Profile Builder

Synthesizes raw outputs from all 3 evaluation agents (Resume, GitHub, CP)
into a cohesive Semantic Career Profile using GPT-4o. This profile captures
career intent, primary domain, strengths, gaps, and experience context
to feed into the Forecasting Agent [4.1].
"""

import json
import os
import logging
import openai


SYNTHESIS_SYSTEM_PROMPT = """You are an expert career analyst for B.Tech Computer Science students.
You will receive evaluation data from three agents: a Resume Agent, a GitHub Agent, and a Competitive Programming Agent.

Your task is to synthesize all evidence into a single cohesive career profile.
Return ONLY a valid JSON object with these exact keys:

- career_intent (string): A 1-2 sentence summary of the student's likely career direction based on all evidence.
- primary_domain (string): The single most likely career domain. Must be one of: "Web Development", "AI/ML", "DevOps", "Data Engineering", "Mobile", "Web3", "CyberSecurity", "Systems", "UI/UX", "General Software Engineering".
- secondary_domain (string or null): A second domain if the student shows strong evidence in two areas.
- top_skills (array of strings): The 5-8 most prominent technical skills observed across all agents.
- experience_summary (string): A 2-3 sentence summary of the student's practical experience (internships, projects, open-source contributions).
- strengths (array of strings): 3-5 key strengths identified from the combined evidence.
- gaps (array of strings): 2-4 areas where the student shows weakness or missing evidence.
- coding_aptitude_level (string): One of "Beginner", "Intermediate", "Advanced", "Expert" based on CP and GitHub combined signals.
- project_maturity_level (string): One of "Academic", "Semi-Professional", "Professional", "Production-Grade" based on resume and GitHub project evidence.
"""


def synthesize_profile(
    student_payload: dict,
    resume_res: dict,
    github_res: dict,
    cp_res: dict,
    ontology: dict,
    inter_agent_consensus: dict = None
) -> dict:
    """
    Calls GPT-4o to synthesize all agent outputs into a semantic career profile.
    
    Args:
        student_payload: The student metadata (name, id, batch_year, etc.)
        resume_res: Raw output from the Resume Agent
        github_res: Raw output from the GitHub Agent
        cp_res: Raw output from the CP Agent
        ontology: The loaded domain_ontology.json for context
        
    Returns:
        A dict containing the semantic career profile, or a fallback on failure.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.warning("[2.6] OPENAI_API_KEY not set. Returning fallback semantic profile.")
        return _build_fallback_profile(resume_res, github_res, cp_res)

    # Build the evidence payload for the LLM
    evidence = {
        "student_info": {
            "name": student_payload.get("name", "Unknown"),
            "student_id": student_payload.get("student_id", "Unknown"),
            "batch_year": student_payload.get("metadata", {}).get("batch_year", "Unknown"),
            "branch": student_payload.get("metadata", {}).get("branch", "Computer Science")
        },
        "resume_agent": {
            "status": resume_res.get("status", "failed"),
            "final_score": resume_res.get("final_score", 0),
            "sub_scores": resume_res.get("sub_scores", {}),
            "narrative_context": resume_res.get("narrative_context", {})
        },
        "github_agent": {
            "status": github_res.get("status", "failed"),
            "final_score": github_res.get("final_score", 0),
            "sub_scores": github_res.get("sub_scores", {}),
            "narrative_context": github_res.get("narrative_context", {})
        },
        "cp_agent": {
            "status": cp_res.get("status", "failed"),
            "final_score": cp_res.get("final_score", 0),
            "sub_scores": cp_res.get("sub_scores", {}),
            "narrative_context": cp_res.get("narrative_context", {})
        },
        "inter_agent_consensus": inter_agent_consensus or {},
        "available_domains": ontology.get("domain_priority_order", [])
    }

    user_prompt = f"""Analyze the following student evaluation data and synthesize a career profile.

{json.dumps(evidence, indent=2)}

Return ONLY a valid JSON object. No markdown, no explanation."""

    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.1,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYNTHESIS_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )

        raw = response.choices[0].message.content
        profile = json.loads(raw)
        profile["synthesis_status"] = "success"
        logging.info(f"[2.6] Semantic profile synthesized: domain={profile.get('primary_domain')}")
        return profile

    except Exception as e:
        logging.error(f"[2.6] Career Synthesizer failed: {str(e)}")
        fallback = _build_fallback_profile(resume_res, github_res, cp_res)
        fallback["synthesis_error"] = str(e)
        return fallback


def _build_fallback_profile(resume_res: dict, github_res: dict, cp_res: dict) -> dict:
    """
    Builds a deterministic fallback profile when the LLM is unavailable.
    Uses GitHub narrative context (top technologies) to infer domain.
    """
    top_tech = []
    if github_res.get("status") == "success":
        top_tech = github_res.get("narrative_context", {}).get("top_technologies", [])

    # Simple heuristic: map first recognized tech to a domain
    tech_to_domain = {
        "Python": "AI/ML", "JavaScript": "Web Development", "TypeScript": "Web Development",
        "Java": "General Software Engineering", "C++": "Systems", "C": "Systems",
        "Go": "Systems", "Rust": "Systems", "Kotlin": "Mobile", "Swift": "Mobile",
        "HTML": "Web Development", "CSS": "Web Development", "React": "Web Development",
        "Docker": "DevOps", "Solidity": "Web3"
    }
    
    primary_domain = "General Software Engineering"
    if github_res.get("status") == "success" and "extracted_domain" in github_res.get("narrative_context", {}):
        primary_domain = github_res["narrative_context"]["extracted_domain"]
    else:
        for tech in top_tech:
            if tech in tech_to_domain:
                primary_domain = tech_to_domain[tech]
                break

    # Determine coding aptitude from CP score
    cp_score = cp_res.get("final_score", 0)
    if cp_score >= 80:
        aptitude = "Expert"
    elif cp_score >= 60:
        aptitude = "Advanced"
    elif cp_score >= 35:
        aptitude = "Intermediate"
    else:
        aptitude = "Beginner"

    return {
        "synthesis_status": "fallback",
        "career_intent": "Could not synthesize career intent (LLM unavailable).",
        "primary_domain": primary_domain,
        "secondary_domain": None,
        "top_skills": top_tech[:6],
        "experience_summary": "Fallback profile — detailed synthesis unavailable.",
        "strengths": [],
        "gaps": [],
        "coding_aptitude_level": aptitude,
        "project_maturity_level": "Academic"
    }
