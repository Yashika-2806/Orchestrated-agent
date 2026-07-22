import math

def calculate_consistency_score(monthly_contributions: dict, epsilon: float = 1.0) -> dict:
    """
    Calculates the consistency score using the Coefficient of Variation (CV) model.
    Applies Base-2 Logarithmic dampening to prevent massive hackathon spikes 
    from destroying the variance calculation of an otherwise consistent developer.
    """
    if not monthly_contributions or "error" in monthly_contributions:
        return {"score": 0.0, "details": {"mu": 0.0, "sigma": 0.0, "total_commits": 0, "epsilon": epsilon}}

    commits = list(monthly_contributions.values())
    total_months = len(commits)
    raw_total_commits = sum(commits)
    
    if raw_total_commits == 0 or total_months == 0:
        return {"score": 0.0, "details": {"mu": 0.0, "sigma": 0.0, "total_commits": 0, "epsilon": epsilon}}

    # THE FIX: Apply Log-Dampening to the dataset before statistical analysis
    log_commits = [math.log2(c + 1) for c in commits]

    # Calculate Log-Mean (μ)
    log_mu = sum(log_commits) / total_months
    
    # Calculate Log-Variance and Log-Standard Deviation (σ)
    variance = sum((c - log_mu) ** 2 for c in log_commits) / total_months
    log_sigma = math.sqrt(variance)

    # Coefficient of Variation logic with Epsilon floor
    score = max(0.0, 100.0 * (1.0 - (log_sigma / (log_mu + epsilon))))

    return {
        "score": round(score, 2),
        "details": {
            "mu": round(log_mu, 2), # This is now the Log-Mean
            "sigma": round(log_sigma, 2), # This is now the Log-Deviation
            "total_commits": raw_total_commits,
            "epsilon": epsilon
        }
    }
def calculate_community_score(
    repositories: list, 
    sweet_spot_low: float = 0.15, 
    sweet_spot_high: float = 0.85, 
    points_per_collab: float = 20.0,
    partial_credit: float = 0.2,
    star_bonus: float = 2.0,
    fork_bonus: float = 5.0
) -> dict:
    """
    Calculates the community score, rewarding users who hit the 
    'Collaboration Sweet Spot' in shared repositories, with adjustable penalties and bonuses.
    """
    if not repositories:
        return {"score": 0.0, "details": {"engagement_sum": 0.0, "total_stars": 0, "total_forks": 0}}

    engagement_sum = 0.0
    total_stars = 0
    total_forks = 0

    for repo in repositories:
        total_stars += int(repo.get("stars", 0))
        total_forks += int(repo.get("forks", 0))
        
        deep_metrics = repo.get("deep_metrics", {})
        commits_data = deep_metrics.get("commits", {})
        
        user_ratio = commits_data.get("user_commit_ratio", 0.0)
        total_commits = commits_data.get("total_repo_commits", 0)
        user_commits = commits_data.get("user_commits_count", 0)

        # Identify shared repositories (where the user isn't the sole contributor)
        if total_commits > user_commits:
            if sweet_spot_low <= user_ratio <= sweet_spot_high:
                engagement_sum += 1.0  # Perfect engagement
            elif user_ratio > 0.0:
                engagement_sum += partial_credit  # Configurable partial credit

    # Base points from engagement, plus dampened dynamic bonuses for raw repo stars/forks
    log_stars = math.log10(total_stars + 1) if total_stars > 0 else 0
    log_forks = math.log10(total_forks + 1) if total_forks > 0 else 0
    score = (engagement_sum * points_per_collab) + (log_stars * star_bonus * 10.0) + (log_forks * fork_bonus * 10.0)
    
    return {
        "score": round(min(100.0, score), 2),
        "details": {
            "engagement_sum": round(engagement_sum, 2),
            "sweet_spot_low": sweet_spot_low,
            "sweet_spot_high": sweet_spot_high,
            "points_per_collab": points_per_collab,
            "partial_credit": partial_credit,
            "star_bonus": star_bonus,
            "fork_bonus": fork_bonus,
            "total_stars": total_stars,
            "total_forks": total_forks
        }
    }

def calculate_technology_score(
    technologies: dict, 
    alpha: float = 5.0, 
    beta: float = 3.0, 
    breadth_ceiling: float = 8.0
) -> dict:
    """
    Calculates the technology score balancing breadth and depth.
    Applies the breadth_ceiling to prevent gaming the system with high language counts.
    """
    if not technologies:
        return {"score": 0.0, "details": {"L": 0, "capped_L": 0, "log_sum": 0.0, "alpha": alpha, "beta": beta, "breadth_ceiling": breadth_ceiling}}

    L = len(technologies)
    capped_L = min(L, breadth_ceiling) 
    
    log_sum = sum(math.log2(count + 1) for count in technologies.values())
    
    score = min(100.0, (alpha * capped_L) + (beta * log_sum))

    return {
        "score": round(score, 2),
        "details": {
            "L": L,
            "capped_L": capped_L,
            "log_sum": round(log_sum, 2),
            "alpha": alpha,
            "beta": beta,
            "breadth_ceiling": breadth_ceiling
        }
    }

def calculate_advanced_score(forked_repositories: list, gamma: float = 10.0, adv_target: int = 3) -> dict:
    """
    Calculates open-source impact using Base-10 logarithms.
    Caps max points per repository based on adv_target and saves individual repo math.
    Includes defensive checks to prevent math domain errors from negative/missing API data.
    """
    if not forked_repositories or adv_target < 1:
        return {"score": 0.0, "details": {"active_forks": 0, "total_impact": 0.0, "gamma": gamma, "adv_target": adv_target, "max_per_repo": 100.0, "repo_breakdowns": []}}

    score = 0.0
    active_forks = 0
    total_impact = 0.0
    max_per_repo = 100.0 / adv_target
    
    repo_breakdowns = []

    for fork in forked_repositories:
        # DEFENSIVE CHECK 1: Ensure values are integers and fallback to 0 if None
        stars = int(fork.get("stars_count") or 0)
        forks = int(fork.get("forks_count") or 0)
        user_commits = int(fork.get("user_commits_count") or 0)
        repo_name = fork.get("name", "Unknown Repo")

        if user_commits > 0:
            active_forks += 1
            
            safe_log_input = max(1, stars + forks + 1)
            base_impact = math.log10(safe_log_input)
            
            # Dampen user commits to prevent infinite scaling
            dampened_commits = math.log2(user_commits + 1)
            raw_repo_score = gamma * base_impact * dampened_commits
            capped_repo_score = min(raw_repo_score, max_per_repo)
            
            total_impact += base_impact * dampened_commits
            score += capped_repo_score
            
            repo_breakdowns.append({
                "name": repo_name,
                "stars": stars if stars >= 0 else "Unknown (Deleted/Private)",
                "forks": forks if forks >= 0 else 0,
                "commits": user_commits,
                "dampened_commits": round(dampened_commits, 2),
                "base_impact": round(base_impact, 3),
                "raw_score": round(raw_repo_score, 2),
                "capped_score": round(capped_repo_score, 2)
            })

    return {
        "score": round(min(100.0, score), 2),
        "details": {
            "active_forks": active_forks,
            "total_impact": round(total_impact, 2),
            "gamma": gamma,
            "adv_target": adv_target,
            "max_per_repo": round(max_per_repo, 2),
            "repo_breakdowns": repo_breakdowns
        }
    }

def calculate_management_score(
    profile: dict, 
    target_ratio: float = 0.75, 
    bio_bonus: float = 10.0, 
    name_bonus: float = 5.0
) -> dict:
    """
    Calculates the management score based on profile completeness and README presence.
    Dynamically adjusts based on strict UI bonus values.
    """
    readme_ratio = profile.get("readme_ratio", 0.0)
    has_bio = bool(profile.get("bio"))
    has_name = bool(profile.get("name"))

    # Safe division check in case the user forces the slider to 0.0
    safe_target = target_ratio if target_ratio > 0 else 0.01

    readme_max_points = 100.0 - bio_bonus - name_bonus
    readme_score = min(1.0, readme_ratio / safe_target) * readme_max_points
    
    bio_score = bio_bonus if has_bio else 0.0
    name_score = name_bonus if has_name else 0.0

    return {
        "score": round(min(100.0, readme_score + bio_score + name_score), 2),
        "details": {
            "readme_ratio": readme_ratio,
            "target_ratio": target_ratio,
            "has_bio": has_bio,
            "has_name": has_name,
            "bio_bonus": bio_bonus,
            "name_bonus": name_bonus
        }
    }

def calculate_final_score(scores: dict, weights: dict) -> dict:
    """
    Generates the final weighted score based on the individual module scores 
    and the normalized weights applied from the UI.
    """
    final_score = 0.0
    for category, module_data in scores.items():
        weight = float(weights.get(category, 0.0))
        final_score += module_data["score"] * weight
        
    return {
        "score": round(final_score, 2),
        "details": {
            "applied_weights": weights,
            "components": {k: v["score"] for k, v in scores.items()}
        }
    }


def calculate_ast_complexity(repositories: list) -> dict:
    """
    [AST Code Complexity Analysis — Anti-Gamification Upgrade]
    Parses code constructs to measure Cyclomatic Complexity & Maintainability Index.
    Flags low-complexity gamified repositories (e.g. 50 single-line typo commits).
    """
    import ast

    total_ast_nodes = 0
    cyclomatic_complexity_sum = 0
    function_count = 0
    evaluated_repos = 0
    gamification_flags = []

    for repo in repositories:
        name = repo.get("name", "Unknown")
        commits_data = repo.get("deep_metrics", {}).get("commits", {})
        user_commits = commits_data.get("user_commits_count", 0)

        # Sample code text or description AST structure if available
        sample_code = repo.get("sample_code_snippet") or "def main():\n    pass\n"

        try:
            tree = ast.parse(sample_code)
            nodes = list(ast.walk(tree))
            total_ast_nodes += len(nodes)

            repo_complexity = 1
            for node in nodes:
                if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.ExceptHandler, ast.With)):
                    repo_complexity += 1
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    function_count += 1

            cyclomatic_complexity_sum += repo_complexity
            evaluated_repos += 1

            # Anti-gamification check: high commits but trivial AST complexity
            if user_commits > 30 and repo_complexity <= 2:
                gamification_flags.append({
                    "repo": name,
                    "user_commits": user_commits,
                    "cyclomatic_complexity": repo_complexity,
                    "reason": "High commit count with trivial AST code complexity (Gamification Warning)"
                })

        except SyntaxError:
            continue

    avg_complexity = round(cyclomatic_complexity_sum / max(1, evaluated_repos), 2)
    maintainability_index = min(100.0, max(0.0, 100.0 - (avg_complexity * 3.5)))

    return {
        "avg_cyclomatic_complexity": avg_complexity,
        "maintainability_index": round(maintainability_index, 2),
        "total_functions_analyzed": function_count,
        "gamification_flags_count": len(gamification_flags),
        "gamification_warnings": gamification_flags
    }


def verify_academic_dsa_consistency(academic_gpa: float, dsa_score: float, repositories: list) -> dict:
    """
    [Curriculum / DSA Cross-Verification]
    Cross-verifies candidate's academic DSA score against actual GitHub repository implementations.
    Flags a warning if a candidate scores >80% in academic DSA but has 0 algorithm/DSA repos.
    """
    dsa_keywords = ["dsa", "algorithm", "data-structure", "leetcode", "codeforces", "competitive-programming", "cpp", "c++", "trees", "graphs"]

    has_dsa_repo = False
    matched_repos = []

    for repo in repositories:
        name = (repo.get("name") or "").lower()
        desc = (repo.get("description") or "").lower()
        lang = (repo.get("primary_language") or "").lower()

        if any(kw in name or kw in desc or kw in lang for kw in dsa_keywords):
            has_dsa_repo = True
            matched_repos.append(repo.get("name"))

    academic_threshold_met = (dsa_score >= 80.0) or (academic_gpa >= 8.0)
    low_practical_consistency = academic_threshold_met and not has_dsa_repo

    return {
        "academic_gpa": academic_gpa,
        "dsa_academic_score": dsa_score,
        "has_dsa_repo_proof": has_dsa_repo,
        "matched_dsa_repos": matched_repos,
        "low_practical_consistency_warning": low_practical_consistency,
        "warning_message": (
            "WARNING: Candidate scored high in academic DSA/GPA but has ZERO algorithm/DSA repositories on GitHub."
            if low_practical_consistency else "Academic and GitHub DSA consistency verified."
        )
    }