import os
import pandas as pd

def load_master_config(config_path: str = "master_config.xlsx") -> dict:
    """
    Loads the master Excel configuration workbook and reconstructs the nested 
    dictionaries required by the quantitative scoring engines.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"[-] Configuration file '{config_path}' not found. Please run initialization first.")

    print(f"[*] Loading configuration architectures from {config_path}...")
    
    # --- REMOVED THE EXCELWRITER BLOCK FROM HERE ---

    # Read individual sheets into flat dictionaries
    raw_linkedin = pd.read_excel(config_path, sheet_name="LinkedIn_Config").iloc[0].to_dict()
    raw_cp = pd.read_excel(config_path, sheet_name="CP_Config").iloc[0].to_dict()
    raw_resume = pd.read_excel(config_path, sheet_name="Resume_Config").iloc[0].to_dict()

    
    # Attempt to load GitHub config if it exists, otherwise fall back to empty defaults
    try:
        raw_github = pd.read_excel(config_path, sheet_name="GitHub_Config").iloc[0].to_dict()
    except ValueError:
        raw_github = {}

    # 1. Parse LinkedIn Configuration Structure
    linkedin_config = {
        "weights": {
            "consistency": float(raw_linkedin.get("w_cons", 0.20)),
            "engagement": float(raw_linkedin.get("w_eng", 0.25)),
            "depth": float(raw_linkedin.get("w_dep", 0.25)),
            "authority": float(raw_linkedin.get("w_auth", 0.20)),
            "optimization": float(raw_linkedin.get("w_opt", 0.10))
        },
        "constants": {
            "epsilon": float(raw_linkedin.get("epsilon", 1.0)),
            "comment_weight": float(raw_linkedin.get("comment_weight", 2.0)),
            "repost_weight": float(raw_linkedin.get("repost_weight", 1.5)),
            "reciprocity_bonus": float(raw_linkedin.get("reciprocity_bonus", 10.0)),
            "alpha": float(raw_linkedin.get("alpha", 4.0)),
            "beta": float(raw_linkedin.get("beta", 2.0)),
            "gamma": float(raw_linkedin.get("gamma", 1.5)),
            "lambda_multiplier": float(raw_linkedin.get("lambda_multiplier", 25.0)),
            "target_features": float(raw_linkedin.get("target_features", 5.0))
        }
    }

    # 2. Parse Competitive Programming (CP) Configuration Structure
    cp_config = {
        "weights": {
            "leetcode": float(raw_cp.get("w_lc", 0.40)),
            "codeforces": float(raw_cp.get("w_cf", 0.30)),
            "codechef": float(raw_cp.get("w_cc", 0.20)),
            "hackerrank": float(raw_cp.get("w_hr", 0.10))
        },
        "constants": {
            "lc_rating_target": int(raw_cp.get("lc_rating_target", 2000)),
            "lc_hard_target": int(raw_cp.get("lc_hard_target", 15)),
            "lc_months_target": int(raw_cp.get("lc_months_target", 6)),
            "lc_solved_target": int(raw_cp.get("lc_solved_target", 150)),
            
            "cf_rating_target": int(raw_cp.get("cf_rating_target", 1800)),
            "cf_contest_target": int(raw_cp.get("cf_contest_target", 3)),
            "cf_practice_target": int(raw_cp.get("cf_practice_target", 8)),
            
            "cc_stars_target": int(raw_cp.get("cc_stars_target", 5)),
            "cc_rating_target": int(raw_cp.get("cc_rating_target", 1800)),
            "cc_solved_target": int(raw_cp.get("cc_solved_target", 100)),
            
            "hr_stars_target": int(raw_cp.get("hr_stars_target", 6)),
            "hr_day_factor": float(raw_cp.get("hr_day_factor", 15.0)),
            "hr_perfect_target": int(raw_cp.get("hr_perfect_target", 10))
        }
    }

    # 3. Parse Resume (ResuGent) Configuration Structure
    resume_config = {
        "weights": {
            2: {cat: float(raw_resume.get(f"w2_{cat}")) for cat in ["hyg", "real", "comp", "imp", "prod", "clar", "dom", "vel"]},
            3: {cat: float(raw_resume.get(f"w3_{cat}")) for cat in ["hyg", "real", "comp", "imp", "prod", "clar", "dom", "vel"]},
            4: {cat: float(raw_resume.get(f"w4_{cat}")) for cat in ["hyg", "real", "comp", "imp", "prod", "clar", "dom", "vel"]}
        },
        "constants": {
            "alpha": float(raw_resume.get("alpha", 5.0)),
            "beta": float(raw_resume.get("beta", 12.0)),
            "omega": float(raw_resume.get("omega", 15.0)),
            "eps": float(raw_resume.get("eps", 1.0)),
            "tier1_c": int(raw_resume.get("tier1_c", 25)),
            "tier2_c": int(raw_resume.get("tier2_c", 65)),
            "tier3_c": int(raw_resume.get("tier3_c", 100))
        },
        "penalties": {
            "hygiene_page_pen": int(raw_resume.get("hygiene_page_pen", 50)),
            "hygiene_link_pen": int(raw_resume.get("hygiene_link_pen", 15)),
            "hygiene_email_pen": int(raw_resume.get("hygiene_email_pen", 25)),
            "hygiene_sec_pen": int(raw_resume.get("hygiene_sec_pen", 20))
        },
        "role_weights": {
            "internship": int(raw_resume.get("role_internship", 15)),
            "freelance": int(raw_resume.get("role_freelance", 10)),
            "tech_lead": int(raw_resume.get("role_tech_lead", 10)),
            "member": int(raw_resume.get("role_member", 3))
        }
    }

    # 4. Parse GitHub Configuration Structure (Failsafe fallback built-in)
    github_config = {
        "weights": {
            "consistency": float(raw_github.get("w_cons", 0.20)),
            "community": float(raw_github.get("w_comm", 0.30)),
            "technology": float(raw_github.get("w_tech", 0.25)),
            "management": float(raw_github.get("w_mgmt", 0.15)),
            "advanced": float(raw_github.get("w_adv", 0.10))
        },
        "constants": {
            "epsilon": float(raw_github.get("epsilon", 1.0)),
            "target_ratio": float(raw_github.get("target_ratio", 0.30)),
            "bio_bonus": float(raw_github.get("bio_bonus", 5.0)),
            "name_bonus": float(raw_github.get("name_bonus", 5.0))
        }
    }

    print("[+] Configuration payloads compiled cleanly into runtime frames.")
    
    return {
        "github": github_config,
        "linkedin": linkedin_config,
        "cp": cp_config,
        "resume": resume_config
    }

if __name__ == "__main__":
    # Test compilation flow
    try:
        config = load_master_config()
        import json
        print(json.dumps(config, indent=2))
    except Exception as e:
        print(f"Error executing config loader test: {e}")