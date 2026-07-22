import asyncio
import json
import logging
import sys
import math
import os
from pathlib import Path
from datetime import datetime, timezone

genai_dir = str(Path(__file__).resolve().parents[2])
if genai_dir not in sys.path:
    sys.path.insert(0, genai_dir)

from agent import tool as github_tool
from resugent import utils as resume_tool
from cpgent import main as cp_tool

import config_loader
import career_synthesizer
import forecasting_agent
import agent_communication

async def run_github_agent(handle: str, config: dict) -> dict:
    if not handle:
        return {"status": "failed", "error_log": "No GitHub handle provided", "final_score": 0}
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(github_tool.execute_github_agent, handle, config),
            timeout=240.0
        )
    except Exception as e:
        return {"status": "failed", "error_log": f"Execution Error: {str(e)}", "final_score": 0}

async def run_cp_agent(platforms: dict, config: dict) -> dict:
    if not platforms:
        return {"status": "failed", "error_log": "No CP platforms provided", "final_score": 0}
    try:
        def build_url(base_url, handle):
            if not handle: return None
            if "http" in str(handle): return handle 
            return f"{base_url}{handle}/"
        formatted_urls = {
            "leetcode": build_url("https://leetcode.com/u/", platforms.get('leetcode')),
            "codeforces": build_url("https://codeforces.com/profile/", platforms.get('codeforces')),
            "codechef": build_url("https://www.codechef.com/users/", platforms.get('codechef')),
            "hackerrank": build_url("https://www.hackerrank.com/profile/", platforms.get('hackerrank'))
        }
        return await asyncio.wait_for(
            asyncio.to_thread(cp_tool.execute_cp_agent, formatted_urls, config),
            timeout=45.0
        )
    except Exception as e:
        return {"status": "failed", "error_log": f"Execution Error: {str(e)}", "final_score": 0}

async def run_resume_agent(pdf_path: str, batch_year: int, config: dict) -> dict:
    if not pdf_path:
        return {"status": "failed", "error_log": "No Resume PDF provided", "final_score": 0}
    try:
        current_year = datetime.now().year
        calculated_btech_year = max(1, min(4, 4 - (int(batch_year) - current_year)))
        return await asyncio.wait_for(
            asyncio.to_thread(resume_tool.execute_resume_agent, pdf_path, calculated_btech_year, config),
            timeout=25.0
        )
    except Exception as e:
        return {"status": "failed", "error_log": f"Execution Error: {str(e)}", "final_score": 0}

async def evaluate_student(student_payload: dict, master_config: dict, benchmarks: dict = None, ontology: dict = None) -> dict:
    targets = student_payload.get("agent_targets", {})
    github_task = run_github_agent(targets.get("github_handle"), master_config.get("github", {}))
    cp_task = run_cp_agent(targets.get("cp_platforms"), master_config.get("cp", {}))
    resume_task = run_resume_agent(targets.get("resume_path"), student_payload.get("metadata", {}).get("batch_year", 2026), master_config.get("resume", {}))

    results = await asyncio.gather(resume_task, github_task, cp_task)
    resume_res, github_res, cp_res = results

    resume_score = resume_res.get("final_score", 0)
    github_score = github_res.get("final_score", 0)
    cp_score = cp_res.get("final_score", 0)
    
    # Calculate master score dynamically based on available data profiles to avoid penalizing missing profiles
    has_github = bool(targets.get("github_handle") and str(targets.get("github_handle")).strip())

    consensus = agent_communication.run_inter_agent_communication(
        student_payload=student_payload,
        resume_res=resume_res,
        github_res=github_res,
        cp_res=cp_res,
        ontology=ontology or {}
    )

    semantic_profile = career_synthesizer.synthesize_profile(
        student_payload=student_payload,
        resume_res=resume_res,
        github_res=github_res,
        cp_res=cp_res,
        ontology=ontology or {},
        inter_agent_consensus=consensus
    )

    # Pass master_score=0 as placeholder — server.py will overwrite it after
    # computing via the weighted formula (resume + github + cp + academic inputs).
    forecast = forecasting_agent.execute_forecast(
        semantic_profile=semantic_profile,
        resume_score=resume_score,
        github_score=github_score,
        cp_score=cp_score,
        master_score=0,           # placeholder; server.py overwrites this
        benchmarks=benchmarks or {},
        ontology=ontology or {},
        inter_agent_consensus=consensus
    )

    return {
        "student_id": student_payload.get("student_id"),
        "name": student_payload.get("name"),
        "execution_timestamp": datetime.now(timezone.utc).isoformat(),
        "scores": {
            "resume_score": resume_score,
            "github_score": github_score,
            "cp_score": cp_score,
            # master_score, academic_score, confidence_level, completeness_score
            # are all injected by server.py after weighted calculation
        },
        "evaluations": {
            "resume_agent": resume_res,
            "github_agent": github_res,
            "cp_agent": cp_res
        },
        "inter_agent_consensus": consensus,
        "semantic_profile": semantic_profile,
        "forecasting": forecast
    }
