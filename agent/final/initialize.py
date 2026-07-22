import pandas as pd

def create_resume_sheet(writer: pd.ExcelWriter):
    resume_defaults = {
        "w2_hyg": 0.25, "w2_real": 0.25, "w2_comp": 0.20, "w2_imp": 0.05, 
        "w2_prod": 0.10, "w2_clar": 0.05, "w2_dom": 0.05, "w2_vel": 0.05,
        "w3_hyg": 0.15, "w3_real": 0.20, "w3_comp": 0.25, "w3_imp": 0.10, 
        "w3_prod": 0.15, "w3_clar": 0.05, "w3_dom": 0.05, "w3_vel": 0.05,
        "w4_hyg": 0.05, "w4_real": 0.10, "w4_comp": 0.30, "w4_imp": 0.20, 
        "w4_prod": 0.15, "w4_clar": 0.05, "w4_dom": 0.05, "w4_vel": 0.10,
        "alpha": 5.0, "beta": 12.0, "omega": 15.0, "eps": 1.0,
        "tier1_c": 25, "tier2_c": 65, "tier3_c": 100,
        "hygiene_page_pen": 50, "hygiene_link_pen": 15, "hygiene_email_pen": 25, "hygiene_sec_pen": 20,
        "role_internship": 15, "role_freelance": 10, "role_tech_lead": 10, "role_member": 3
    }
    df = pd.DataFrame([resume_defaults])
    df.to_excel(writer, sheet_name="Resume_Config", index=False)

def create_cp_sheet(writer: pd.ExcelWriter):
    cp_defaults = {
        "w_lc": 0.40, "w_cf": 0.30, "w_cc": 0.20, "w_hr": 0.10,
        "lc_rating_target": 2000, "lc_hard_target": 15, "lc_months_target": 6, "lc_solved_target": 150,
        "cf_rating_target": 1800, "cf_contest_target": 3, "cf_practice_target": 8,
        "cc_stars_target": 5, "cc_rating_target": 1800, "cc_solved_target": 100,
        "hr_stars_target": 6, "hr_day_factor": 15.0, "hr_perfect_target": 10
    }
    df = pd.DataFrame([cp_defaults])
    df.to_excel(writer, sheet_name="CP_Config", index=False)

def create_linkedin_sheet(writer: pd.ExcelWriter):
    linkedin_defaults = {
        "w_cons": 0.20, "w_eng": 0.25, "w_dep": 0.25, "w_auth": 0.20, "w_opt": 0.10,
        "epsilon": 1.0, "comment_weight": 2.0, "repost_weight": 1.5, "reciprocity_bonus": 10.0,
        "alpha": 4.0, "beta": 2.0, "gamma": 1.5, "lambda_multiplier": 25.0, "target_features": 5.0
    }
    df = pd.DataFrame([linkedin_defaults])
    df.to_excel(writer, sheet_name="LinkedIn_Config", index=False)

def create_github_sheet(writer: pd.ExcelWriter):
    github_defaults = {
        "w_cons": 0.20, "w_comm": 0.30, "w_tech": 0.25, "w_mgmt": 0.15, "w_adv": 0.10,
        "epsilon": 1.0, "sweet_spot_low": 0.15, "sweet_spot_high": 0.85, "points_per_collab": 20.0,
        "partial_credit": 0.2, "star_bonus": 2.0, "fork_bonus": 5.0,
        "alpha": 5.0, "beta": 3.0, "breadth_ceiling": 8.0,
        "target_ratio": 0.75, "bio_bonus": 10.0, "name_bonus": 5.0,
        "gamma": 10.0, "adv_target": 3
    }
    df = pd.DataFrame([github_defaults])
    df.to_excel(writer, sheet_name="GitHub_Config", index=False)

def initialize_master_config():
    filepath = "master_config.xlsx"
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        create_github_sheet(writer)
        create_resume_sheet(writer)  
        create_linkedin_sheet(writer) 
        create_cp_sheet(writer)    

if __name__ == "__main__":
    initialize_master_config()
