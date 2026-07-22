"""
[4.1] Master Career Synthesis & Forecasting Agent (LLM-Driven)

JSON-Enforced Prompt Mechanism that takes:
- Semantic Career Profile from [2.6]
- Raw agent scores (resume, github, cp)
- Historical Benchmarks [1.5]
- Domain Ontology [1.6]

And produces:
- Placement Probability Inference
- Salary Band Synthesis
- Domain/Role Classification
- Backtesting validation against historical data [4.4]
"""

import json
import os
import logging
import openai


FORECASTING_SYSTEM_PROMPT = """You are a career forecasting AI for B.Tech Computer Science graduates.

You are equipped with 3 advanced agentic tools:
1. Employability Index State Machine (Part A): Strictly gates candidate placement readiness across Core Tech Competence, Communication, and Market Readiness pillars.
2. Vector/Semantic Anchoring (Part B): Programmatically grounds domain classification and role recommendations into strict Industry Domain Ontology enums.
3. Mini-RAG Local Market Anchors (Part C): RAG retrieval over historical institution placement data for exact LPA salary package baselines.

Your job is to produce a grounded, highly accurate career forecast. Return ONLY a valid JSON object with these exact keys:

- predicted_domain (string): The primary career domain. Must match one of the domains in the ontology.
- domain_confidence (float): 0.0 to 1.0 confidence in the domain prediction.
- recommended_roles (array of strings): Top 3 suitable job roles from the strict ontology enum list.
- placement_probability (float): 0 to 100. The estimated probability (%) that this student will be placed. Ground this strictly against the State Machine gating.
- expected_salary_band (object): {"min_lpa": float, "max_lpa": float, "label": string} — expected salary band in INR LPA. GROUND THIS STRICTLY WITHIN THE MINI-RAG BASELINE WINDOW PROVIDED.
- career_readiness (string): One of "High Risk / Not Placed", "Needs Development", "Market Ready", "Highly Competitive".
- key_differentiators (array of strings): 2-3 factors that make this student stand out.
- improvement_areas (array of strings): 2-3 actionable recommendations.
- reasoning (string): A 3-5 sentence explanation referencing the State Machine pillars, semantic domain anchoring, and Mini-RAG salary window.
- salary_reasoning (string): A detailed 2-3 sentence explanation justifying the predicted salary window based on the candidate's master score, domain, and historical local market anchors.
- risk_factors (array of strings): 1-3 risks that could lower placement chances.
"""


def calculate_employability_state_machine(
    resume_score: float,
    github_score: float,
    cp_score: float,
    master_score: float = 0.0
) -> dict:
    """
    [Part A: Employability Index State Machine]
    Calculates explicit employability index across 3 pillars:
    - Pillar 1: Core Tech Competence (CP 60% + GitHub 40%)
    - Pillar 2: Communication & Presentation (Resume hygiene/clarity score)
    - Pillar 3: Market Readiness (GitHub management & production realization)

    Hard Threshold Gating:
    Uses master_score to determine placement probability tiers, 
    so students with high CPI and DSA marks aren't penalized by outdated rules.
    """
    p1_tech = (0.60 * cp_score) + (0.40 * github_score)
    p2_comm = resume_score if resume_score > 0 else 45.0  # Fallback baseline for missing resume
    p3_readiness = (0.50 * github_score) + (0.50 * resume_score) if resume_score > 0 else (0.75 * github_score)

    employability_index = round((0.45 * p1_tech) + (0.25 * p2_comm) + (0.30 * p3_readiness), 2)

    master_val = master_score if master_score > 0 else employability_index

    if master_val < 40.0:
        state = "HIGH_RISK_NOT_PLACED"
        max_allowed_probability = 25.0
        gating_reason = f"Master score ({round(master_val, 1)}) indicates high risk."
    elif master_val >= 80.0:
        state = "PLACED_HIGH_TIER"
        max_allowed_probability = 99.0
        gating_reason = "Master score exceeds high-tier employability thresholds."
    elif master_val >= 60.0:
        state = "PLACED_MARKET_READY"
        max_allowed_probability = 85.0
        gating_reason = "Master score passes market-readiness thresholds."
    else:
        state = "NEEDS_DEVELOPMENT"
        max_allowed_probability = 50.0
        gating_reason = "Master score passes minimum thresholds but requires core skill development."

    return {
        "employability_index": employability_index,
        "state": state,
        "pillar_scores": {
            "pillar1_tech_competence": round(p1_tech, 2),
            "pillar2_communication": round(p2_comm, 2),
            "pillar3_market_readiness": round(p3_readiness, 2)
        },
        "max_allowed_placement_probability": max_allowed_probability,
        "gating_reason": gating_reason
    }


def anchor_semantic_domain(
    semantic_profile: dict,
    inter_agent_consensus: dict,
    ontology: dict
) -> dict:
    """
    [Part B: Vector/Semantic Anchoring Engine]
    Programmatically calculates semantic intersections between verified skills/technologies
    and domain profiles from domain_ontology.json.
    Anchors domain classification & enforces strict enum roles.
    """
    primary = inter_agent_consensus.get("validated_primary_domain") or semantic_profile.get("primary_domain", "Web Development")
    verified_skills = [s.get("skill", "").lower() for s in inter_agent_consensus.get("verified_skills", []) if isinstance(s, dict)]
    top_skills = [s.lower() for s in semantic_profile.get("top_skills", [])]
    all_candidate_skills = list(set(verified_skills + top_skills))

    domain_mapping = ontology.get("skill_to_domain", {}).get("mapping", {})
    intersection_counts = {}

    for skill in all_candidate_skills:
        for mapped_skill, dom in domain_mapping.items():
            if skill in mapped_skill.lower() or mapped_skill.lower() in skill:
                intersection_counts[dom] = intersection_counts.get(dom, 0) + 1

    anchored_domain = primary
    if intersection_counts:
        top_anchored = max(intersection_counts, key=intersection_counts.get)
        if intersection_counts[top_anchored] >= 2:
            anchored_domain = top_anchored

    roles_map = ontology.get("domain_to_roles", {}).get("mapping", {})
    anchored_roles = roles_map.get(anchored_domain, ["Software Development Engineer (SDE)"])[:3]

    return {
        "anchored_primary_domain": anchored_domain,
        "anchored_roles": anchored_roles,
        "semantic_intersection_counts": intersection_counts
    }


def mini_rag_salary_lookup(
    master_score: float,
    anchored_domain: str,
    benchmarks: dict
) -> dict:
    """
    [Part C: Mini-RAG Local Market Anchors]
    Queries benchmarks.json for historical placement salary baselines matching
    the semantic domain anchor. Returns exact bounds to constrain the LLM.
    """
    domain_data = benchmarks.get(anchored_domain, benchmarks.get("Software Development", {}))
    bands = domain_data.get("salary_bands", {})
    
    if master_score >= 80:
        band = bands.get("premium", {"min": 14.0, "max": 25.0, "examples": []})
        tier = "Premium"
    elif master_score >= 60:
        band = bands.get("high", {"min": 8.0, "max": 14.0, "examples": []})
        tier = "High"
    elif master_score >= 40:
        band = bands.get("mid", {"min": 5.0, "max": 8.0, "examples": []})
        tier = "Mid"
    else:
        band = bands.get("entry", {"min": 3.0, "max": 5.0, "examples": []})
        tier = "Entry"

    return {
        "domain": anchored_domain,
        "tier": tier,
        "min_lpa": band.get("min", 3.0),
        "max_lpa": band.get("max", 5.0),
        "prompt_injection": f"MARKET BASELINE INJECTION: For domain '{anchored_domain}', a student with master score {master_score} falls into the '{tier}' tier. Your forecasted expected_salary_band MUST strictly bound between {band.get('min')} LPA and {band.get('max')} LPA."
    }


from pydantic import BaseModel, Field, ValidationError, validator
from typing import List


# --- PYDANTIC EXIT-POINT GUARDRAILS (ANTI-HALLUCINATION CONTRACT) ---

class SalaryBandGuardrail(BaseModel):
    min_lpa: float = Field(..., ge=1.0, le=50.0)
    max_lpa: float = Field(..., ge=1.0, le=50.0)

    @validator('max_lpa')
    def check_range(cls, v, values):
        if 'min_lpa' in values and v < values['min_lpa']:
            raise ValueError('max_lpa must be greater than or equal to min_lpa')
        return v


class ForecastOutputGuardrail(BaseModel):
    predicted_domain: str
    recommended_roles: List[str] = Field(default_factory=list)
    placement_probability: float = Field(..., ge=0.0, le=100.0)
    expected_salary_band: SalaryBandGuardrail
    career_readiness: str
    key_differentiators: List[str] = Field(default_factory=list)
    improvement_areas: List[str] = Field(default_factory=list)
    reasoning: str
    salary_reasoning: str = Field(default="Salary reasoning not provided.")
    risk_factors: List[str] = Field(default_factory=list)


def validate_forecast_guardrail(raw_json_dict: dict) -> dict:
    """
    [Pydantic Exit-Point Guardrail Layer — Anti-Hallucination]
    Enforces strict Pydantic model validation on block [4.1] outputs.
    Rejects text formatted values (e.g. 'around 6-7 Lakhs') and forces numerical floats.
    """
    validated = ForecastOutputGuardrail(**raw_json_dict)
    return validated.model_dump()


def execute_forecast(
    semantic_profile: dict,
    resume_score: float,
    github_score: float,
    cp_score: float,
    master_score: float,
    benchmarks: dict,
    ontology: dict,
    inter_agent_consensus: dict = None
) -> dict:
    """
    Executes the LLM-driven forecasting pipeline with State Machine gating,
    Semantic Domain Anchoring, Mini-RAG Local Market Salary Lookup,
    and Pydantic Exit-Point Guardrail Auto-Retries.
    """
    consensus_data = inter_agent_consensus or {}

    # 1. Execute State Machine Gating (Part A)
    state_machine = calculate_employability_state_machine(resume_score, github_score, cp_score, master_score)

    # 2. Execute Vector/Semantic Anchoring Engine (Part B)
    semantic_anchor = anchor_semantic_domain(semantic_profile, consensus_data, ontology)
    anchored_domain = semantic_anchor["anchored_primary_domain"]

    # 3. Execute Mini-RAG Local Market Lookup (Part C)
    rag_salary = mini_rag_salary_lookup(master_score, anchored_domain, benchmarks)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.warning("[4.1] OPENAI_API_KEY not set. Running deterministic fallback forecast.")
        return _deterministic_forecast(
            semantic_profile, resume_score, github_score, cp_score,
            master_score, benchmarks, ontology
        )

    # Build the grounded forecasting evidence payload
    forecast_input = {
        "semantic_profile": semantic_profile,
        "inter_agent_consensus": consensus_data,
        "employability_state_machine": state_machine,
        "semantic_domain_anchor": semantic_anchor,
        "mini_rag_market_baseline": rag_salary,
        "agent_scores": {
            "resume_score": resume_score,
            "github_score": github_score,
            "cp_score": cp_score,
            "master_score": master_score
        }
    }

    user_prompt = f"""Based on the following student evaluation data, produce a grounded career forecast.

{json.dumps(forecast_input, indent=2)}

{rag_salary['prompt_injection']}

STATE MACHINE GATING MANDATE: State is '{state_machine['state']}'. Max placement probability allowed is {state_machine['max_allowed_placement_probability']}%.

Return ONLY a valid JSON object. No markdown, no explanation."""

    client = openai.OpenAI(api_key=api_key)
    max_retries = 3
    retry_count = 0
    correction_hint = ""

    while retry_count < max_retries:
        try:
            current_prompt = user_prompt + (f"\n\nPREVIOUS ERROR CORRECTION: {correction_hint}" if correction_hint else "")
            response = client.chat.completions.create(
                model="gpt-4o",
                temperature=0.10,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": FORECASTING_SYSTEM_PROMPT},
                    {"role": "user", "content": current_prompt}
                ]
            )

            raw = response.choices[0].message.content
            raw_dict = json.loads(raw)

            # [Guardrail Validation Layer] Pass through Pydantic exit-point validator
            validated_dict = validate_forecast_guardrail(raw_dict)
            
            forecast = validated_dict
            forecast["forecast_status"] = "success"
            forecast["forecast_method"] = "LLM-Driven (GPT-4o + State Machine + Mini-RAG + Pydantic Guardrail)"
            forecast["employability_state_machine"] = state_machine
            forecast["semantic_domain_anchor"] = semantic_anchor
            forecast["mini_rag_market_baseline"] = rag_salary

            # Enforce State Machine Gating Clamp
            if state_machine["state"] == "HIGH_RISK_NOT_PLACED":
                forecast["placement_probability"] = min(forecast.get("placement_probability", 20.0), 25.0)
                forecast["career_readiness"] = "High Risk / Not Placed"

            # [4.4] Placement Backtesting & Validation Loop
            backtest = _run_backtesting(master_score, forecast, benchmarks)
            forecast["backtesting_validation"] = backtest

            logging.info(f"[4.1 Guardrail Passed] Forecast complete: domain={forecast.get('predicted_domain')}, "
                         f"state={state_machine['state']}, "
                         f"placement={forecast.get('placement_probability')}%, "
                         f"salary=INR {forecast.get('expected_salary_band', {}).get('min_lpa')}-{forecast.get('expected_salary_band', {}).get('max_lpa')} LPA")
            return forecast

        except (ValidationError, json.JSONDecodeError, KeyError) as ve:
            retry_count += 1
            correction_hint = f"Your previous output failed Pydantic validation: {str(ve)}. Ensure expected_salary_band min_lpa and max_lpa are strict floats (e.g. 6.5, not '6-7 LPA')."
            logging.warning(f"[4.1 Guardrail REJECTED] Attempt {retry_count}/{max_retries} failed validation: {ve}. Retrying...")

    # Fallback if retries exhausted
    logging.error(f"[4.1 Guardrail Exhausted] All {max_retries} validation attempts failed. Falling back to deterministic engine.")
    return _deterministic_forecast(
        semantic_profile, resume_score, github_score, cp_score,
        master_score, benchmarks, ontology
    )


def _deterministic_forecast(
    semantic_profile: dict,
    resume_score: float,
    github_score: float,
    cp_score: float,
    master_score: float,
    benchmarks: dict,
    ontology: dict
) -> dict:
    """
    Deterministic fallback forecasting when LLM is unavailable.
    Uses benchmark lookup tables and ontology for predictions.
    """
    # 1. Placement Probability from benchmark curve
    placement_pct = 10  # default
    placement_label = "Critical Gap"
    for tier in benchmarks.get("placement_probability_curve", {}).get("tiers", []):
        if tier["score_min"] <= master_score < tier["score_max"]:
            placement_pct = tier["placement_pct"]
            placement_label = tier["label"]
            break
    # Handle score == 100
    if master_score >= 100:
        placement_pct = 99
        placement_label = "Exceptional"

    # 2. Domain from semantic profile
    predicted_domain = semantic_profile.get("primary_domain", "General Software Engineering")

    # 3. Salary band from benchmarks
    domain_bands = benchmarks.get("salary_bands", {}).get("bands", {}).get(
        predicted_domain,
        benchmarks.get("salary_bands", {}).get("bands", {}).get("General Software Engineering", {})
    )
    
    if master_score < 40:
        salary_band = domain_bands.get("below_40", {"min_lpa": 3.0, "max_lpa": 5.0, "label": "Entry Level"})
    elif master_score < 60:
        salary_band = domain_bands.get("40_to_60", {"min_lpa": 5.0, "max_lpa": 8.0, "label": "Mid Tier"})
    elif master_score < 80:
        salary_band = domain_bands.get("60_to_80", {"min_lpa": 8.0, "max_lpa": 14.0, "label": "High Tier"})
    else:
        salary_band = domain_bands.get("above_80", {"min_lpa": 14.0, "max_lpa": 25.0, "label": "Premium Tier"})

    # 4. Roles from ontology
    roles = ontology.get("domain_to_roles", {}).get("mapping", {}).get(
        predicted_domain,
        ["Software Development Engineer (SDE)"]
    )[:3]

    # 5. Career readiness
    if master_score >= 80:
        readiness = "Highly Competitive"
    elif master_score >= 60:
        readiness = "Market Ready"
    elif master_score >= 40:
        readiness = "Needs Development"
    else:
        readiness = "Not Ready"

    forecast = {
        "forecast_status": "fallback",
        "forecast_method": "Deterministic (Benchmark Lookup)",
        "predicted_domain": predicted_domain,
        "domain_confidence": 0.6,
        "recommended_roles": roles,
        "placement_probability": placement_pct,
        "expected_salary_band": salary_band,
        "career_readiness": readiness,
        "key_differentiators": [],
        "improvement_areas": [],
        "reasoning": f"Deterministic forecast: master_score={master_score} maps to '{placement_label}' tier with {placement_pct}% placement probability. Domain '{predicted_domain}' yields '{salary_band.get('label')}' salary band.",
        "salary_reasoning": f"Based on the Master Score of {master_score}, the candidate is placed in the '{salary_band.get('label')}' tier for the '{predicted_domain}' domain. Historically, this corresponds to an expected package of {salary_band.get('min_lpa')} - {salary_band.get('max_lpa')} LPA.",
        "risk_factors": []
    }

    # [4.4] Backtesting
    backtest = _run_backtesting(master_score, forecast, benchmarks)
    forecast["backtesting_validation"] = backtest

    return forecast


def _run_backtesting(master_score: float, forecast: dict, benchmarks: dict) -> dict:
    """
    [4.4] Placement Backtesting & Validation Loop
    
    Compares the predicted placement probability against historical
    observed rates from previous batches to flag deviations.
    """
    predicted_pct = forecast.get("placement_probability", 0)
    
    backtesting_samples = benchmarks.get("backtesting_reference", {}).get("samples", [])
    
    matched_sample = None
    for sample in backtesting_samples:
        score_range = sample["score_range"]
        parts = score_range.split("-")
        low, high = float(parts[0]), float(parts[1])
        if low <= master_score < high:
            matched_sample = sample
            break
    # Handle edge case for score == 100
    if matched_sample is None and master_score >= 85:
        matched_sample = backtesting_samples[-1] if backtesting_samples else None

    if matched_sample is None:
        return {
            "status": "no_reference_data",
            "message": "No historical backtesting data available for this score range."
        }

    observed_rate = matched_sample["observed_rate"]
    deviation = abs(predicted_pct - observed_rate)
    
    if deviation <= 10:
        alignment = "Strong Alignment"
    elif deviation <= 20:
        alignment = "Moderate Alignment"
    else:
        alignment = "Weak Alignment — Review Required"

    return {
        "status": "validated",
        "score_range": matched_sample["score_range"],
        "historical_sample_size": matched_sample["total_students"],
        "historical_placed": matched_sample["placed"],
        "historical_observed_rate": observed_rate,
        "predicted_probability": predicted_pct,
        "deviation_pct": round(deviation, 2),
        "alignment": alignment
    }
