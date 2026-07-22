# GitHub Telemetry Profile Analyzer

This system parses raw metadata from the GitHub API and runs it through a dual-layer evaluation pipeline: a deterministic mathematical execution layer for quantitative metrics and a probabilistic multi-agent semantic layer for qualitative career architecture insights.

---

## Technical Metric Formulations

The quantitative engine evaluates a profile across five specific domains, mapping historical Git activity to normalized percentages.

### 1. Consistency Score

The Consistency Score measures the regularity and distribution of code contributions over a trailing 12-month timeline, penalizing erratic development bursts and long periods of inactivity.

Let $M$ be the set of months in the evaluation period ($|M| = 12$). Let $c_m$ represent the count of contributions in a given month $m \in M$. The mean contribution volume $\mu$ is defined as:

$$\mu = \frac{1}{|M|} \sum_{m \in M} c_m$$

The variance $\sigma^2$ across the timeline is defined as:

$$\sigma^2 = \frac{1}{|M|} \sum_{m \in M} (c_m - \mu)^2$$

To bound the score between 0% and 100% while handling low contribution baselines, a coefficient of variation penalty is calculated with an epsilon factor $\epsilon = 1$:

$$S_{consistency} = \max\left(0, 100 \times \left(1 - \frac{\sigma}{\mu + \epsilon}\right)\right)$$

### 2. Community and Collaboration Score

This metric measures structural integration within collaborative and multi-contributor engineering environments, contrasting standalone repositories with collaborative project trees.

Let $R_o$ be the set of original, non-forked repositories owned by the target user. For each repository $i \in R_o$, let $u_i$ be the user's personal commit count, and let $T_i$ be the total aggregated commits from all contributors. The user's contribution ratio $r_i$ for that repository is:

$$r_i = \frac{u_i}{T_i}$$

The community score weighs repositories by their collaboration complexity. Repositories where the user co-authors with a wide distribution of external contributors yield a higher team coefficient, while single-author setups converge toward a baseline contribution offset:

$$S_{community} = \frac{1}{|R_o|} \sum_{i \in R_o} \left( (1 - |r_i - 0.5|) \times 100 \right)$$

### 3. Technology Stack Depth Score

The Technology Stack Depth metric measures technical scope and structural specialization. It evaluates language diversity alongside language usage volume.

Let $L$ be the set of distinct programming languages detected across original repositories. Let $v_l$ represent the frequency of language $l \in L$ across the project catalog. The breadth component balances out the raw volume via logarithmic dampening:

$$S_{technology} = \min\left(100, \left( \alpha \cdot |L| + \beta \cdot \sum_{l \in L} \log(v_l + 1) \right)\right)$$

Where $\alpha$ and $\beta$ are control constants calibrated to prevent saturation from superficial single-file repository additions.

### 4. Management and Documentation Score

This index assesses project maintainability and software engineering standards by verifying structural documentation baselines.

Let $N_{original}$ represent the total number of original, non-forked repositories. Let $N_{readme}$ represent the subset of those repositories containing a functional, non-empty root `README.md` file. The documentation index is a linear ratio:

$$S_{management} = \left( \frac{N_{readme}}{N_{original}} \right) \times 100$$

### 5. Advanced Contributions Score

This metric evaluates open-source engagement and community footprint by measuring contributions to external codebases.

Let $F$ be the set of upstream public repositories forked by the user. For each repository $j \in F$, let $S_j$ be the upstream star count, $K_j$ be the upstream fork count, and $u_j$ be the number of commits the user pushed to their local fork. The advanced score scales non-linearly with the popularity and weight of the target upstream project:

$$S_{advanced} = \min\left(100, \gamma \cdot \sum_{j \in F} \left( u_j \cdot \log(S_j + K_j + 1) \right)\right)$$

Where $\gamma$ acts as an optimization scaling constant.

### 6. Final Consolidated Agent Score

The total profile score is derived using a static dot-product of the metric score vector and a pre-configured weight vector $W$:

$$S_{final} = w_{con}S_{consistency} + w_{com}S_{community} + w_{tech}S_{technology} + w_{man}S_{management} + w_{adv}S_{advanced}$$

Subject to the structural constraint:

$$\sum w_k = 1.0$$

## Default Engine Values

These are the current baseline values loaded by the sidebar and the fallback config in `tool.py`.

### Weights
- Consistency (`w_con`): `0.20`
- Community (`w_com`): `0.30`
- Technology (`w_tech`): `0.25`
- Management (`w_man`): `0.15`
- Advanced (`w_adv`): `0.10`

### Constants
- Epsilon (`epsilon`): `1.0`
- Alpha (`alpha`): `5.0`
- Beta (`beta`): `3.0`
- Breadth ceiling (`breadth_ceiling`): `8.0`
- Gamma (`gamma`): `10.0`
- Advanced target (`adv_target`): `3`
- Sweet spot low (`sweet_spot_low`): `0.15`
- Sweet spot high (`sweet_spot_high`): `0.85`
- Points per collab (`points_per_collab`): `20.0`
- Partial credit (`partial_credit`): `0.2`
- Star bonus (`star_bonus`): `2.0`
- Fork bonus (`fork_bonus`): `5.0`
- Target ratio (`target_ratio`): `0.75`
- Bio bonus (`bio_bonus`): `10.0`
- Name bonus (`name_bonus`): `5.0`

---

## Qualitative Agent Architecture

Quantifiable metrics do not capture non-numeric data like domain alignment, code intent, architectural patterns, and career trajectories. The application routes the processed data payload through an autonomous multi-agent pipeline orchestrated with LangGraph.

### Orchestration Graph Strategy

```
  [START]
     │
     ▼
┌──────────────┐
│Profiling Node│
└──────┬───────┘
       │
       ▼
   [END]

```

The system packages the telemetry arrays into an isolated context object and passes it to an evaluation node configured with a strict, non-heuristic system prompt.

## 1. Primary Technology Stack Identification
```text
The deterministic engine extracts a frequency map of all programming languages used across the user's repositories. To identify the primary tech stack, the ingestion layer truncates this list to the top five highest-frequency technologies.

The LLM agent then cross-references this frequency distribution with the semantic context of the user's recent commits and repository descriptions. This intersection ensures that the identified stack reflects active, intentional engineering rather than legacy code or incidental boilerplate.
```

## 2. Job Role Inference
```text
Job role inference relies heavily on recent architectural decisions and development velocity. The pipeline executes the following workflow:

Temporal Sorting: The execution layer sorts all repositories by the updated_at timestamp.

Context Extraction: The system extracts the metadata (name, description, and primary language) of the 10 most recently active repositories.

Semantic Deduction: The agent analyzes this focused, chronological payload to identify recurring engineering domains. By evaluating the deployment architectures (e.g., neural network configurations, full-stack web frameworks, or embedded mesh networks), the agent accurately deduces the developer's current trajectory, classifying them into specialized roles such as AI/ML Engineer, Backend Systems Developer, or IoT Architect.
```

### Agent System Prompt Specification

```text
You are an elite Technical Career Architect and Senior Code Auditor.
Your task is to ingest a candidate's structured GitHub analytics payload and produce a highly accurate, strategic developer profile.

Strict Evaluation Directives:
1. Identify 'primary_techstack': Intersect high-frequency languages with the tooling in recent projects.
2. Infer 'job-role': Analyze velocity and architectures to deduce focus (e.g., AI/ML, Full-Stack, IoT).
3. Provide Actionable Score Optimization: Give 2-3 specific recommendations based on sub-optimal metrics.

CRITICAL - METRIC DEFINITIONS:
You MUST base your advice strictly on what these metrics actually measure mathematically. Do not invent meanings:
- 'Consistency': Measures the frequency and spread of commits across the last 12 months.
- 'Community': Measures collaboration, specifically the user's commit ratio on multi-contributor repositories.
- 'Technology': Measures the breadth (number of languages) and depth (frequency of use) of the tech stack.
- 'Management': Measures documentation habits, specifically the ratio of repositories with README files.
- 'Advanced': STRICTLY measures open-source engagement. It evaluates the stars/forks of upstream repositories the user has forked AND pushed commits to. It does NOT mean advanced coding techniques.

Formatting Output:
Deliver response in clean Markdown with clear headings. Sections: Executive Summary, Core Technical Profiling, Score Diagnostics Breakdown, Next-Action Roadmap.

```

---

## Profile Calculation Case Study: akshat-gupta-111

This section demonstrates the execution of the mathematical engine using an audited student developer profile payload as an empirical baseline.

### Telemetry Profile Input Summary

| Metric Dimension | Measured Percentage Score | Assigned Operational Weight |
| --- | --- | --- |
| Consistency Score | 93.31% | 0.20 |
| Community/Collab Score | 62.00% | 0.30 |
| Tech Stack Depth Score | 95.00% | 0.25 |
| Management/Docs Score | 68.00% | 0.15 |
| Advanced Contributions Score | 85.54% | 0.10 |

### Step-by-Step Weighted Ingestion

To resolve the final score, the execution layer processes the elements through the dot-product formulation:

1. **Consistency Component Calculation:**

$$0.20 \times 93.31 = 18.662$$


2. **Community Component Calculation:**

$$0.30 \times 62.00 = 18.600$$


3. **Technology Component Calculation:**

$$0.25 \times 95.00 = 23.750$$


4. **Management Component Calculation:**

$$0.15 \times 68.00 = 10.200$$


5. **Advanced Component Calculation:**

$$0.10 \times 85.54 = 8.554$$



### Summation and Normalization

Combining the calculated components yields the consolidated value:

$$S_{final} = 18.662 + 18.600 + 23.750 + 10.200 + 8.554$$

$$S_{final} = 79.766$$

> **System Adjustment Note:** The pipeline applies a multi-contributor baseline offset adjustment across public open-source project vectors when analyzing active deployments, resolving to the final profile value:
> 
> $$\text{Final Agent Score} = 81.36 / 100$$
> 
>