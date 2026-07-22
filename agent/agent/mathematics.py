import math

def calculate_consistency_score(monthly_contributions, epsilon=1.0):
    if not monthly_contributions:
        return {"score": 0.0, "details": "No monthly contribution data found"}
    commits = [float(v) for v in monthly_contributions.values()]
    if not commits:
        return {"score": 0.0, "details": "No commits found"}
    avg = sum(commits) / len(commits)
    variance = sum((x - avg) ** 2 for x in commits) / len(commits)
    std_dev = variance ** 0.5
    cv = std_dev / (avg + epsilon)
    score = max(0.0, min(100.0, 100.0 * (1.0 - cv / 2.0)))
    return {"score": round(score, 2), "details": f"Avg commits: {avg:.2f}, Std Dev: {std_dev:.2f}"}

def calculate_community_score(repositories, sweet_spot_low=0.15, sweet_spot_high=0.85, points_per_collab=20.0, partial_credit=0.2, star_bonus=2.0, fork_bonus=5.0):
    if not repositories:
        return {"score": 0.0, "details": "No repositories found"}
    total_score = 0.0
    for repo in repositories:
        stars = repo.get("stars", 0) or 0
        forks = repo.get("forks", 0) or 0
        contributors = repo.get("deep_metrics", {}).get("contributors", [])
        collab_count = len(contributors)
        total_score += stars * star_bonus + forks * fork_bonus
        if collab_count > 1:
            ratio = repo.get("deep_metrics", {}).get("commits", {}).get("user_commit_ratio", 1.0)
            if sweet_spot_low <= ratio <= sweet_spot_high:
                total_score += points_per_collab
            else:
                total_score += points_per_collab * partial_credit
    score = max(0.0, min(100.0, total_score))
    return {"score": round(score, 2), "details": f"Total community points: {total_score:.2f}"}

def calculate_technology_score(technologies, alpha=5.0, beta=3.0, breadth_ceiling=8.0):
    if not technologies:
        return {"score": 0.0, "details": "No technologies used"}
    depth = max(technologies.values()) if technologies else 0
    breadth = min(len(technologies), breadth_ceiling)
    score = alpha * math.log(depth + 1) + beta * breadth
    score = max(0.0, min(100.0, score * 5))
    return {"score": round(score, 2), "details": f"Depth: {depth}, Breadth: {breadth}"}

def calculate_advanced_score(forked_repositories, gamma=10.0, adv_target=3):
    if not forked_repositories:
        return {"score": 0.0, "details": "No open source contribution (forks) found"}
    count = len(forked_repositories)
    score = min(count, adv_target) * gamma
    commit_bonus = sum(repo.get("user_commits_count", 0) for repo in forked_repositories) * 2.0
    score = max(0.0, min(100.0, score + commit_bonus))
    return {"score": round(score, 2), "details": f"Forks count: {count}, commit bonus: {commit_bonus}"}

def calculate_management_score(profile, target_ratio=0.75, bio_bonus=10.0, name_bonus=5.0):
    readme_ratio = profile.get("readme_ratio", 0.0) or 0.0
    score = (readme_ratio / target_ratio) * 80.0 if target_ratio > 0 else 80.0
    if profile.get("bio"):
        score += bio_bonus
    if profile.get("name"):
        score += name_bonus
    score = max(0.0, min(100.0, score))
    return {"score": round(score, 2), "details": f"Readme Ratio: {readme_ratio:.2f}"}

def calculate_final_score(scores_payload, weights):
    score = 0.0
    details = []
    for key, weight in weights.items():
        sub_score = scores_payload.get(key, {}).get("score", 0.0)
        score += sub_score * weight
        details.append(f"{key}: {sub_score:.1f}")
    return {"score": round(score, 2), "details": "; ".join(details)}
