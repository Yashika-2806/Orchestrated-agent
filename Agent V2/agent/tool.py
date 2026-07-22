from datetime import datetime
from . import mathematics
# import mathematics
def extract_top_technologies(technologies: dict, limit: int = 5) -> list:
    """Extracts the most frequently used technologies from the frequency map."""
    return list(technologies.keys())[:limit]

def extract_recent_repository_context(repositories: list, limit: int = 10) -> list:
    """Extracts the metadata of the most recently updated repositories for the LLM context."""
    sorted_repos = sorted(
        repositories, 
        key=lambda x: datetime.strptime(x.get('updated_at', '1970-01-01T00:00:00Z'), "%Y-%m-%dT%H:%M:%SZ"), 
        reverse=True
    )
    recent_context = []
    for repo in sorted_repos[:limit]:
        recent_context.append({
            "name": repo.get("name"),
            "description": repo.get("description") or "No description provided.",
            "primary_language": repo.get("primary_language") or "Unknown"
        })
    return recent_context

def extract_domain_via_llm(profile: dict, repositories: list, custom_prompt: str = None) -> str:
    """Uses LLM to extract the correct career domain based on GitHub profile and repositories."""
    import os
    import openai
    import json

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "General Software Engineering"

    # Compile a concise context of repositories for the LLM
    repos_summary = []
    for repo in repositories:
        repos_summary.append({
            "name": repo.get("name"),
            "description": repo.get("description") or "No description provided.",
            "primary_language": repo.get("primary_language") or "Unknown",
            "all_languages": repo.get("all_languages", [])
        })

    github_payload = {
        "bio": profile.get("bio", ""),
        "technologies": profile.get("technologies", {}),
        "repositories": repos_summary
    }

    # Default high-quality domain extraction prompt
    default_prompt = (
        "You are an expert career assessor. Analyze the student's GitHub profile and repositories "
        "to determine their primary technical domain. Do not default to 'Web Development' unless "
        "there is clear evidence of frontend/backend projects. Look closely at the languages, names, "
        "and descriptions of the repositories.\n\n"
        "Your task is to identify the single most appropriate domain from: "
        "['Web Development', 'AI/ML', 'DevOps', 'Data Engineering', 'Mobile', 'Web3', 'CyberSecurity', 'Systems', 'UI/UX', 'General Software Engineering'].\n\n"
        "Return ONLY a valid JSON object with the key 'domain'. Example:\n"
        "{\"domain\": \"AI/ML\"}"
    )

    system_prompt = custom_prompt if custom_prompt else default_prompt

    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(github_payload, indent=2)}
            ]
        )
        result = json.loads(response.choices[0].message.content)
        return result.get("domain", "General Software Engineering")
    except Exception:
        return "General Software Engineering"

def compile_payload_from_memory(data: dict, engine_config: dict = None) -> dict:
    """
    Ingests raw dictionary data to calculate scores and build context.
    Acts as the bridge between the UI constants and the Math engine.
    """
    profile = data.get('profile', {})
    repositories = data.get('repositories', [])
    username = profile.get('username', 'Unknown')

    # Establish Failsafe Defaults (In case engine_config fails to pass)
    if not engine_config:
        engine_config = {
            "persona": "Default (Balanced Assessor)",
            "weights": {"consistency": 0.20, "community": 0.30, "technology": 0.25, "management": 0.15, "advanced": 0.10},
            "constants": {
                "epsilon": 1.0, "alpha": 5.0, "beta": 3.0, "breadth_ceiling": 8.0,
                "gamma": 10.0, "adv_target": 3,
                "sweet_spot_low": 0.15, "sweet_spot_high": 0.85, "points_per_collab": 20.0,
                "partial_credit": 0.2, "star_bonus": 2.0, "fork_bonus": 5.0,
                "target_ratio": 0.75, "bio_bonus": 10.0, "name_bonus": 5.0
            }
        }

    weights = engine_config.get("weights", {})
    c = engine_config.get("constants", {})

    # Execute Mathematics with Dynamic Constants explicitly mapped
    con_data = mathematics.calculate_consistency_score(
        profile.get('monthly_contributions', {}), 
        epsilon=c.get("epsilon", 1.0)
    )
    
    com_data = mathematics.calculate_community_score(
        repositories, 
        sweet_spot_low=c.get("sweet_spot_low", 0.15), 
        sweet_spot_high=c.get("sweet_spot_high", 0.85), 
        points_per_collab=c.get("points_per_collab", 20.0),
        partial_credit=c.get("partial_credit", 0.2),
        star_bonus=c.get("star_bonus", 2.0),
        fork_bonus=c.get("fork_bonus", 5.0)
    )
    
    tech_data = mathematics.calculate_technology_score(
        profile.get('technologies', {}), 
        alpha=c.get("alpha", 5.0), 
        beta=c.get("beta", 3.0),
        breadth_ceiling=c.get("breadth_ceiling", 8.0)
    )
    
    adv_data = mathematics.calculate_advanced_score(
        profile.get('forked_repositories', []), 
        gamma=c.get("gamma", 10.0),
        adv_target=c.get("adv_target", 3)
    )
    
    man_data = mathematics.calculate_management_score(
        profile, 
        target_ratio=c.get("target_ratio", 0.75), 
        bio_bonus=c.get("bio_bonus", 10.0), 
        name_bonus=c.get("name_bonus", 5.0)
    )

    # Bundle calculated components and execute Final Score logic
    scores_payload = {
        "consistency": con_data,
        "community": com_data,
        "technology": tech_data,
        "advanced": adv_data,
        "management": man_data
    }

    final_score_data = mathematics.calculate_final_score(scores_payload, weights)

    # Execute Upgraded Mathematics: AST Code Complexity & Academic DSA Cross-Verification
    ast_data = mathematics.calculate_ast_complexity(repositories)
    academic_gpa = float(engine_config.get("academic_gpa", 8.5)) if engine_config else 8.5
    dsa_score = float(engine_config.get("dsa_score", 85.0)) if engine_config else 85.0
    dsa_data = mathematics.verify_academic_dsa_consistency(academic_gpa, dsa_score, repositories)

    # Extract Narrative Context
    top_tech = extract_top_technologies(profile.get('technologies', {}))
    recent_repos = extract_recent_repository_context(repositories)

    custom_prompt = None
    if engine_config:
        custom_prompt = engine_config.get("prompt") or engine_config.get("custom_prompt")
    if not custom_prompt and isinstance(data, dict):
        custom_prompt = data.get("prompt") or data.get("custom_prompt")

    extracted_domain = extract_domain_via_llm(profile, repositories, custom_prompt)

    # Build the structured Context Payload returned to the main UI
    return {
        "user_target": username,
        "bio": profile.get("bio", ""),
        "evaluation_persona": engine_config.get("persona", "Default"),
        "hard_metrics": {
            "final_score": final_score_data["score"],
            "category_scores": {
                "consistency": con_data["score"],
                "community": com_data["score"],
                "technology": tech_data["score"],
                "advanced": adv_data["score"],
                "management": man_data["score"]
            },
            "breakdowns": {
                "final": final_score_data["details"],
                "consistency": con_data["details"],
                "community": com_data["details"],
                "technology": tech_data["details"],
                "advanced": adv_data["details"],
                "management": man_data["details"]
            }
        },
        "narrative_context": {
            "top_technologies": top_tech,
            "recent_focus_areas": recent_repos,
            "ast_code_complexity": ast_data,
            "academic_dsa_verification": dsa_data,
            "extracted_domain": extracted_domain
        }
    }


def execute_github_agent(handle: str, custom_config: dict = None) -> dict:
    """
    Thread-safe entry point for the Orchestrator.
    """
    from . import scraper  # Relative import to your scraper.py
    
    try:
        raw_data = scraper.run_scraper(handle)
        
        if "error" in raw_data:
            return {
                "agent": "github",
                "status": "failed",
                "error_log": raw_data["error"],
                "final_score": 0
            }
            
        payload = compile_payload_from_memory(raw_data, engine_config=custom_config)
        
        return {
            "agent": "github",
            "status": "success",
            "final_score": payload["hard_metrics"]["final_score"],
            "sub_scores": payload["hard_metrics"]["category_scores"],
            "narrative_context": payload["narrative_context"]
        }
        
    except Exception as e:
        return {
            "agent": "github",
            "status": "failed",
            "error_log": str(e),
            "final_score": 0
        }