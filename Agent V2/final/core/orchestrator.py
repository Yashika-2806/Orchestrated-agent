import asyncio
import json
import logging
import sys
import math
import os
import openai
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone 

# Calculate the path to the 'GenAI' directory
genai_dir = str(Path(__file__).resolve().parents[2])

# Add GenAI to sys.path if it is not already there
if genai_dir not in sys.path:
    sys.path.insert(0, genai_dir)

# Import the tool module using its directory path
from agent import tool as github_tool
from resugent import utils as resume_tool
from cpgent import main as cp_tool

# Import the Configuration Loader
import config_loader

# Import the Forecasting Pipeline Modules [2.6], [4.1], Inter-Agent Communication Protocol, Blackboard & Semantic Cache
import career_synthesizer
import forecasting_agent
import agent_communication
from blackboard import SharedBlackboard
from semantic_cache import SemanticCacheEngine

# Setup Basic Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- ASYNC WORKER WRAPPERS WITH FAULT ISOLATION ---

async def run_github_agent(handle: str, config: dict) -> dict:
    if not handle:
        return {"status": "failed", "error_log": "No GitHub handle provided", "final_score": 0}
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(github_tool.execute_github_agent, handle, config),
            timeout=240.0
        )
    except asyncio.TimeoutError:
        return {"status": "failed", "error_log": "Timeout: GitHub API response exceeded 240s", "final_score": 0}
    except Exception as e:
        return {"status": "failed", "error_log": f"Execution Error: {str(e)}", "final_score": 0}
    


async def run_cp_agent(platforms: dict, config: dict) -> dict:
    if not platforms:
        return {"status": "failed", "error_log": "No CP platforms provided", "final_score": 0}
    try:
        # Safely handle either raw usernames OR full URLs from the CSV
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
            timeout=30.0
        )
    except asyncio.TimeoutError:
        return {"status": "failed", "error_log": "Timeout: CP APIs exceeded 30s", "final_score": 0}
    except Exception as e:
        return {"status": "failed", "error_log": f"Execution Error: {str(e)}", "final_score": 0}


async def run_resume_agent(pdf_path: str, batch_year: int, config: dict) -> dict:
    if not pdf_path:
        return {"status": "failed", "error_log": "No Resume PDF path provided", "final_score": 0}
    try:
        current_year = datetime.now().year
        calculated_btech_year = max(1, min(4, 4 - (int(batch_year) - current_year)))

        return await asyncio.wait_for(
            asyncio.to_thread(resume_tool.execute_resume_agent, pdf_path, calculated_btech_year, config),
            timeout=20.0
        )
    except asyncio.TimeoutError:
        return {"status": "failed", "error_log": "Timeout: Groq LLM extraction exceeded 20s", "final_score": 0}
    except Exception as e:
        return {"status": "failed", "error_log": f"Execution Error: {str(e)}", "final_score": 0}


# --- LLM SMART DATA EXTRACTOR ---

def llm_smart_parser(raw_row_string: str, available_resumes: list) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set. Cannot run smart parser.")
        
    client = openai.OpenAI(api_key=api_key)
    
    prompt = f"""You are an intelligent data parser for a student evaluation pipeline.
You are given a raw string representing a jumbled row from a CSV, and a list of available resume filenames.

Your task is to extract the data and return a JSON object with EXACTLY these keys:
- roll_number (string): The student's roll number or ID.
- name (string): The student's name.
- github_url (string or null): Find the GitHub profile URL. Look for github.com.
- linkedin_url (string or null): Find the LinkedIn profile URL. Look for linkedin.com.
- leetcode_url (string or null): Find the LeetCode profile URL. Look for leetcode.com.
- codeforces_url (string or null): Find the Codeforces profile URL. Look for codeforces.com.
- hackerrank_url (string or null): Find the HackerRank profile URL. Look for hackerrank.com.
- codechef_url (string or null): Find the CodeChef profile URL. Look for codechef.com.
- resume_filename (string or null): Look at the available resumes list. Find the filename that best matches the student's name or roll_number. If no good match exists, return null.

Here are the available resumes:
{available_resumes}

Here is the raw CSV row string:
{raw_row_string}

Return ONLY a valid JSON object. Do not include markdown or explanations.
"""
    
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a precise JSON data extraction AI."},
            {"role": "user", "content": prompt}
        ]
    )
    
    raw = response.choices[0].message.content
    return json.loads(raw)


# --- MASTER PIPELINE ORCHESTRATOR ---

async def evaluate_student(student_payload: dict, master_config: dict, benchmarks: dict = None, ontology: dict = None) -> dict:
    targets = student_payload.get("agent_targets", {})
    logging.info(f"[*] Booting evaluation sequence for Student ID: {student_payload.get('student_id')}")

    # [2.7] Async Agent Orchestrator & Fault Isolation — Launch 3 concurrent agents
    github_task = run_github_agent(targets.get("github_handle"), master_config.get("github", {}))
    cp_task = run_cp_agent(targets.get("cp_platforms"), master_config.get("cp", {}))
    resume_task = run_resume_agent(targets.get("resume_path"), student_payload.get("metadata", {}).get("batch_year", 2026), master_config.get("resume", {}))

    results = await asyncio.gather(resume_task, github_task, cp_task)
    resume_res, github_res, cp_res = results

    # Extract agent scores
    resume_score = resume_res.get("final_score", 0)
    github_score = github_res.get("final_score", 0)
    cp_score = cp_res.get("final_score", 0)
    
    # Calculate master score dynamically based on available data profiles to avoid penalizing missing profiles
    has_github = bool(targets.get("github_handle") and str(targets.get("github_handle")).strip())
    cp_platforms = targets.get("cp_platforms") or {}
    has_cp = bool(any(val and str(val).strip() for val in cp_platforms.values()))
    
    # Dynamic weighting using peak coding score logic
    if has_github and has_cp:
        # Both linked: Resume 40%, Coding (max of GitHub & CP) 60%
        master_score = round((resume_score * 0.40) + max(github_score, cp_score) * 0.60, 2)
        total_weight = 100
    elif has_github:
        # Only GitHub linked: Resume 57%, GitHub 43%
        master_score = round((resume_score * 0.57) + (github_score * 0.43), 2)
        total_weight = 70
    elif has_cp:
        # Only CP linked: Resume 57%, CP 43%
        master_score = round((resume_score * 0.57) + (cp_score * 0.43), 2)
        total_weight = 70
    else:
        # No coding profiles: Resume 100%
        master_score = round(resume_score, 2)
        total_weight = 40
        
    completeness_score = int(total_weight)
    
    if completeness_score >= 90:
        confidence_level = "High"
    elif completeness_score >= 60:
        confidence_level = "Medium"
    else:
        confidence_level = "Low"

    logging.info(f"[+] 3 Agent evaluations complete. Master Score: {master_score} (Completeness: {completeness_score}%)")

    # [Shared Local Context Cache & Blackboard] Publish Agent Findings Immediately
    blackboard = SharedBlackboard()
    blackboard.publish_github_findings(github_res)
    blackboard.publish_resume_findings(resume_res)
    blackboard.publish_cp_findings(cp_res)
    logging.info(f"[*] Agent findings published to Shared Local Context Blackboard.")

    # [Agent-to-Agent Communication Protocol] Strict Schema Query & Inter-Agent Brainstorming
    logging.info(f"[*] Triggering Agent-to-Agent Communication Protocol (I-A2A Bus)...")
    consensus = agent_communication.run_inter_agent_communication(
        student_payload=student_payload,
        resume_res=resume_res,
        github_res=github_res,
        cp_res=cp_res,
        ontology=ontology or {},
        blackboard=blackboard
    )

    # [2.6] LLM Career Semantic Synthesizer & Profile Builder
    logging.info(f"[*] Engaging Career Semantic Synthesizer [2.6]...")
    semantic_profile = career_synthesizer.synthesize_profile(
        student_payload=student_payload,
        resume_res=resume_res,
        github_res=github_res,
        cp_res=cp_res,
        ontology=ontology or {},
        inter_agent_consensus=consensus
    )

    # [Semantic Caching Engine (Part B)] Check local persistent cache
    cache_engine = SemanticCacheEngine()
    anchored_domain = consensus.get("validated_primary_domain") or semantic_profile.get("primary_domain", "Web Development")
    profile_hash = cache_engine.compute_profile_hash(
        master_score=master_score,
        anchored_domain=anchored_domain,
        github_score=github_score,
        cp_score=cp_score,
        resume_score=resume_score,
        verified_skills=consensus.get("verified_skills", [])
    )

    cached_forecast = cache_engine.get(profile_hash)
    if cached_forecast:
        logging.info(f"[*] [Semantic Cache HIT] Serving forecasting payload from local disk cache (0ms, $0 API cost).")
        forecast = cached_forecast
    else:
        # [4.1] Master Career Synthesis & Forecasting Agent
        logging.info(f"[*] [Semantic Cache MISS] Engaging Forecasting Agent [4.1] with Pydantic Exit-Point Guardrail...")
        forecast = forecasting_agent.execute_forecast(
            semantic_profile=semantic_profile,
            resume_score=resume_score,
            github_score=github_score,
            cp_score=cp_score,
            master_score=master_score,
            benchmarks=benchmarks or {},
            ontology=ontology or {},
            inter_agent_consensus=consensus
        )
        cache_engine.set(profile_hash, forecast)

    final_evaluation = {
        "student_id": student_payload.get("student_id"),
        "name": student_payload.get("name"),
        "execution_timestamp": datetime.now(timezone.utc).isoformat(),
        "scores": {
            "resume_score": resume_score,
            "github_score": github_score if has_github else None,
            "cp_score": cp_score if has_cp else None,
            "master_score": master_score,
            "completeness_score": completeness_score,
            "confidence_level": confidence_level
        },
        "evaluations": {
            "resume_agent": resume_res,
            "github_agent": github_res,
            "cp_agent": cp_res
        },
        "blackboard_snapshot": blackboard.get_snapshot(),
        "inter_agent_consensus": consensus,
        "semantic_profile": semantic_profile,
        "forecasting": forecast
    }

    logging.info(f"[+] Full pipeline complete for Student ID: {student_payload.get('student_id')} "
                 f"| Domain: {forecast.get('predicted_domain')} "
                 f"| Placement: {forecast.get('placement_probability')}%")
    return final_evaluation


# --- ENTRY POINT ---

if __name__ == "__main__":
    # 1. Parse Command Line Arguments
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <yx> [n]")
        print("Example: python orchestrator.py y2 5")
        sys.exit(1)

    yx = sys.argv[1]  # Expected: 'y2', 'y3', or 'y4'
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 1  # Default to row 1

    # Extract the numerical year (2, 3, or 4) from the string 'y2'
    try:
        year_val = int(yx.replace('y', ''))
    except ValueError:
        print(f"[-] Invalid year argument: {yx}. Please use y2, y3, or y4.")
        sys.exit(1)

    # 2. Define Absolute Paths
    genai_dir_path = Path(__file__).resolve().parents[2]
    suites_dir = genai_dir_path / "Suites"
    csv_file_path = suites_dir / f"year{year_val}_data.csv"
    config_path = Path(__file__).parent.parent / "config" / "master_config.xlsx"

    if not csv_file_path.exists():
        print(f"[-] Error: Could not find CSV file at {csv_file_path}")
        sys.exit(1)

    # 3. Load Configurations
    try:
        master_configuration = config_loader.load_master_config(str(config_path))
    except Exception as e:
        logging.error(f"Failed to load master configuration: {e}")
        sys.exit(1)

    # 4. Read Data from CSV
    print(f"[*] Loading {csv_file_path.name} ...")
    
    import csv
    with open(csv_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        header = next(reader)
        max_cols = len(header)
        for row in reader:
            max_cols = max(max_cols, len(row))
            
    if max_cols > len(header):
        full_headers = header.copy()
        extra_cols = ["codechef", "extra1", "extra2"]
        needed = max_cols - len(header)
        full_headers.extend(extra_cols[:needed])
        df = pd.read_csv(csv_file_path, names=full_headers, skiprows=1)
    else:
        df = pd.read_csv(csv_file_path)


    # Convert 1-indexed 'n' to 0-indexed row for pandas
    row_idx = n - 1
    if row_idx < 0 or row_idx >= len(df):
        print(f"[-] Error: Row {n} is out of bounds. The CSV has {len(df)} rows.")
        sys.exit(1)

    raw_row = df.iloc[row_idx].to_dict()

    # Clean NaN values from Pandas to None for python compatibility
    student_data = {}
    for k, v in raw_row.items():
        if isinstance(v, float) and math.isnan(v):
            student_data[k] = None
        else:
            student_data[k] = v

    print(f"[*] Engaging LLM Smart Parser to clean and route CSV data...")
    resumes_dir = suites_dir / "resumes"
    available_resumes = []
    if resumes_dir.exists():
        available_resumes = [f.name for f in resumes_dir.iterdir() if f.suffix.lower() == '.pdf']
        
    try:
        from dotenv import load_dotenv
        load_dotenv(genai_dir_path / "resugent" / ".env")
        smart_data = llm_smart_parser(str(raw_row), available_resumes)
    except Exception as e:
        print(f"[-] LLM Smart Parser Failed: {e}")
        sys.exit(1)

    roll_number = str(smart_data.get('roll_number', ''))
    student_name = smart_data.get('name', 'Unknown')
    
    # Calculate batch_year dynamically for the math engine weights
    current_year = datetime.now().year
    batch_year = current_year + (4 - year_val)

    resume_target = str(resumes_dir / smart_data['resume_filename']) if smart_data.get('resume_filename') else ""
    print(f"[*] LLM mapped resume to: {smart_data.get('resume_filename')}")

    # 5. Construct Payload
    test_student = {
        "student_id": roll_number,
        "name": student_name,
        "metadata": {
            "batch_year": str(batch_year),
            "branch": "Computer Science"
        },
        "agent_targets": {
            "resume_path": resume_target,
            "github_handle": smart_data.get('github_url'),
            "linkedin_url": smart_data.get('linkedin_url'),
            "cp_platforms": {
                "leetcode": smart_data.get('leetcode_url'),
                "codeforces": smart_data.get('codeforces_url'),
                "codechef": smart_data.get('codechef_url'), 
                "hackerrank": smart_data.get('hackerrank_url')
            }
        }
    }

    # 6. Load Forecasting Data Sources [1.5] and [1.6]
    benchmarks_path = Path(__file__).parent.parent / "config" / "benchmarks.json"
    ontology_path = Path(__file__).parent.parent / "config" / "domain_ontology.json"
    
    benchmarks_data = {}
    ontology_data = {}
    try:
        with open(benchmarks_path, "r") as f:
            benchmarks_data = json.load(f)
        print("[+] Historical Benchmarks [1.5] loaded.")
    except Exception as e:
        print(f"[!] Warning: Could not load benchmarks.json: {e}")
    
    try:
        with open(ontology_path, "r") as f:
            ontology_data = json.load(f)
        print("[+] Domain Ontology [1.6] loaded.")
    except Exception as e:
        print(f"[!] Warning: Could not load domain_ontology.json: {e}")

    # 7. Trigger the Full Async Pipeline (Agents + Synthesizer + Forecaster)
    final_result = asyncio.run(evaluate_student(
        test_student, master_configuration,
        benchmarks=benchmarks_data, ontology=ontology_data
    ))

    # 8. Extract Scores, Consensus and Forecasting Data
    scores = final_result.get("scores", {})
    resume_score = scores.get("resume_score", 0)
    github_score = scores.get("github_score", 0)
    cp_score = scores.get("cp_score", 0)
    master_score = scores.get("master_score", 0)
    
    consensus = final_result.get("inter_agent_consensus", {})
    validated_domain = consensus.get("validated_primary_domain", "Unknown")
    domain_validation_score = consensus.get("domain_validation_score", 0)
    verified_skills = consensus.get("verified_skills", [])
    unverified_claims = consensus.get("unverified_resume_claims", [])

    forecast = final_result.get("forecasting", {})
    predicted_domain = forecast.get("predicted_domain", validated_domain)
    placement_probability = forecast.get("placement_probability", 0)
    salary_band = forecast.get("expected_salary_band", {})
    career_readiness = forecast.get("career_readiness", "Unknown")
    recommended_roles = forecast.get("recommended_roles", [])

    # 9. Build Forecasting CSV Report [4.2]
    output_row = student_data.copy()
    output_row["resume_score"] = resume_score
    output_row["github_score"] = github_score
    output_row["cp_score"] = cp_score
    output_row["master_score"] = master_score
    output_row["validated_domain"] = validated_domain
    output_row["domain_validation_score"] = domain_validation_score
    output_row["verified_skills_count"] = len(verified_skills)
    output_row["unverified_resume_claims_count"] = len(unverified_claims)
    output_row["predicted_domain"] = predicted_domain
    output_row["placement_probability"] = placement_probability
    output_row["salary_band_min_lpa"] = salary_band.get("min_lpa", 0)
    output_row["salary_band_max_lpa"] = salary_band.get("max_lpa", 0)
    output_row["salary_band_label"] = salary_band.get("label", "Unknown")
    output_row["career_readiness"] = career_readiness
    output_row["recommended_roles"] = "; ".join(recommended_roles[:3])

    # 10. Save Outputs
    output_dir = Path(__file__).parent.parent / "storage" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    # [4.2] Forecasting CSV Report
    output_csv_filename = output_dir / f"student-{roll_number}_scores_{yx}_{n}.csv"
    pd.DataFrame([output_row]).to_csv(output_csv_filename, index=False)
    
    # [4.3] Deep Forecasting JSON & Career Audit
    output_json_filename = output_dir / f"student-{roll_number}_raw_payload_{yx}_{n}.json"
    with open(output_json_filename, "w") as f:
        json.dump(final_result, f, indent=4)
    
    print(f"\n{'='*65}")
    print(f"[*] EXECUTION COMPLETE — Inter-Agent Consensus & Forecasting Pivot")
    print(f"{'='*65}")
    print(f"    Student:                  {student_name} ({roll_number})")
    print(f"    Master Score:             {master_score}")
    print(f"    Validated Domain:         {validated_domain} (Validation Score: {domain_validation_score}%)")
    print(f"    Verified Skills Count:    {len(verified_skills)}")
    print(f"    Unverified Resume Claims: {len(unverified_claims)}")
    print(f"    Placement Probability:    {placement_probability}%")
    print(f"    Expected Salary Band:     INR {salary_band.get('min_lpa', '?')}-{salary_band.get('max_lpa', '?')} LPA ({salary_band.get('label', '?')})")
    print(f"    Career Readiness:         {career_readiness}")
    print(f"    Recommended Roles:        {', '.join(recommended_roles[:3])}")
    print(f"{'='*65}")
    print(f"    -> [4.2] Forecasting CSV: {output_csv_filename}")
    print(f"    -> [4.3] Deep JSON Audit: {output_json_filename}")