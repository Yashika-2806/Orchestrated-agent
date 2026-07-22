import json
import os
import logging
import openai

FORECASTING_SYSTEM_PROMPT = """You are a career forecasting AI for B.Tech Computer Science graduates.

You will receive:
1. A semantic career profile (synthesized from resume, GitHub, and competitive programming evaluations)
2. Agent scores (resume_score, github_score, cp_score, master_score)
3. Historical placement benchmarks
4. Domain ontology with role mappings

Your job is to produce a comprehensive career forecast. Return ONLY a valid JSON object with these exact keys:

- predicted_domain (string): The primary career domain. Must match one of the domains in the ontology.
- domain_confidence (float): 0.0 to 1.0 confidence in the domain prediction.
- recommended_roles (array of strings): Top 3 suitable job roles for this student from the ontology.
- placement_probability (float): 0 to 100. The estimated probability (%) that this student will be placed in a campus recruitment drive. Base this on their master score, profile strength, and benchmark data.
- expected_salary_band (object): {"min_lpa": float, "max_lpa": float, "label": string} — the expected salary band in INR Lakhs Per Annum.
- career_readiness (string): One of "Not Ready", "Needs Development", "Market Ready", "Highly Competitive".
- key_differentiators (array of strings): 2-3 factors that make this student stand out (or not).
- improvement_areas (array of strings): 2-3 actionable recommendations to improve placement chances.
- reasoning (string): A 3-5 sentence explanation of how you arrived at the placement probability.
- salary_reasoning (string): A detailed 2-3 sentence explanation justifying the predicted salary window based on the candidate's master score, domain, and historical local market anchors.
- risk_factors (array of strings): 1-3 risks that could lower placement chances.
"""

def execute_forecast(semantic_profile: dict, resume_score: float, github_score: float, cp_score: float, master_score: float, benchmarks: dict, ontology: dict, inter_agent_consensus: dict = None) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.warning("[4.1] OPENAI_API_KEY not set. Running deterministic fallback forecast.")
        return _deterministic_forecast(semantic_profile, resume_score, github_score, cp_score, master_score, benchmarks, ontology)

    forecast_input = {
        "semantic_profile": semantic_profile,
        "inter_agent_consensus": inter_agent_consensus or {},
        "agent_scores": {
            "resume_score": resume_score,
            "github_score": github_score,
            "cp_score": cp_score,
            "master_score": master_score
        },
        "placement_benchmarks": benchmarks.get("placement_probability_curve", {}),
        "salary_benchmarks": benchmarks.get("salary_bands", {}),
        "domain_roles": ontology.get("domain_to_roles", {}),
        "backtesting_reference": benchmarks.get("backtesting_reference", {})
    }

    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.15,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": FORECASTING_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(forecast_input, indent=2)}
            ]
        )
        raw = response.choices[0].message.content
        forecast = json.loads(raw)
        forecast["forecast_status"] = "success"
        forecast["forecast_method"] = "LLM-Driven (GPT-4o)"
        backtest = _run_backtesting(master_score, forecast, benchmarks)
        forecast["backtesting_validation"] = backtest
        return forecast
    except Exception as e:
        fallback = _deterministic_forecast(semantic_profile, resume_score, github_score, cp_score, master_score, benchmarks, ontology)
        fallback["forecast_error"] = str(e)
        return fallback

def _deterministic_forecast(semantic_profile: dict, resume_score: float, github_score: float, cp_score: float, master_score: float, benchmarks: dict, ontology: dict) -> dict:
    placement_pct = 10
    placement_label = "Critical Gap"
    for tier in benchmarks.get("placement_probability_curve", {}).get("tiers", []):
        if tier["score_min"] <= master_score < tier["score_max"]:
            placement_pct = tier["placement_pct"]
            placement_label = tier["label"]
            break
    if master_score >= 100:
        placement_pct = 99
        placement_label = "Exceptional"

    predicted_domain = semantic_profile.get("primary_domain", "General Software Engineering")
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

    roles = ontology.get("domain_to_roles", {}).get("mapping", {}).get(
        predicted_domain,
        ["Software Development Engineer (SDE)"]
    )[:3]

    if master_score >= 80: readiness = "Highly Competitive"
    elif master_score >= 60: readiness = "Market Ready"
    elif master_score >= 40: readiness = "Needs Development"
    else: readiness = "Not Ready"

    forecast = {
        "forecast_status": "fallback",
        "forecast_method": "Deterministic (Benchmark Lookup)",
        "predicted_domain": predicted_domain,
        "domain_confidence": 0.6,
        "recommended_roles": roles,
        "placement_probability": placement_pct,
        "expected_salary_band": salary_band,
        "career_readiness": readiness,
        "key_differentiators": ["Consistent profile ratings", "Core academic alignment"],
        "improvement_areas": ["Deploy projects live", "Engage in more open source"],
        "reasoning": f"Deterministic fallback: master_score={master_score} maps to '{placement_label}' with {placement_pct}% placement probability.",
        "salary_reasoning": f"Based on the Master Score of {master_score}, the candidate is placed in the '{salary_band.get('label')}' tier for the '{predicted_domain}' domain. Historically, this corresponds to an expected package of {salary_band.get('min_lpa')} - {salary_band.get('max_lpa')} LPA.",
        "risk_factors": ["Rate limit risks or profile accessibility"]
    }
    backtest = _run_backtesting(master_score, forecast, benchmarks)
    forecast["backtesting_validation"] = backtest
    return forecast

def _run_backtesting(master_score: float, forecast: dict, benchmarks: dict) -> dict:
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
    if matched_sample is None and master_score >= 85:
        matched_sample = backtesting_samples[-1] if backtesting_samples else None
    if matched_sample is None:
        return {"status": "no_reference_data", "message": "No historical backtesting data available."}
    observed_rate = matched_sample["observed_rate"]
    deviation = abs(predicted_pct - observed_rate)
    alignment = "Strong Alignment" if deviation <= 10 else ("Moderate Alignment" if deviation <= 20 else "Weak Alignment")
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
