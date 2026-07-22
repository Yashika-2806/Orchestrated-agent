import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Cpu, FileText, GitBranch, Code2, BarChart3, Sigma, FlaskConical } from 'lucide-react';

/* ────────────────────────────────────────────────────────────────────────────
   TYPES
──────────────────────────────────────────────────────────────────────────── */
interface Section {
  id: string;
  title: string;
  subtitle: string;
  icon: React.ReactNode;
  color: string;
  content: React.ReactNode;
}

/* ────────────────────────────────────────────────────────────────────────────
   HELPERS
──────────────────────────────────────────────────────────────────────────── */
const Formula: React.FC<{ label: string; formula: string; note?: string }> = ({ label, formula, note }) => (
  <div style={{
    background: 'rgba(99,102,241,0.06)',
    border: '1px solid rgba(99,102,241,0.18)',
    borderRadius: 10,
    padding: '14px 18px',
    marginBottom: 10,
  }}>
    <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 6 }}>{label}</div>
    <code style={{
      display: 'block',
      fontFamily: '"JetBrains Mono", "Fira Code", monospace',
      fontSize: '0.82rem',
      color: 'var(--color-primary)',
      lineHeight: 1.8,
      whiteSpace: 'pre-wrap',
      wordBreak: 'break-word',
    }}>{formula}</code>
    {note && <div style={{ marginTop: 8, fontSize: '0.72rem', color: 'var(--text-dim)', lineHeight: 1.5, borderTop: '1px solid rgba(99,102,241,0.1)', paddingTop: 8 }}>💡 {note}</div>}
  </div>
);

const WeightTable: React.FC<{ rows: { param: string; weight: string; description: string }[] }> = ({ rows }) => (
  <div style={{ overflowX: 'auto', marginBottom: 12 }}>
    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.78rem' }}>
      <thead>
        <tr style={{ background: 'rgba(99,102,241,0.08)' }}>
          {['Parameter', 'Weight / Value', 'Description'].map(h => (
            <th key={h} style={{ padding: '8px 12px', textAlign: 'left', color: 'var(--text-dim)', fontWeight: 700, borderBottom: '1px solid var(--border-color)', whiteSpace: 'nowrap' }}>{h}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((r, i) => (
          <tr key={i} style={{ borderBottom: '1px solid rgba(99,102,241,0.06)', transition: 'background 0.15s' }}
            onMouseEnter={e => (e.currentTarget.style.background = 'rgba(99,102,241,0.04)')}
            onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
          >
            <td style={{ padding: '8px 12px', fontFamily: '"JetBrains Mono","Fira Code",monospace', color: 'var(--color-primary)', fontWeight: 600 }}>{r.param}</td>
            <td style={{ padding: '8px 12px', color: 'var(--color-warning, #f59e0b)', fontWeight: 700 }}>{r.weight}</td>
            <td style={{ padding: '8px 12px', color: 'var(--text-dim)' }}>{r.description}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

const Badge: React.FC<{ text: string; color?: string }> = ({ text, color = '#6366f1' }) => (
  <span style={{
    display: 'inline-block',
    background: `${color}22`,
    color,
    border: `1px solid ${color}44`,
    borderRadius: 6,
    padding: '2px 8px',
    fontSize: '0.65rem',
    fontWeight: 700,
    letterSpacing: '0.04em',
    marginRight: 4,
  }}>{text}</span>
);

const Divider = () => <div style={{ height: 1, background: 'var(--border-color)', margin: '18px 0', opacity: 0.5 }} />;

const SectionHeader: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-main)', margin: '16px 0 10px', display: 'flex', alignItems: 'center', gap: 6 }}>
    {children}
  </h4>
);

/* ────────────────────────────────────────────────────────────────────────────
   SECTION CONTENT
──────────────────────────────────────────────────────────────────────────── */



const MasterScoreContent = () => (
  <div>
    <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: 16, lineHeight: 1.6 }}>
      The <strong>Master Score</strong> is the top-level composite score (0–100). It is computed in the backend using a
      <em> flat weighted sum</em> of independent components. Each agent (Resume, GitHub, CP) computes its score independently, and academic inputs are normalized to 0-100 before weighting.
    </p>

    <SectionHeader>⚖️ Component Weights</SectionHeader>
    <WeightTable rows={[
      { param: 'CPI (GPA)', weight: '20%', description: 'Normalized: (CPI ÷ 10) × 100' },
      { param: 'DSA Marks', weight: '18%', description: 'Normalized: min(100, marks)' },
      { param: 'English Marks', weight: '17%', description: 'Normalized: min(100, marks)' },
      { param: 'Internships', weight: '15%', description: 'Normalized: min(100, count × 25)' },
      { param: 'GitHub Score', weight: '15%', description: 'Open source & codebase contribution' },
      { param: 'Resume Score', weight: '9%', description: 'Base professional representation' },
      { param: 'CP Score', weight: '3%', description: 'Algorithmic problem solving clout' },
      { param: 'Backlogs', weight: '3%', description: 'Normalized: max(0, 100 − count × 25)' },
      { param: 'Attendance', weight: '0%', description: 'Raw percentage' },
    ]} />

    <Formula
      label="Master Score Formula (server.py)"
      formula={
`numerator = (
  norm_cpi          × 20 +
  norm_dsa          × 18 +
  norm_english      × 17 +
  norm_internships  × 15 +
  github_score      × 15 +
  resume_score      × 9  +
  cp_score          × 3  +
  norm_backlogs     × 3  +
  norm_attendance   × 0
)

total_weight = 20 + 18 + 17 + 15 + 15 + 9 + 3 + 3 + 0

master_score = clamp(numerator / total_weight, 0, 100)`}
      note="The total_weight is always the sum of all configured weights (100 in this case). If a student has no GitHub profile, their github_score is 0, but the weight of 15 remains in the denominator."
    />

    <SectionHeader>📊 Confidence Level</SectionHeader>
    <WeightTable rows={[
      { param: '≥ 4 non-zero components', weight: '"High" Confidence', description: 'Strong profile evidence' },
      { param: '2–3 non-zero components', weight: '"Medium" Confidence', description: 'Partial profile evidence' },
      { param: '< 2 non-zero components', weight: '"Low" Confidence', description: 'Insufficient data' },
    ]} />
  </div>
);
const ResumeScoreContent = () => (
  <div>
    <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: 16, lineHeight: 1.6 }}>
      The Resume Agent extracts structured data via GPT-4o and computes 8 weighted sub-scores.
      Weights shift based on B.Tech year (Year 2 / 3 / 4) to reflect what matters most at each stage.
    </p>

    <SectionHeader>⚖️ Sub-Score Weights by B.Tech Year</SectionHeader>
    <WeightTable rows={[
      { param: 'S_hygiene (Format / Links)', weight: 'Y2: 25% | Y3: 15% | Y4: 5%', description: 'Page count, missing sections, links, generic email' },
      { param: 'S_realization (Skills Used)', weight: 'Y2: 25% | Y3: 20% | Y4: 10%', description: 'How many declared skills actually appear in projects' },
      { param: 'S_complexity (Project Tier)', weight: 'Y2: 20% | Y3: 25% | Y4: 30%', description: 'Project architectural sophistication (T3/T2/T1 tech)' },
      { param: 'S_impact (STAR Impact)', weight: 'Y2: 5% | Y3: 10% | Y4: 20%', description: 'Qualitative impact score via GPT-4o (0–100)' },
      { param: 'S_production (Live/Repo)', weight: 'Y2: 10% | Y3: 15% | Y4: 15%', description: 'Fraction of projects with code repo or live deployment' },
      { param: 'S_clarity (Buzzword penalty)', weight: 'Y2: 5% | Y3: 5% | Y4: 5%', description: 'Penalises buzzwords like "passionate", "dynamic", etc.' },
      { param: 'S_domain (Focus)', weight: 'Y2: 5% | Y3: 5% | Y4: 5%', description: 'Penalises >1 domain: each extra domain deducts 20 pts' },
      { param: 'S_velocity (Experience)', weight: 'Y2: 5% | Y3: 5% | Y4: 10%', description: 'Internships/roles weighted by type × months' },
    ]} />

    <Divider />
    <SectionHeader>📐 Individual Sub-Score Formulas</SectionHeader>

    <Formula
      label="S_hygiene — Resume Hygiene"
      formula={
`S_hygiene = max(0,
  100
  − pen_page  × max(0, pages − 1)      # 50 pts per extra page
  − pen_link  × missing_links          # 15 pts per missing link (GitHub/LinkedIn)
  − pen_email × generic_email_flag     # 25 pts if email has "cool/coder/gamer/..."
  − pen_sec   × missing_sections       # 20 pts per missing mandatory section
)`}
      note="Mandatory sections = {Education, Projects, Skills}. Optimal resume = 1 page, has GitHub+LinkedIn, professional email, all sections present."
    />

    <Formula
      label="S_realization — Skill Realization"
      formula={
`for each skill k in declared_skills:
  skill_weight(k) = log(difficulty(k) + 1)
    where difficulty: Tier3 (Docker/K8s/Kafka/AWS...) = 10
                      Tier2 (Python/React/SQL/Java...) = 5
                      Other                            = 2

S_realization = (Σ skill_weight(k) for k in declared ∩ applied_in_text + ε)
              / (Σ skill_weight(k) for k in declared + ε)   × 100`}
      note="'applied_in_text' = skills that appear verbatim in the Projects or Experience text corpus. Epsilon=1.0 prevents division by zero."
    />

    <Formula
      label="S_complexity — Project Complexity"
      formula={
`for each project j:
  tier(j) = 100  if uses arch keywords (WebSockets/Kafka/Docker/K8s/Redis/CI-CD/gRPC...)
           = 100  if uses any Tier3 tech keyword
           = 65   if has_backend AND has_database
           = 25   otherwise

S_complexity = min(100, max(tier) + α × log(J + 1))
  where α = 5.0, J = total project count`}
      note="Rewards projects with advanced architecture. The log bonus rewards having multiple projects without overinflating."
    />

    <Formula
      label="S_impact — STAR Qualitative Impact"
      formula={`S_impact = clamp(GPT-4o_STAR_score, 0, 100)
# GPT-4o rates the overall impact of projects & experience on 0–100 STAR scale`}
    />

    <Formula
      label="S_production — Live Evidence"
      formula={
`J_total = max(project_count, 1)
J_code  = count of GitHub/GitLab repo URLs found
J_deploy = count of live deployment URLs (Vercel/Netlify/Heroku/AWS/custom domain)

S_production = min(100, ((J_code + J_deploy) / (2 × J_total)) × 100)`}
    />

    <Formula
      label="S_clarity — Buzzword Penalty"
      formula={
`buzzwords = ["passionate","detail-oriented","synergy","motivated","hardworking",
              "team player","go-getter","self-starter","results-driven",
              "dynamic","innovative","proactive"]

S_clarity = max(0, 100 − ω × Σ log(count_i + 1))
  where ω = 15.0`}
    />

    <Formula
      label="S_domain — Domain Focus"
      formula={
`unique_domains = count of distinct domains in domain_classification_vector

S_domain = max(0, 100 − max(0, unique_domains − 1) × 20)`}
      note="One domain = 100. Two domains = 80. Three = 60. Rewards specialization."
    />

    <Formula
      label="S_velocity — Experience Velocity"
      formula={
`velocity_sum = Σ (months × role_weight) for each experience entry
  role_weights: internship=10, tech_lead=8, freelance=5, member=3

S_velocity = min(100, log₂(velocity_sum + 1) × 20)`}
    />

    <Divider />
    <Formula
      label="Final Resume Score"
      formula={
`resume_score = clamp(
  W_hyg  × S_hygiene     +
  W_real × S_realization +
  W_comp × S_complexity  +
  W_imp  × S_impact      +
  W_prod × S_production  +
  W_clar × S_clarity     +
  W_dom  × S_domain      +
  W_vel  × S_velocity
, 0, 100)`}
    />
  </div>
);

const GitHubScoreContent = () => (
  <div>
    <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: 16, lineHeight: 1.6 }}>
      The GitHub Agent scrapes the public profile via GitHub's REST/GraphQL API and computes 5 sub-scores.
      It also uses GPT-4o to extract the primary career domain from repository contents.
    </p>

    <SectionHeader>⚖️ Default GitHub Sub-Score Weights</SectionHeader>
    <WeightTable rows={[
      { param: 'consistency', weight: '20%', description: 'Regularity of monthly commit activity (low CV = high score)' },
      { param: 'community', weight: '30%', description: 'Stars, forks, collaborator ratio across repos' },
      { param: 'technology', weight: '25%', description: 'Depth + breadth of languages/tech used' },
      { param: 'management', weight: '15%', description: 'README coverage, bio, profile completeness' },
      { param: 'advanced', weight: '10%', description: 'Open-source fork contributions + commit volume' },
    ]} />

    <Divider />
    <Formula
      label="Consistency Score"
      formula={
`commits = monthly contribution counts (last 12 months)
avg = mean(commits)
std_dev = sqrt(variance(commits))
CV = std_dev / (avg + ε)          # Coefficient of Variation; ε=1.0

consistency_score = clamp(100 × (1 − CV / 2))`}
      note="Lower coefficient of variation = more consistent. A perfectly regular contributor scores near 100."
    />

    <Formula
      label="Community Score"
      formula={
`for each repo:
  points += stars × 2.0 + forks × 5.0
  if collab_count > 1:
    if 0.15 ≤ user_commit_ratio ≤ 0.85:
      points += 20.0   # sweet-spot collaboration
    else:
      points += 4.0    # partial credit

community_score = clamp(total_points, 0, 100)`}
    />

    <Formula
      label="Technology Score"
      formula={
`depth   = max usage count among all languages
breadth = min(distinct language count, 8)   # ceiling = 8

tech_score = clamp((α×log(depth+1) + β×breadth) × 5)
  where α=5.0, β=3.0`}
    />

    <Formula
      label="Advanced Score (Open Source)"
      formula={
`forked_repos = repos forked from other owners with user commits

adv_score = clamp(
  min(fork_count, adv_target) × γ
  + Σ user_commits_per_fork × 2.0
, 0, 100)
  where γ=10.0, adv_target=3`}
    />

    <Formula
      label="Management Score"
      formula={
`readme_ratio = repos with README / total repos

mgmt_score = clamp(
  (readme_ratio / 0.75) × 80
  + (10 if bio present)
  + (5  if display name set)
, 0, 100)`}
    />

    <Divider />
    <Formula
      label="Final GitHub Score"
      formula={
`github_score = consistency×0.20 + community×0.30 + technology×0.25
             + management×0.15  + advanced×0.10`}
    />
  </div>
);

const CPScoreContent = () => (
  <div>
    <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: 16, lineHeight: 1.6 }}>
      The CP Agent scrapes up to 4 platforms (LeetCode, Codeforces, CodeChef, HackerRank).
      Each platform yields <strong>Clout</strong>, <strong>Consistency</strong>, and <strong>Velocity</strong> sub-scores.
      A <em>Dynamic Persona</em> blends them; a <em>sigmoidal multi-platform multiplier</em> rewards cross-platform activity.
    </p>

    <SectionHeader>🎭 Persona Blending (per platform)</SectionHeader>
    <WeightTable rows={[
      { param: 'Contest Hunter', weight: 'Clout×0.60 + Cons×0.20 + Vel×0.20', description: 'Triggered when clout≥75 AND consistency≥60' },
      { param: 'Streak Maker', weight: 'Clout×0.20 + Cons×0.60 + Vel×0.20', description: 'Triggered when clout<40 AND consistency≥75' },
      { param: 'Balanced Developer', weight: 'Clout×0.40 + Cons×0.40 + Vel×0.20', description: 'Default for all other profiles' },
    ]} />

    <Divider />
    <SectionHeader>📐 Platform Sub-Score Formulas</SectionHeader>

    <Formula
      label="LeetCode — Clout"
      formula={
`clout_rating = clamp((contest_rating / 2000) × 50)
clout_hard   = clamp((hard_solved / 15) × 20)
lc_clout     = clamp(clout_rating + clout_hard)`}
    />
    <Formula
      label="LeetCode — Consistency"
      formula={`active_days_90 = count of days with any submission in last 90 days
lc_consistency = clamp(active_days_90 / 30 × 100)`}
    />
    <Formula
      label="LeetCode — Velocity"
      formula={
`accept_rate  = total_accepted / total_attempted
vel_acceptance = clamp(accept_rate × 60)
vel_volume     = clamp((solved_count / 150) × 40)
lc_velocity    = clamp(vel_acceptance + vel_volume)`}
    />

    <Divider />
    <Formula
      label="Codeforces — Clout"
      formula={`cf_clout = clamp(max_rating / 1800 × 100)`}
    />
    <Formula
      label="Codeforces — Consistency"
      formula={
`IF contests_last_90 > 0:
  cf_consistency = clamp(contests_last_90 / 3 × 100)
ELSE:
  active_days_90 = active submission days in last 90 days
  cf_consistency = clamp(active_days_90 / 8 × 100)`}
    />
    <Formula
      label="Codeforces — Velocity"
      formula={`cf_velocity = clamp(100 − (wrong_during_contest / total_contests) × 5)`}
    />

    <Divider />
    <Formula
      label="CodeChef — Clout"
      formula={`cc_clout = clamp(stars / 5 × 60 + rating / 1800 × 40)`}
    />
    <Formula
      label="CodeChef — Consistency"
      formula={`cc_consistency = clamp(solved_count / 100 × 100)`}
    />
    <Formula
      label="CodeChef — Velocity"
      formula={`full_ratio = fully_solved / (fully_solved + partially_solved)
cc_velocity = clamp(full_ratio × 100)`}
    />

    <Divider />
    <Formula
      label="HackerRank — Clout"
      formula={`hr_clout = clamp(sum(badge_stars) / 6 × 100)`}
    />
    <Formula
      label="HackerRank — Consistency"
      formula={`hr_consistency = clamp((total_score / account_age_days) × 15.0)`}
    />
    <Formula
      label="HackerRank — Velocity"
      formula={`hr_velocity = clamp(perfect_challenges / 10 × 100)`}
    />

    <Divider />
    <SectionHeader>🔗 Multi-Platform Aggregation</SectionHeader>
    <Formula
      label="Step 1 — Dynamic Platform Weights (CP Index)"
      formula={
`for each platform p:
  cp_index(p) = log(solved_count + 1) × (clout / 100)

dynamic_weight(p) = cp_index(p) / Σ cp_index(all platforms)

base_cp_score = Σ platform_score(p) × dynamic_weight(p)`}
      note="Platforms where the student has solved more problems AND has higher clout get a larger dynamic weight."
    />
    <Formula
      label="Step 2 — Sigmoidal Global Consistency Multiplier (multi-platform only)"
      formula={
`unified_daily = merged daily activity across all platforms (365 days)
μ_global     = mean(daily_activity)
σ_global     = std_dev(daily_activity)
g_cons       = max(0, 100 × (1 − (σ/μ) / 10))

raw_m   = 1.15 / (1 + exp(−0.08 × (g_cons − 45)))
m_global = max(0.9, raw_m)           # floor = 0.9, ceiling ≈ 1.15

final_cp_score = clamp(base_cp_score × m_global)`}
      note="This multiplier only applies when 2+ platforms are provided. A highly consistent cross-platform user gets up to 15% bonus."
    />
  </div>
);

const ForecastContent = () => (
  <div>
    <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: 16, lineHeight: 1.6 }}>
      The Forecasting Agent uses the <strong>master_score</strong> and semantic profile to predict placement probability,
      salary band, and career readiness. If an OpenAI key is set, GPT-4o generates the forecast;
      otherwise a <em>deterministic benchmark lookup</em> is used.
    </p>

    <SectionHeader>📈 Placement Probability (Deterministic / Benchmark Tiers)</SectionHeader>
    <WeightTable rows={[
      { param: 'master_score < 40', weight: '~10%', description: '"Critical Gap" tier — high-risk' },
      { param: '40 ≤ score < 60', weight: '~35–50%', description: '"Developing" tier — needs improvement' },
      { param: '60 ≤ score < 80', weight: '~60–75%', description: '"Market Ready" tier — competitive' },
      { param: 'score ≥ 80', weight: '~85–99%', description: '"Premium" tier — highly competitive' },
    ]} />

    <Formula
      label="Career Readiness Mapping"
      formula={
`master_score ≥ 80  →  "Highly Competitive"
master_score ≥ 60  →  "Market Ready"
master_score ≥ 40  →  "Needs Development"
master_score  < 40 →  "Not Ready"`}
    />

    <Formula
      label="Salary Band Mapping (Historical Benchmarks)"
      formula={
`master_score < 40  →  Entry Level   (3.0 – 5.0 LPA)
master_score < 60  →  Mid Tier      (5.0 – 8.0 LPA)
master_score < 80  →  High Tier     (8.0 – 14.0 LPA)
master_score ≥ 80  →  Premium Tier  (14.0 – 25.0 LPA)

Domain-specific bands override these defaults based on benchmarks.json
For LLM-driven mode, Mini-RAG injects these exact bounds for the agent to refine.`}
    />

    <Formula
      label="Fallback Salary Simulation (Sandbox Mode / Missing API Key)"
      formula={
`min_lpa = round(3.5 + (master_score - 40) * 0.2, 1)
max_lpa = round(min_lpa + 4.5, 1)

Example (Master Score = 65):
min_lpa = 3.5 + (65 - 40) * 0.2 = 3.5 + 5.0 = 8.5 LPA
max_lpa = 8.5 + 4.5 = 13.0 LPA
`}
      note="Used strictly when running without OpenAI keys in deterministic mode or fallback endpoints."
    />

    <Divider />
    <SectionHeader>🔬 Backtesting Validation</SectionHeader>
    <Formula
      label="Backtesting Alignment Check"
      formula={
`deviation = |predicted_probability − historical_observed_rate|

alignment = "Strong Alignment"   if deviation ≤ 10
           "Moderate Alignment"  if deviation ≤ 20
           "Weak Alignment"      if deviation  > 20

# historical_observed_rate comes from backtesting_reference in benchmarks.json`}
    />
  </div>
);

const XAIContent = () => (
  <div>
    <p style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: 16, lineHeight: 1.6 }}>
      The <strong>XAI (Explainable AI) Attribution</strong> layer runs purely in the backend (<code>server.py</code>)
      on top of the final result. It assigns a <em>signed impact score</em> to each input feature to explain
      what drove the final prediction up or down.
    </p>

    <SectionHeader>📊 XAI Feature Impacts</SectionHeader>
    <WeightTable rows={[
      { param: 'CPI ≥ 8.5', weight: '+25 pts', description: 'Exceptional GPA — top shortlisting bracket' },
      { param: 'CPI 7.5–8.4', weight: '+12 pts', description: 'Solid GPA — satisfies most shortlists' },
      { param: 'CPI 6.0–7.4', weight: '+2 pts', description: 'Standard — neutral impact' },
      { param: 'CPI < 6.0', weight: '−18 pts', description: 'Below average — negative shortlisting impact' },
      { param: 'Backlogs = 0', weight: '+8 pts', description: 'No backlogs — meets corporate hiring criteria' },
      { param: 'Backlogs ≥ 1', weight: '−12 × N pts', description: 'N active backlogs — triggers eligibility blocks' },
      { param: 'DSA ≥ 85%', weight: '+20 pts', description: 'Strong algorithmic competence' },
      { param: 'DSA 70–84%', weight: '+8 pts', description: 'Meets competence baseline' },
      { param: 'DSA 50–69%', weight: '0 pts', description: 'Baseline — neutral' },
      { param: 'DSA < 50%', weight: '−15 pts', description: 'Potential coding test barrier' },
      { param: 'Attendance ≥ 85%', weight: '+10 pts', description: 'Strong academic consistency' },
      { param: 'Attendance 75–84%', weight: '0 pts', description: 'Meets GLA shortlisting rules' },
      { param: 'Attendance < 75%', weight: '−20 pts', description: 'Critically low — triggers restrictions' },
      { param: 'Internships ≥ 1', weight: '+15 pts', description: 'Improves practical industry readiness' },
      { param: 'Internships = 0', weight: '−5 pts', description: 'Gap in practical exposure' },
      { param: 'GitHub score ≥ 75', weight: '+20 pts', description: 'Active, validated commit history' },
      { param: 'GitHub score 45–74', weight: '+10 pts', description: 'Steady codebase exposure' },
      { param: 'GitHub score > 0 (low)', weight: '+2 pts', description: 'Entry-level activity' },
      { param: 'GitHub score = 0 (profile linked)', weight: '−10 pts', description: 'No commits found' },
      { param: 'CP score ≥ 75', weight: '+22 pts', description: 'Advanced algorithmic problem-solving' },
      { param: 'CP score 45–74', weight: '+10 pts', description: 'Consistent coding practice' },
      { param: 'CP score > 0 (low)', weight: '+2 pts', description: 'Basic coding exposure' },
      { param: 'CP score = 0 (profile linked)', weight: '−10 pts', description: 'No platform activity found' },
    ]} />
    <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginTop: 8 }}>
      <Badge text="NOTE" color="#f59e0b" /> If GitHub score is low but CP score ≥ 60, the GitHub penalty is waived (and vice versa).
      This prevents double-penalising students who are strong on one coding platform.
    </div>
  </div>
);

/* ────────────────────────────────────────────────────────────────────────────
   EXPANDABLE CARD
──────────────────────────────────────────────────────────────────────────── */
const ExpandableSection: React.FC<{ section: Section }> = ({ section }) => {
  const [open, setOpen] = useState(false);

  return (
    <div style={{
      border: `1px solid ${open ? section.color + '55' : 'var(--border-color)'}`,
      borderRadius: 14,
      overflow: 'hidden',
      transition: 'border-color 0.2s, box-shadow 0.2s',
      boxShadow: open ? `0 0 20px ${section.color}18` : 'none',
      marginBottom: 16,
    }}>
      {/* Header */}
      <button
        type="button"
        onClick={() => setOpen(!open)}
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          gap: 14,
          padding: '16px 20px',
          background: open ? `${section.color}10` : 'var(--card-bg, rgba(255,255,255,0.02))',
          border: 'none',
          cursor: 'pointer',
          textAlign: 'left',
          transition: 'background 0.2s',
        }}
      >
        <div style={{
          width: 40, height: 40,
          borderRadius: 10,
          background: `${section.color}18`,
          border: `1px solid ${section.color}33`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: section.color,
          flexShrink: 0,
        }}>
          {section.icon}
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-main)' }}>{section.title}</div>
          <div style={{ fontSize: '0.73rem', color: 'var(--text-dim)', marginTop: 2 }}>{section.subtitle}</div>
        </div>
        <div style={{ color: 'var(--text-dim)', flexShrink: 0 }}>
          {open ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
        </div>
      </button>

      {/* Body */}
      {open && (
        <div style={{ padding: '20px 24px', borderTop: `1px solid ${section.color}22`, background: 'var(--card-bg, rgba(255,255,255,0.01))' }}>
          {section.content}
        </div>
      )}
    </div>
  );
};

/* ────────────────────────────────────────────────────────────────────────────
   MAIN COMPONENT
──────────────────────────────────────────────────────────────────────────── */
export const FormulaEngine: React.FC = () => {
  const sections: Section[] = [
    {
      id: 'master',
      title: 'Master Score  ·  Orchestrator',
      subtitle: 'Top-level composite score · Dynamic weighting by profile completeness · file: orchestrator.py',
      icon: <Cpu size={18} />,
      color: '#6366f1',
      content: <MasterScoreContent />,
    },
    {
      id: 'resume',
      title: 'Resume Agent Score',
      subtitle: '8 weighted sub-scores · Year-adaptive weights · GPT-4o extraction · file: resugent/utils.py',
      icon: <FileText size={18} />,
      color: '#10b981',
      content: <ResumeScoreContent />,
    },
    {
      id: 'github',
      title: 'GitHub Agent Score',
      subtitle: '5 sub-scores · Consistency / Community / Technology / Management / Advanced · file: agent/mathematics.py',
      icon: <GitBranch size={18} />,
      color: '#f59e0b',
      content: <GitHubScoreContent />,
    },
    {
      id: 'cp',
      title: 'CP Agent Score  ·  LeetCode / Codeforces / CodeChef / HackerRank',
      subtitle: 'Persona-blended Clout + Consistency + Velocity · Sigmoidal multi-platform multiplier · file: cpgent/main.py',
      icon: <Code2 size={18} />,
      color: '#ec4899',
      content: <CPScoreContent />,
    },
    {
      id: 'forecast',
      title: 'Forecasting Agent',
      subtitle: 'Placement probability · Salary band mapping · Career readiness · Backtesting · file: forecasting_agent.py',
      icon: <BarChart3 size={18} />,
      color: '#8b5cf6',
      content: <ForecastContent />,
    },
    {
      id: 'xai',
      title: 'XAI Attribution Layer',
      subtitle: 'Signed feature impacts · Academic inputs (CPI, backlogs, DSA, attendance, internships) · file: server.py',
      icon: <FlaskConical size={18} />,
      color: '#06b6d4',
      content: <XAIContent />,
    },
  ];

  return (
    <div style={{ padding: '24px 0' }}>
      {/* Top banner */}
      <div style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: 16,
        padding: '20px 24px',
        background: 'rgba(99,102,241,0.06)',
        border: '1px solid rgba(99,102,241,0.2)',
        borderRadius: 14,
        marginBottom: 24,
      }}>
        <div style={{ color: '#6366f1', marginTop: 2 }}><Sigma size={28} /></div>
        <div>
          <div style={{ fontWeight: 800, fontSize: '1.05rem', color: 'var(--text-main)', marginBottom: 4 }}>
            Formula Engine  ·  Scoring Methodology Reference
          </div>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-dim)', margin: 0, lineHeight: 1.6, maxWidth: 720 }}>
            All formulas below are <strong>static</strong> and directly reflect the production code.
            Expand each section to inspect the exact equations, weights, and thresholds used to generate
            every score in the system. No simulation — these are the actual calculations.
          </p>
          <div style={{ marginTop: 10, display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            <Badge text="Resume Agent" color="#10b981" />
            <Badge text="GitHub Agent" color="#f59e0b" />
            <Badge text="CP Agent" color="#ec4899" />
            <Badge text="Orchestrator" color="#6366f1" />
            <Badge text="Forecasting" color="#8b5cf6" />
            <Badge text="XAI Attribution" color="#06b6d4" />
          </div>
        </div>
      </div>

      {/* Pipeline flow diagram */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 0,
        marginBottom: 28,
        flexWrap: 'wrap',
        padding: '16px 20px',
        background: 'rgba(255,255,255,0.01)',
        border: '1px solid var(--border-color)',
        borderRadius: 12,
      }}>
        {[
          { label: 'Resume', sub: 'W_resume', color: '#10b981' },
          { label: '+', sub: '', color: 'var(--text-dim)' },
          { label: 'GitHub', sub: 'W_github', color: '#f59e0b' },
          { label: '+', sub: '', color: 'var(--text-dim)' },
          { label: 'CP', sub: 'W_cp', color: '#ec4899' },
          { label: '+', sub: '', color: 'var(--text-dim)' },
          { label: 'Academics', sub: 'W_cpi, etc.', color: '#06b6d4' },
          { label: '→', sub: '', color: 'var(--text-dim)' },
          { label: 'Master Score', sub: 'flat sum', color: '#6366f1' },
          { label: '→', sub: '', color: 'var(--text-dim)' },
          { label: 'Forecast', sub: 'placement%', color: '#8b5cf6' },
        ].map((item, i) => (
          <div key={i} style={{ textAlign: 'center', padding: '0 10px' }}>
            <div style={{ fontWeight: 700, fontSize: item.label.length === 1 ? '1.4rem' : '0.78rem', color: item.color }}>{item.label}</div>
            {item.sub && <div style={{ fontSize: '0.6rem', color: 'var(--text-dim)', marginTop: 2 }}>{item.sub}</div>}
          </div>
        ))}
      </div>

      {/* Expandable sections */}
      {sections.map(s => <ExpandableSection key={s.id} section={s} />)}


    </div>
  );
};
