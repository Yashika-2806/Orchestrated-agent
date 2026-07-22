import json
import math
import re
import os
import openai
from pydantic import BaseModel, Field
from pypdf import PdfReader

class ResumeData(BaseModel):
    total_page_count: int = Field(default=1)
    extracted_links_array: list[str] = Field(default_factory=list)
    raw_email_string: str = Field(default="")
    detected_section_headers: list[str] = Field(default_factory=list)
    skills_section_keywords: list[str] = Field(default_factory=list)
    project_descriptions_text_corpus: str = Field(default="")
    experience_descriptions_text_corpus: str = Field(default="")
    project_titles: list[str] = Field(default_factory=list)
    project_tech_keywords: list[list[str]] = Field(default_factory=list)
    architectural_regex_flags: list[bool] = Field(default_factory=list)
    total_bullet_points_count: int = Field(default=0)
    qualitative_impact_score: int = Field(default=0)
    project_count: int = Field(default=0)
    code_repository_urls: list[str] = Field(default_factory=list)
    deployment_live_urls: list[str] = Field(default_factory=list)
    buzzword_frequency_map: dict[str, int] = Field(default_factory=dict)
    domain_classification_vector: list[str] = Field(default_factory=list)
    experience_timeline_intervals: list[dict] = Field(default_factory=list)
    candidate_name: str = Field(default="Unknown")
    btech_year: int = Field(default=3)

SYSTEM_PROMPT = """You are a precise resume data extractor for B.Tech student resumes.
Return ONLY a valid JSON object — no markdown, no explanation, no extra keys.

Extract EXACTLY these fields:
extracted_links_array (array of strings): Every URL/link found (GitHub, LinkedIn, portfolio, Vercel, Netlify, etc.).
raw_email_string (string): The email address found on the resume.
detected_section_headers (array of strings): All section headings found, e.g. ["Education","Projects","Skills","Experience"].
skills_section_keywords (array of strings): ONLY skills listed in the dedicated Skills section.
project_descriptions_text_corpus (string): All text from the Projects section concatenated.
experience_descriptions_text_corpus (string): All text from Experience/Internships section concatenated.
project_titles (array of strings): Title of each project listed.
project_tech_keywords (array of arrays of strings): For each project, the tech keywords used IN THAT PROJECT (same order as project_titles).
architectural_regex_flags (array of booleans): For each project, true if it uses any of: WebSockets, Kafka, Docker, Kubernetes, Redis, CI/CD, gRPC, Microservices, Distributed Systems, AWS, GCP, Azure, Celery, RabbitMQ. Same order as project_titles.
total_bullet_points_count (int): Total bullet points across Projects and Experience sections.
qualitative_impact_score (int): Score the overall impact of the candidate's projects and experience on a scale of 0 to 100 based on the STAR methodology.
project_count (int): Total number of projects.
code_repository_urls (array of strings): Only GitHub/GitLab repo links for projects.
deployment_live_urls (array of strings): Only live deployment links (Vercel, Netlify, Heroku, AWS link, custom domain for a project).
buzzword_frequency_map (object): Count occurrences of these EXACT words anywhere in the resume:
  ["passionate","detail-oriented","synergy","motivated","hardworking","team player","go-getter","self-starter","results-driven","dynamic","innovative","proactive"]
domain_classification_vector (array of strings): Map skills_section_keywords to these domains only:
  ["Web Development","AI/ML","DevOps","Web3","CyberSecurity","Mobile","Systems","Data Engineering","UI/UX"]
experience_timeline_intervals (array of objects): Each experience entry as:
  {"role": "SDE Intern at Google", "months": 3, "type": "internship"}
  type must be one of: "internship", "freelance", "tech_lead", "member"
candidate_name (string): Full name of the candidate.
btech_year (int): 2, 3, or 4. Infer from graduation year or year of study mentioned. Default 3.
"""

def extract_resume_data(resume_text: str, api_key: str, btech_year: int, page_count: int) -> ResumeData:
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract data from this resume:\n\n{resume_text[:7000]}"}
        ]
    )
    raw = response.choices[0].message.content
    parsed = json.loads(raw)
    parsed["btech_year"] = btech_year
    parsed["total_page_count"] = page_count
    return ResumeData(**parsed)

TIER3_SKILLS = {"golang","go","docker","kubernetes","redis","kafka","grpc","aws","gcp","azure",
                "tensorflow","pytorch","spark","hadoop","elasticsearch","rabbitmq","celery",
                "websockets","microservices","ci/cd","jenkins","terraform"}
TIER2_SKILLS = {"python","java","javascript","typescript","react","nodejs","node.js","sql",
                "mongodb","postgresql","mysql","git","spring","fastapi","flask","django",
                "express","graphql","rest","linux","bash","c#","kotlin","swift"}

def _skill_difficulty(skill: str) -> int:
    s = skill.lower().strip()
    if s in TIER3_SKILLS: return 10
    if s in TIER2_SKILLS: return 5
    return 2

def _project_tier(tech_keywords: list[str], arch_flag: bool) -> int:
    if arch_flag: return 100
    kw = {k.lower() for k in tech_keywords}
    if kw & TIER3_SKILLS: return 100
    has_backend = bool(kw & {"nodejs","node.js","express","django","flask","fastapi","spring","java","python","golang"})
    has_db = bool(kw & {"mongodb","postgresql","mysql","sql","redis","firebase","supabase"})
    if has_backend and has_db: return 65
    return 25

def compute_score(data: ResumeData, config_overrides: dict = None) -> dict:
    config = config_overrides or {}
    consts = config.get("constants", {})
    pens = config.get("penalties", {})
    roles = config.get("role_weights", {})
    weights_map = config.get("weights", {
        2: {"hyg": 0.25, "real": 0.25, "comp": 0.20, "imp": 0.05, "prod": 0.10, "clar": 0.05, "dom": 0.05, "vel": 0.05},
        3: {"hyg": 0.15, "real": 0.20, "comp": 0.25, "imp": 0.10, "prod": 0.15, "clar": 0.05, "dom": 0.05, "vel": 0.05},
        4: {"hyg": 0.05, "real": 0.10, "comp": 0.30, "imp": 0.20, "prod": 0.15, "clar": 0.05, "dom": 0.05, "vel": 0.10}
    })
    alpha = consts.get("alpha", 5.0)
    beta = consts.get("beta", 12.0)
    omega = consts.get("omega", 15.0)
    eps = consts.get("eps", 1.0)
    pen_page = pens.get("hygiene_page_pen", 50)
    pen_link = pens.get("hygiene_link_pen", 15)
    pen_email = pens.get("hygiene_email_pen", 25)
    pen_sec = pens.get("hygiene_sec_pen", 20)
    P = max(data.total_page_count, 1)
    links_lower = [l.lower() for l in data.extracted_links_array]
    has_github = any("github" in l for l in links_lower)
    has_linkedin = any("linkedin" in l for l in links_lower)
    L_missing = (0 if has_github else 1) + (0 if has_linkedin else 1)
    email = data.raw_email_string.lower()
    E_generic = 1 if any(w in email for w in ["cool","coder","gamer","noob","pro","god","king","boss"]) else 0
    mandatory = {"education", "projects", "skills"}
    found = {h.lower() for h in data.detected_section_headers}
    X_missing = len(mandatory - found)
    S_hygiene = max(0, 100 - pen_page * max(0, P - 1) - pen_link * L_missing - pen_email * E_generic - pen_sec * X_missing)
    declared = set(k.lower().strip() for k in data.skills_section_keywords)
    corpus = (data.project_descriptions_text_corpus + " " + data.experience_descriptions_text_corpus).lower()
    applied = {k for k in declared if re.search(r'(?<!\\w)' + re.escape(k) + r'(?!\\w)', corpus)}
    intersect = declared & applied
    sum_intersect = sum(math.log(_skill_difficulty(k) + 1) for k in intersect)
    sum_declared = sum(math.log(_skill_difficulty(k) + 1) for k in declared)
    S_realization = ((sum_intersect + eps) / (sum_declared + eps)) * 100
    if data.project_titles:
        tiers = []
        for i, title in enumerate(data.project_titles):
            tech = data.project_tech_keywords[i] if i < len(data.project_tech_keywords) else []
            arch = data.architectural_regex_flags[i] if i < len(data.architectural_regex_flags) else False
            tiers.append(_project_tier(tech, arch))
        max_cj = max(tiers)
        J = len(data.project_titles)
        S_complexity = min(100, max_cj + alpha * math.log(J + 1))
    else:
        S_complexity = 0.0
    S_impact = min(100, max(0, float(data.qualitative_impact_score)))
    J_total = max(data.project_count, 1)
    J_code = len(data.code_repository_urls)
    J_deploy = len(data.deployment_live_urls)
    S_production = min(100.0, ((J_code + J_deploy) / (2 * J_total)) * 100)
    bmap = data.buzzword_frequency_map or {}
    deduction = omega * sum(math.log(count + 1) for count in bmap.values() if count > 0)
    S_clarity = max(0, 100 - deduction)
    unique_domains = len(set(data.domain_classification_vector))
    S_domain = max(0, 100 - (max(0, unique_domains - 1) * 20))
    velocity_sum = sum(
        e.get("months", 0) * roles.get(e.get("type", "member"), 3)
        for e in data.experience_timeline_intervals
    )
    S_velocity = min(100, math.log2(velocity_sum + 1) * 20)
    year = data.btech_year if data.btech_year in weights_map else 3
    W = weights_map.get(year, weights_map.get(3))
    S_final = (
        W.get("hyg", 0.15)  * S_hygiene +
        W.get("real", 0.20) * S_realization +
        W.get("comp", 0.25) * S_complexity +
        W.get("imp", 0.10)  * S_impact +
        W.get("prod", 0.15) * S_production +
        W.get("clar", 0.05) * S_clarity +
        W.get("dom", 0.05)  * S_domain +
        W.get("vel", 0.05)  * S_velocity
    )
    S_final = round(min(100, max(0, S_final)), 2)
    return {
        "final_score": S_final,
        "btech_year": year,
        "weights": W,
        "S_hygiene": round(S_hygiene, 2),
        "S_realization": round(S_realization, 2),
        "S_complexity": round(S_complexity, 2),
        "S_impact": round(S_impact, 2),
        "S_production": round(S_production, 2),
        "S_clarity": round(S_clarity, 2),
        "S_domain": round(S_domain, 2),
        "S_velocity": round(S_velocity, 2),
        "L_missing": L_missing,
        "E_generic": E_generic,
        "X_missing": X_missing,
        "buzzwords_found": bmap
    }

def execute_resume_agent(pdf_path: str, btech_year: int, config_overrides: dict = None) -> dict:
    try:
        if not pdf_path or not os.path.exists(pdf_path):
            return {
                "agent": "resume",
                "status": "failed",
                "error_log": f"PDF file not found: {pdf_path}",
                "final_score": 0
            }
        reader = PdfReader(pdf_path)
        page_count = len(reader.pages)
        text_corpus = " ".join(page.extract_text() for page in reader.pages if page.extract_text())
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        resume_data = extract_resume_data(text_corpus, api_key, btech_year, page_count)
        score_data = compute_score(resume_data, config_overrides=config_overrides)
        return {
            "agent": "resume",
            "status": "success",
            "final_score": score_data["final_score"],
            "sub_scores": {
                "S_hygiene": score_data["S_hygiene"],
                "S_realization": score_data["S_realization"],
                "S_complexity": score_data["S_complexity"],
                "S_impact": score_data["S_impact"],
                "S_production": score_data["S_production"],
                "S_clarity": score_data["S_clarity"],
                "S_domain": score_data["S_domain"],
                "S_velocity": score_data["S_velocity"]
            },
            "narrative_context": {
                "buzzwords_found": score_data.get("buzzwords_found", {}),
                "generic_email_flag": score_data.get("E_generic", 0),
                "missing_sections": score_data.get("X_missing", 0)
            }
        }
    except Exception as e:
        return {
            "agent": "resume",
            "status": "failed",
            "error_log": f"Resume Thread Error: {str(e)}",
            "final_score": 0
        }
