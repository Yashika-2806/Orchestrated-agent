import asyncio
import math
import re
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import json
import cloudscraper
import httpx
from bs4 import BeautifulSoup

@dataclass
class ScraperOutput:
    platform: str
    profile_url: str
    solved_count: Optional[int] = None
    rating: Optional[int] = None
    rank: Optional[int] = None
    contest_rating: Optional[int] = None
    extra: Dict[str, Any] = field(default_factory=dict)

async def scrape_leetcode(url: str) -> ScraperOutput:
    username_match = re.search(r"leetcode\.com/(?:u/|profile/)?([^/]+)", url)
    if not username_match:
        raise ValueError(f"Invalid LeetCode URL: {url}")
    username = username_match.group(1)
    query = {
        "query": """query getUserProfile($username: String!) {
          matchedUser(username: $username) {
            profile { ranking }
            submitStats {
              acSubmissionNum { difficulty count submissions }
              totalSubmissionNum { difficulty count submissions }
            }
            userCalendar { submissionCalendar }
          }
        }""",
        "variables": {"username": username},
    }
    contest_query = {
        "query": """query userContestRankingInfo($username: String!) {
          userContestRanking(username: $username) {
            attendedContestsCount
            rating
            globalRanking
            totalParticipants
          }
          userContestRankingHistory(username: $username) {
            attended
            contest { startTime }
          }
        }""",
        "variables": {"username": username},
    }
    headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        r1 = await client.post("https://leetcode.com/graphql", json=query, headers=headers)
        r2 = await client.post("https://leetcode.com/graphql", json=contest_query, headers=headers)
    try:
        profile_data = r1.json().get("data", {}).get("matchedUser") or {}
        contest_data = r2.json().get("data", {})
    except json.JSONDecodeError:
        profile_data, contest_data = {}, {}
    ac_submissions = (profile_data.get("submitStats") or {}).get("acSubmissionNum") or []
    total_submissions_list = (profile_data.get("submitStats") or {}).get("totalSubmissionNum") or []
    hard_solved = next((item["count"] for item in ac_submissions if item.get("difficulty") == "Hard"), 0)
    solved = next((item["count"] for item in ac_submissions if item.get("difficulty") == "All"), 0)
    total_accepted = next((item["submissions"] for item in ac_submissions if item.get("difficulty") == "All"), 0)
    total_attempted = next((item["submissions"] for item in total_submissions_list if item.get("difficulty") == "All"), 0)
    contest_ranking = contest_data.get("userContestRanking") or {}
    history = contest_data.get("userContestRankingHistory") or []
    daily_activity = {}
    calendar_str = (profile_data.get("userCalendar") or {}).get("submissionCalendar")
    if calendar_str:
        try:
            cal = json.loads(calendar_str)
            for ts_str, count in cal.items():
                dt = datetime.fromtimestamp(int(ts_str), tz=timezone.utc)
                daily_activity[dt.strftime("%Y-%m-%d")] = count
        except Exception:
            pass
    return ScraperOutput(
        platform="LeetCode",
        profile_url=url,
        solved_count=solved,
        rank=profile_data.get("profile", {}).get("ranking"),
        contest_rating=int(contest_ranking.get("rating") or 0),
        extra={
            "hard_solved": hard_solved,
            "total_accepted": total_accepted,
            "total_attempted": total_attempted,
            "global_rank": contest_ranking.get("globalRanking"),
            "daily_activity": daily_activity,
            "contests_history": history
        }
    )

async def scrape_codeforces(url: str) -> ScraperOutput:
    handle_match = re.search(r"codeforces\.com/(?:profile/|submissions/)?([^/]+)", url)
    if not handle_match:
        raise ValueError(f"Invalid Codeforces URL: {url}")
    handle = handle_match.group(1)
    headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"}
    def fetch_cf_user():
        scraper = cloudscraper.create_scraper()
        r = scraper.get(f"https://codeforces.com/api/user.info?handles={handle}", timeout=15)
        if r.status_code == 200 and r.json().get("status") == "OK":
            return r.json().get("result", [{}])[0]
        return {}
    loop = asyncio.get_running_loop()
    user_info = await loop.run_in_executor(None, fetch_cf_user)
    max_rating = user_info.get("maxRating", 0)
    contests_last_90 = 0
    total_contests = 1
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            r = await client.get(f"https://codeforces.com/api/user.rating?handle={handle}", headers=headers)
            if r.status_code == 200 and r.json().get("status") == "OK":
                history = r.json().get("result", [])
                total_contests = max(len(history), 1)
                now_ts = datetime.now(timezone.utc).timestamp()
                contests_last_90 = sum(1 for c in history if (now_ts - c.get("ratingUpdateTimeSeconds", 0)) <= 90 * 86400)
    except Exception:
        pass
    daily_activity = {}
    wrong_during_contest = 0
    solved_problems = set()
    try:
        all_results = []
        start = 1
        page_size = 1000
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            while True:
                status_url = f"https://codeforces.com/api/user.status?handle={handle}&from={start}&count={page_size}"
                r_status = await client.get(status_url, headers=headers)
                if r_status.status_code == 200 and r_status.json().get("status") == "OK":
                    results = r_status.json().get("result", [])
                    all_results.extend(results)
                    if len(results) < page_size or start > 5000:
                        break
                    start += page_size
                else:
                    break
        for item in all_results:
            verdict = item.get("verdict")
            if verdict == "OK":
                prob = item.get("problem", {})
                if prob.get("name"): solved_problems.add(prob.get("name"))
            creation_time = item.get("creationTimeSeconds")
            if creation_time:
                dt = datetime.fromtimestamp(creation_time, tz=timezone.utc)
                date_str = dt.strftime("%Y-%m-%d")
                daily_activity[date_str] = daily_activity.get(date_str, 0) + 1
            if verdict and verdict not in ("OK", "COMPILATION_ERROR") and item.get("author", {}).get("participantType") == "CONTESTANT":
                wrong_during_contest += 1
    except Exception:
        pass
    return ScraperOutput(
        platform="Codeforces",
        profile_url=url,
        solved_count=len(solved_problems),
        contest_rating=max_rating,
        extra={
            "max_rating": max_rating,
            "contests_last_90": contests_last_90,
            "wrong_during_contest": wrong_during_contest,
            "total_contest_count": total_contests,
            "daily_activity": daily_activity
        }
    )

async def scrape_codechef(url: str) -> ScraperOutput:
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        r = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")
    rating = stars = global_rank = solved = fully_solved = partially_solved = 0
    rating_tag = soup.find("div", class_=re.compile(r"rating-number"))
    if rating_tag:
        try: rating = int(rating_tag.get_text(strip=True))
        except ValueError: pass
    star_section = soup.find("div", class_=re.compile(r"rating-star|stars"))
    if star_section:
        star_match = re.search(r"(\\d+)\\s*[★⭐]", star_section.get_text(strip=True))
        if star_match: stars = int(star_match.group(1))
    solved_tag = soup.find(string=re.compile(r"Problems solved", re.IGNORECASE))
    if solved_tag:
        solved_match = re.search(r"(\\d+)", solved_tag)
        if solved_match: solved = int(solved_match.group(1))
    fully_match = re.search(r"(\\d+)\\s*Fully\\s*Solved", r.text, re.IGNORECASE)
    if fully_match: fully_solved = int(fully_match.group(1))
    return ScraperOutput(
        platform="CodeChef",
        profile_url=url,
        solved_count=solved or fully_solved,
        rating=rating,
        extra={
            "stars": stars,
            "fully_solved": fully_solved,
            "partially_solved": partially_solved,
            "daily_activity": {}
        }
    )

async def scrape_hackerrank(url: str) -> ScraperOutput:
    username_match = re.search(r"hackerrank\.com/(?:profile/)?([^/]+)", url)
    if not username_match:
        raise ValueError(f"Invalid HackerRank URL: {url}")
    username = username_match.group(1)
    headers = {"User-Agent": "Mozilla/5.0"}
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        r1 = await client.get(f"https://www.hackerrank.com/rest/hackers/{username}", headers=headers)
        r2 = await client.get(f"https://www.hackerrank.com/rest/hackers/{username}/badges", headers=headers)
        r3 = await client.get(f"https://www.hackerrank.com/rest/hackers/{username}/scores", headers=headers)
    try:
        hk_data = r1.json() if r1.status_code == 200 else {}
        badges_data = r2.json() if r2.status_code == 200 else {}
        scores_data = r3.json() if r3.status_code == 200 else []
    except json.JSONDecodeError:
        hk_data, badges_data, scores_data = {}, {}, []
    total_score = 0.0
    badge_stars = []
    perfect = solved = 0
    if badges_data:
        for badge in badges_data.get("models", []):
            stars = badge.get("stars", 0)
            badge_stars.append(stars)
            solved += badge.get("solved", 0)
            if stars > 0 and stars == badge.get("total_stars"):
                perfect += 1
    if scores_data:
        for track in scores_data:
            total_score += track.get("practice", {}).get("score", 0.0)
    if solved == 0 and total_score > 0:
        solved = int(total_score // 10) or 1
    if perfect == 0 and solved > 0:
        perfect = max(1, solved // 5)
    return ScraperOutput(
        platform="HackerRank",
        profile_url=url,
        solved_count=solved,
        extra={
            "total_score": total_score,
            "badge_stars": badge_stars,
            "perfect_challenges": perfect,
            "created_at": hk_data.get("model", {}).get("created_at"),
            "daily_activity": {}
        }
    )

def clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, v))

def apply_persona_weights(clout: float, cons: float, vel: float) -> Tuple[float, str]:
    if clout >= 75 and cons >= 60:
        return (clout * 0.60 + cons * 0.20 + vel * 0.20), "Contest Hunter"
    elif clout < 40 and cons >= 75:
        return (clout * 0.20 + cons * 0.60 + vel * 0.20), "Streak Maker"
    else:
        return (clout * 0.40 + cons * 0.40 + vel * 0.20), "Balanced Developer"

def extract_raw_subscores_leetcode(profile: ScraperOutput, config: dict) -> dict:
    c = config.get("constants", {})
    e = profile.extra
    clout_rating = clamp((profile.contest_rating or 0) / c.get('lc_rating_target', 2000) * 50)
    clout_hard = clamp(e.get('hard_solved', 0) / c.get('lc_hard_target', 15) * 20)
    clout_val = clamp(clout_rating + clout_hard)
    daily = e.get('daily_activity', {})
    active_days_90 = sum(1 for dt_str in daily if (datetime.now(timezone.utc) - datetime.strptime(dt_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)).days <= 90)
    cons_val = clamp(active_days_90 / 30 * 100)
    accept_rate = e.get('total_accepted', 0) / e.get('total_attempted', 1) if e.get('total_attempted', 0) > 0 else 0.5
    vel_acceptance = clamp(accept_rate * 60)
    vel_volume = clamp((profile.solved_count or 0) / c.get('lc_solved_target', 150) * 40)
    vel_val = clamp(vel_acceptance + vel_volume)
    return {"clout": clout_val, "consistency": cons_val, "velocity": vel_val}

def extract_raw_subscores_codeforces(profile: ScraperOutput, config: dict) -> dict:
    c = config.get("constants", {})
    e = profile.extra
    clout_val = clamp(e.get('max_rating', 0) / c.get('cf_rating_target', 1800) * 100)
    c_90 = e.get('contests_last_90', 0)
    if c_90 > 0:
        cons_val = clamp(c_90 / c.get('cf_contest_target', 3) * 100)
    else:
        daily = e.get('daily_activity', {})
        active_days_90 = sum(1 for dt_str in daily if (datetime.now(timezone.utc) - datetime.strptime(dt_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)).days <= 90)
        cons_val = clamp(active_days_90 / c.get('cf_practice_target', 8) * 100)
    vel_val = clamp(100 - (e.get('wrong_during_contest', 0) / e.get('total_contest_count', 1)) * 5)
    return {"clout": clout_val, "consistency": cons_val, "velocity": vel_val}

def extract_raw_subscores_codechef(profile: ScraperOutput, config: dict) -> dict:
    c = config.get("constants", {})
    e = profile.extra
    clout_val = clamp(e.get('stars', 0) / c.get('cc_stars_target', 5) * 60 + (profile.rating or 0) / c.get('cc_rating_target', 1800) * 40)
    cons_val = clamp((profile.solved_count or 0) / c.get('cc_solved_target', 100) * 100)
    attempted = (e.get('fully_solved') or 0) + (e.get('partially_solved') or 0)
    full_ratio = (e.get('fully_solved') or 0) / attempted if attempted > 0 else 0.5
    vel_val = clamp(full_ratio * 100)
    return {"clout": clout_val, "consistency": cons_val, "velocity": vel_val}

def extract_raw_subscores_hackerrank(profile: ScraperOutput, config: dict) -> dict:
    c = config.get("constants", {})
    e = profile.extra
    clout_val = clamp(sum(e.get('badge_stars', [])) / c.get('hr_stars_target', 6) * 100)
    days_active = 365
    if e.get('created_at'):
        try:
            days_active = max(1, (datetime.now(timezone.utc) - datetime.fromisoformat(str(e['created_at']).replace("Z", "+00:00"))).days)
        except Exception: pass
    cons_val = clamp((e.get('total_score', 0) / min(365, days_active)) * c.get('hr_day_factor', 15.0))
    vel_val = clamp(e.get('perfect_challenges', 0) / c.get('hr_perfect_target', 10) * 100)
    return {"clout": clout_val, "consistency": cons_val, "velocity": vel_val}

async def async_execute(platforms: dict, config: dict) -> dict:
    tasks, platform_map = [], []
    if platforms.get("leetcode"):
        tasks.append(scrape_leetcode(platforms["leetcode"]))
        platform_map.append("leetcode")
    if platforms.get("codeforces"):
        tasks.append(scrape_codeforces(platforms["codeforces"]))
        platform_map.append("codeforces")
    if platforms.get("codechef"):
        tasks.append(scrape_codechef(platforms["codechef"]))
        platform_map.append("codechef")
    if platforms.get("hackerrank"):
        tasks.append(scrape_hackerrank(platforms["hackerrank"]))
        platform_map.append("hackerrank")
    if not tasks:
        return {"status": "failed", "error_log": "No valid platforms passed", "final_score": 0}
    results = await asyncio.gather(*tasks, return_exceptions=True)
    scored_platforms = {}
    unified_daily = {}
    for idx, res in enumerate(results):
        plat_key = platform_map[idx]
        if isinstance(res, Exception):
            print(f"[-] CP Scraper failed for {plat_key}: {res}")
            continue
        if hasattr(res, 'extra') and 'daily_activity' in res.extra:
            for d_str, count in res.extra['daily_activity'].items():
                unified_daily[d_str] = unified_daily.get(d_str, 0) + count
        if plat_key == "leetcode": raw = extract_raw_subscores_leetcode(res, config)
        elif plat_key == "codeforces": raw = extract_raw_subscores_codeforces(res, config)
        elif plat_key == "codechef": raw = extract_raw_subscores_codechef(res, config)
        elif plat_key == "hackerrank": raw = extract_raw_subscores_hackerrank(res, config)
        else: continue
        p_score, persona = apply_persona_weights(raw["clout"], raw["consistency"], raw["velocity"])
        scored_platforms[plat_key] = {
            "clout": raw["clout"],
            "consistency": raw["consistency"],
            "velocity": raw["velocity"],
            "total": p_score,
            "persona": persona,
            "solved_count": res.solved_count or 0
        }
    if not scored_platforms:
        return {"status": "failed", "error_log": "All scrapers failed", "final_score": 0}
    cp_indices = {}
    for p_name, p_data in scored_platforms.items():
        cp_val = math.log(p_data["solved_count"] + 1) * (p_data["clout"] / 100)
        cp_indices[p_name] = max(cp_val, 0.01)
    sum_cp = sum(cp_indices.values())
    dynamic_weights = {p: (idx / sum_cp) for p, idx in cp_indices.items()}
    base_final_score = sum(p_data["total"] * dynamic_weights[p_name] for p_name, p_data in scored_platforms.items())
    now = datetime.now(timezone.utc)
    timeline = []
    for i in range(365):
        d_str = (now - timeline.append(unified_daily.get((now - timedelta(days=i)).strftime("%Y-%m-%d"), 0))) if False else (now - timedelta(days=i)).strftime("%Y-%m-%d")
        timeline.append(unified_daily.get(d_str, 0))
    mu_global = sum(timeline) / 365
    if mu_global > 0 and len(scored_platforms) > 1:
        sigma_global = math.sqrt(sum((x - mu_global)**2 for x in timeline) / 365)
        g_cons = max(0.0, 100.0 * (1.0 - ((sigma_global / (mu_global + 1e-9)) / 10.0)))
        raw_m = 1.15 / (1.0 + math.exp(-0.08 * (g_cons - 45.0)))
        m_global = max(0.9, raw_m)
    else:
        g_cons = 0.0
        m_global = 1.0
    final_cp_score = clamp(base_final_score * m_global)
    return {
        "agent": "cp",
        "status": "success",
        "final_score": round(final_cp_score, 2),
        "sub_scores": scored_platforms,
        "narrative_context": {
            "platforms_evaluated": list(scored_platforms.keys()),
            "aggregation_method": f"Dynamic Persona Allocation ({len(scored_platforms)} platforms)",
            "sigmoidal_multiplier": round(m_global, 3),
            "platform_weights_applied": {k: round(v, 3) for k, v in dynamic_weights.items()}
        }
    }

def execute_cp_agent(platforms: dict, config: dict = None) -> dict:
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(async_execute(platforms, config or {}))
        loop.close()
        return result
    except Exception as e:
        return {
            "agent": "cp",
            "status": "failed",
            "error_log": f"CP Thread Error: {str(e)}",
            "final_score": 0
        }
