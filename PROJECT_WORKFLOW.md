# GLA Talent Forecast: Technical Architecture & System Workflow Documentation

This document serves as the complete, production-grade technical specification and system architecture walkthrough for the **GLA Talent Forecast** project. It details the system workflows, mathematical formulations, agent collaborations, and implementation layers across both **Engine V1** and **Engine V2** pipelines.

---

## 1. Project Overview

### Purpose & Problem Statement
In traditional university recruitment and talent assessment, there is a fundamental mismatch between **self-reported claims** (found on resumes) and **verified competency** (hands-on code repositories and algorithmic problem-solving). Students often list advanced technologies on resumes without having built actual projects with them, while their competitive programming (CP) capabilities are left siloed on platforms like LeetCode and Codeforces.

**GLA Talent Forecast** solves this problem by providing a data-driven, explainable forecasting platform that:
1. **Cross-validates candidate claims** by scraping and parsing public developer profiles (GitHub, LeetCode, Codeforces, CodeChef, HackerRank) and reading resume PDFs.
2. **Grades candidates mathematically** across 8 core dimensions using customized weight matrices tailored to their college year.
3. **Orchestrates AI agents** to debate claims, synthesize career intents, and forecast placement probability and salary packages.
4. **Applies institutional benchmarks** by executing similarity matching against local historical placement records (591 student dataset from GLA University).
5. **Generates explanations** via Explainable AI (XAI) feature attribution, allowing recruiters and student advisors to modify parameters and inspect predictions.

### Key Features
- **Multi-Platform Scraper Engine**: Parallel HTTP/GraphQL API integration with GitHub, LeetCode, Codeforces, HackerRank, and BeautifulSoup scraping for CodeChef.
- **Multi-Agent Deliberation Bus (I-A2A)**: Collaborative consensus model where GitHub, CP, and Resume agents debate candidate profiles to determine domain alignment.
- **Whiteboard Blackboard Cache (V2)**: Shared, in-memory blackboard allowing agents to execute schema-validated lookups without slow API rounds.
- **SHA256 Bucketed Semantic Cache (V2)**: Clusters candidate metrics into 5-point score intervals to serve forecast queries from disk, optimizing API tokens.
- **Employability Index State Machine (V2)**: Strict 3-pillar gate preventing high-risk predictions and clamping probabilities for deficient profiles.
- **Mini-RAG Local Market Anchors (V2)**: Grounds predicted packages in historical institutional salary baselines.
- **Pydantic Exit Guardrails & Auto-Retry (V2)**: Intercepts raw LLM outputs to enforce schema constraints and retries on validation errors.
- **Interactive Dashboards**: React front-end sandbox (with sliders for real-time weight adjustments) and a standalone Streamlit control room.

### High-Level Architecture

```
                                  +-----------------------+
                                  |    Vite / React UI    |
                                  +-----------+-----------+
                                              |
                                     JSON API | (FastAPI)
                                              v
                                  +-----------+-----------+
                                  |       server.py       |
                                  +-----------+-----------+
                                              |
                                              | sys.stdin/stdout Subprocess
                                              v
                                  +-----------+-----------+
                                  |    agent_runner.py    |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------+-----------+
                                  |    orchestrator.py    |
                                  +-----------+-----------+
                                              |
                   +--------------------------+--------------------------+
                   |                          |                          |
                   v                          v                          v
       +-----------+-----------+  +-----------+-----------+  +-----------+-----------+
       |     Resume Agent      |  |     GitHub Agent      |  |       CP Agent        |
       | (pypdf, Groq/OpenAI)  |  |   (GraphQL/REST API)  |  | (API, BeautifulSoup)  |
       +-----------+-----------+  +-----------+-----------+  +-----------+-----------+
                   |                          |                          |
                   +--------------------------+--------------------------+
                                              |
                                              v
                                  +-----------+-----------+
                                  |  Shared Blackboard    | <--- (V2 Memory Cache)
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------+-----------+
                                  |  Inter-Agent Debate   | <--- (LLM / Fallback)
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------+-----------+
                                  |  Semantic Synthesizer | <--- (Career Intent Profile)
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------+-----------+
                                  |     Semantic Cache    | <--- (V2 Disk/Memory Store)
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------+-----------+
                                  |   Forecasting Agent   | <--- (State Machine + Mini-RAG)
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------+-----------+
                                  |  Pydantic Guardrail   | <--- (Schema Validator & Retry)
                                  +-----------------------+
```

---

## 2. Tech Stack

| Category | Technology | Usage & Rationale |
| :--- | :--- | :--- |
| **Frontend** | React (v19) | Component-based state management, modular component creation, and reactivity. |
| | TypeScript | Implements compile-time type safety for complex forecast data models. |
| | Vite (v8) | Next-generation frontend tooling providing sub-second Hot Module Replacement (HMR). |
| | Lucide React | Provides sleek, vector-based iconography consistent with dashboard requirements. |
| | Vanilla CSS | Custom styling using CSS variables, HSL color tokens, glassmorphism, and transitions. |
| **Backend** | Python (3.10+) | Core runtime for running mathematical engines, web scrapers, and data analysis. |
| | FastAPI | High-performance Web API framework utilizing Python typing for auto-documentation. |
| | Uvicorn | ASGI web server implementation for executing concurrent async request handlers. |
| **Database** | Pandas / OpenPyXL | Manages local tabular storage of datasets and master configurations. |
| | Local Excel/CSV | Tabular storage representing configurations, benchmarks, and institutional dataset. |
| **AI / LLM** | OpenAI API | Invokes `gpt-4o` and `gpt-4o-mini` for metadata extraction, debate, and forecasting. |
| | Groq / Anthropic | Alternate LLM providers integrated in the V2 Resume Agent for fast extraction. |
| **APIs Scraped**| GitHub API | Queries user repositories, commits count, languages, bio, and collaborators. |
| | LeetCode GraphQL | Fetches ranking, accepted submissions, difficulty categories, and calendar metrics. |
| | Codeforces REST | Fetches info, rating history, and user submissions timeline. |
| | CodeChef HTML | Scrapes profiles using BeautifulSoup to parse rating, stars, and solved counts. |
| | HackerRank REST | Fetches hacker profiles, badge models, track scores, and active durations. |
| **Dev Tools** | Oxlint | High-speed JavaScript/TypeScript linter used to keep codebase standards clean. |
| | Streamlit | Standalone library used to implement a local dashboard for testing V2 resume rules. |
| | Gdown / PyPDF | Gdown pulls test resumes from Drive links; PyPDF handles text stream extractions. |

---

## 3. Folder Structure

```
orichestation/
├── Talent_Forecast/                  # Main Project Directory
│   ├── package.json                  # Frontend dependencies and Vite build scripts
│   ├── vite.config.ts                # Vite configurations (bundler, plugins, ports)
│   ├── tsconfig.json                 # TypeScript compiler base rules
│   ├── index.html                    # Single Page Application container template
│   ├── server.py                     # FastAPI backend application exposing REST API
│   ├── agent_runner.py               # Subprocess bridging CLI script
│   ├── merge_cont_update.xlsx        # Historical institutional dataset (591 GLA students)
│   │
│   ├── src/                          # React Frontend Source
│   │   ├── main.tsx                  # React DOM mount orchestrator
│   │   ├── App.tsx                   # Main layout container and app states
│   │   ├── App.css                   # Component-specific frontend stylesheets
│   │   ├── index.css                 # Global design system variables & glassmorphism
│   │   └── components/
│   │       ├── StudentSelector.tsx   # Sidebar list for batch/student CSV mapping
│   │       ├── ParameterForm.tsx     # Central profile editor and resume PDF uploader
│   │       └── ForecastResults.tsx   # Predictions visualizer & XAI sliders panel
│   │
│   ├── agent/                        # V1 Evaluation Engine
│   │   ├── .env                      # Local environment configurations (OpenAI keys)
│   │   ├── requirements.txt          # V1 python dependency list
│   │   ├── agent/                    # GitHub Agent folder (scraper.py, mathematics.py, tool.py)
│   │   ├── cpgent/                   # Competitive Programming Agent (main.py)
│   │   ├── resugent/                 # Resume Agent (utils.py)
│   │   ├── Suites/                   # V1 dataset suites (year2_data.csv, year6_data.csv)
│   │   └── final/                    # V1 configurations and core scripts
│   │       ├── initialize.py         # Setups master config files
│   │       ├── config/               # benchmarks.json, domain_ontology.json, master_config.xlsx
│   │       └── core/                 # V1 orchestrator and agent scripts
│   │
│   └── Agent V2/                     # V2 Evaluation Engine (Blackboard & Semantic Cache)
│       ├── .env                      # V2 environment keys
│       ├── requirements.txt          # V2 python requirements
│       ├── agent/                    # GitHub Agent V2
│       ├── cpgent/                   # CP Agent V2
│       ├── resugent/                 # Resume Agent V2 (app.py Streamlit dashboard, utils.py)
│       ├── Suites/                   # V2 datasets and PDF resume repositories
│       └── final/                    # V2 configurations and core modules
│           ├── initialize.py         
│           ├── config/               # V2 benchmarks.json, domain_ontology.json, master_config.xlsx
│           └── core/                 
│               ├── blackboard.py     # Whiteboard memory bus schema queries
│               ├── semantic_cache.py # SHA256 bucketed disk-cache manager
│               ├── orchestrator.py   # V2 master execution flow
│               └── agent_communication.py, career_synthesizer.py, forecasting_agent.py
```

### Key Folder Rationale & Interactions
- **`src/` & `server.py`**: The frontend sends requests to `/api/evaluate` inside `server.py`. The server saves any uploaded PDF resume to a temporary directory and executes a Python subprocess.
- **`agent_runner.py`**: Acts as a bridge between the FastAPI server and the core agent modules. It prepends the correct engine directory (`agent` or `Agent V2`) to Python’s `sys.path`, loads the associated `.env` variables, and reads the JSON payload from standard input.
- **`core/` & `agent/cpgent/resugent`**: The orchestrator spawns concurrent task threads to run `resume_agent`, `github_agent`, and `cp_agent`. They fetch data and calculate sub-scores using their respective mathematics module, sending the final snapshots to the debate and synthesizer components.

---

## 4. Application Startup Flow

```
[User opens website]
         ↓
[React frontend mounts via src/main.tsx]
         ↓
[Theme (light/dark) and active portal engine (V1/V2) load from localStorage]
         ↓
[React calls GET /api/batches to populate batch selection dropdown]
         ↓
[React calls GET /api/students/{batch_id} to fetch student records from suites]
         ↓
[Sidebar populates student list sorted by Roll Number]
         ↓
[User selects student -> Form pre-fills profile URLs, GPA, DSA and English marks]
         ↓
[User clicks "Run Forecast Prediction"]
         ↓
[React state changes: submitting=true -> cycle loading steps animation]
         ↓
[React sends multipart/form-data POST request to /api/evaluate]
         ↓
[FastAPI receives request -> saves uploaded resume as temporary PDF file]
         ↓
[FastAPI resolves V1/V2 paths -> spawns subprocess: python agent_runner.py <version>]
         ↓
[Subprocess loads version dotenv -> reads payload from stdin -> inserts core paths to sys.path]
         ↓
[Subprocess executes orchestrator.py -> loads config from master_config.xlsx]
         ↓
[Subprocess executes orchestrator.py -> loads config from master_config.xlsx]
         ↓
[Orchestrator spawns concurrent async tasks via asyncio.gather()]
  ├─> executes GitHub Agent (scrapes profile, commits, repo statistics)
  ├─> executes CP Agent (fetches LeetCode/CF/CodeChef/HackerRank metrics)
  └─> executes Resume Agent (reads PDF, extracts details using LLM)
         ↓
[V2: Agent metrics are published to SharedBlackboard in-memory slots]
         ↓
[Orchestrator calls agent_communication: debate bus validated consensus domain matrix]
         ↓
[Orchestrator calls career_synthesizer: builds semantic profile summary]
         ↓
[V2: Computes SHA256 profile hash -> checks semantic cache disk store]
  ├─> Cache HIT: return cached forecast payload immediately (0ms, $0 cost)
  └─> Cache MISS:
         ├─> executes forecasting_agent (Pillar State Machine + Semantic Anchor + Mini-RAG)
         ├─> executes Pydantic Exit-Point Guardrail (validates types, retries on error)
         └─> writes new forecast payload to local disk cache
         ↓
[Subprocess outputs result JSON on stdout -> terminates]
         ↓
[FastAPI server parses subprocess JSON -> runs Excel k-NN similarity lookup in GLA dataset]
         ↓
[FastAPI calculates XAI feature attributions -> formats final JSON payload -> returns HTTP response]
         ↓
[React updates evaluationResult state -> triggers transition animations]
         ↓
[Dashboard renders metrics, Consensus brainstorm dialogue, and backtesting tables]
```

---

## 5. Complete Request Lifecycle

### 1. `GET /api/batches`
- **Frontend Source**: Called in [StudentSelector.tsx](file:///c:/Users/Rudra/OneDrive/Desktop/orichestation/Talent_Forecast/src/components/StudentSelector.tsx#L46-L64) inside `fetchBatches()`. Passed `version` parameter.
- **HTTP Request**: `GET /api/batches?version=v1|v2`
- **FastAPI Route**: [@app.get("/api/batches")](file:///c:/Users/Rudra/OneDrive/Desktop/orichestation/Talent_Forecast/server.py#L338)
- **Controller/Service**: Finds files in the Suites directory (`agent/Suites` or `Agent V2/Suites`) matching the pattern `year*_data.csv`.
- **Database Query**: Read filenames via python standard library `glob`.
- **Response Formatting**: Formats into `[{"id": "year6", "label": "Year 6"}]`.
- **Frontend Rendering**: populates selector dropdown state.

### 2. `GET /api/students/{batch_id}`
- **Frontend Source**: Called in [StudentSelector.tsx](file:///c:/Users/Rudra/OneDrive/Desktop/orichestation/Talent_Forecast/src/components/StudentSelector.tsx#L66-L79) inside `fetchStudents()`. Passes batch ID and engine version.
- **HTTP Request**: `GET /api/students/year6?version=v1|v2`
- **FastAPI Route**: [@app.get("/api/students/{batch_id}")](file:///c:/Users/Rudra/OneDrive/Desktop/orichestation/Talent_Forecast/server.py#L354)
- **Controller/Service**: Reads CSV files safely via `parse_csv_safely(file_path)` which adjusts mismatched columns (e.g. CodeChef shift offsets) and strips trailing whitespace.
- **Database Query**: Pandas parses CSV file and generates dictionary rows.
- **Response Formatting**: Formats rows into student interfaces containing `name`, `roll_number`, `gpa`, `github`, `leetcode`, and `raw_data`.
- **Frontend Rendering**: Renders student items list in sidebar.

### 3. `POST /api/evaluate`
- **Frontend Source**: Called in [App.tsx](file:///c:/Users/Rudra/OneDrive/Desktop/orichestation/Talent_Forecast/src/App.tsx#L72-L95) inside `handleFormSubmit(formData)`.
- **HTTP Request**: `POST /api/evaluate` (Multipart Form Payload)
- **FastAPI Route**: [@app.post("/api/evaluate")](file:///c:/Users/Rudra/OneDrive/Desktop/orichestation/Talent_Forecast/server.py#L523)
- **Controller/Service**:
  1. Checks if configuration path exists.
  2. Saves PDF resume to temporary directory.
  3. Formulates a JSON subprocess payload containing data URLs, GPA, marks, and temp file path.
  4. Calls `run_agent_in_subprocess` which spawns `agent_runner.py` passing stdin payload.
- **Subprocess Pipeline**:
  1. Spawns, modifying system paths.
  2. Spawns threads to fetch profile metrics and parse resume.
  3. Runs consensus debate and synthesizer (LLM calls).
  4. V2: Blackboard snapshot, Semantic cache retrieval, Employability state machine, Mini-RAG, Pydantic model check.
  5. Returns structured JSON string.
- **FastAPI Post-Processing**:
  1. Runs `run_historical_analysis` which reads `merge_cont_update.xlsx`, cleans GPA values, determines placement statuses, runs distance matching, and returns the historical rates.
  2. Runs `generate_xai_attribution_backend` to map parameter impacts.
  3. Cleans temporary files.
- **Response Formatting**: JSON block with evaluations, consensus, semantic profile, forecast, and historical analysis.
- **Frontend Rendering**: Renders results, dials, transcripts, and backtesting tables.

### 4. `GET /api/download-template`
- **Frontend Source**: Download button in sandbox interface.
- **HTTP Request**: `GET /api/download-template`
- **FastAPI Route**: [@app.get("/api/download-template")](file:///c:/Users/Rudra/OneDrive/Desktop/orichestation/Talent_Forecast/server.py#L864)
- **Controller/Service**: Generates a standard list of CSV columns.
- **Response Formatting**: Returns a `StreamingResponse` with media type `text/csv` and file name header `gla_talent_forecast_template.csv`.

### 5. `POST /api/evaluate-bulk`
- **Frontend Source**: Called in [App.tsx](file:///c:/Users/Rudra/OneDrive/Desktop/orichestation/Talent_Forecast/src/App.tsx#L97-L134) inside `handleBulkSubmit()`.
- **HTTP Request**: `POST /api/evaluate-bulk` (with spreadsheet file and a list of resume PDFs)
- **FastAPI Route**: [@app.post("/api/evaluate-bulk")](file:///c:/Users/Rudra/OneDrive/Desktop/orichestation/Talent_Forecast/server.py#L889)
- **Controller/Service**:
  1. Creates a temporary resumes directory and saves uploaded PDFs, mapping filenames.
  2. Reads spreadsheet and maps columns (name, roll, GPA, GitHub, LeetCode, etc.).
  3. Iterates over rows (capped at 50 records to prevent hangs).
  4. For each row: matches resume, calls `run_agent_in_subprocess` (if API key is found) or gets fallback mock, executes historical analysis, and generates attribution.
  5. Uses `asyncio.gather` to evaluate records in parallel.
- **Response Formatting**: JSON array of evaluation results.
- **Frontend Rendering**: Renders search list of bulk records, allowing recruiters to inspect individual audits.

---

## 6. Backend Workflow

```
+--------------------------------------------------------+
|                      FastAPI App                       |
|   (CORS Middleware, route registrations, settings)     |
+                           +                            +
                            |
                            v
+---------------------------+----------------------------+
|             HTTP POST Request on /api/evaluate         |
+                           +                            +
                            |
                            v
+---------------------------+----------------------------+
|             Temp File Handler (NamedTemporaryFile)      |
|           (Saves uploaded resume.pdf to system disk)   |
+                           +                            +
                            |
                            v
+---------------------------+----------------------------+
|        Subprocess Runner (asyncio.to_thread & Popen)   |
|     (Spawns agent_runner.py, pipes JSON to sys.stdin)  |
+                           +                            +
                            |
                            v
+---------------------------+----------------------------+
|             FastAPI Historical Validation Engine        |
|  (Loads merge_cont_update.xlsx, cleans columns, filters  |
|   cpi range, checks placement rates, yields statistics) |
+                           +                            +
                            |
                            v
+---------------------------+----------------------------+
|         FastAPI Explainable AI Attribution Engine       |
|    (Attributes parameter weights based on GPA brackets,|
|      active backlogs, DSA marks, and profile status)   |
+                           +                            +
                            |
                            v
+---------------------------+----------------------------+
|             Finally Block (Temporary File Cleanup)     |
|         (Removes temp files and directory handles)      |
+--------------------------------------------------------+
```

### Express-like Structure in FastAPI
FastAPI implements equivalent middleware, routing, and controller layers:
- **Initialization**: Initialized as `app = FastAPI(title="Talent Forecast API")`.
- **CORS Middleware**: Exposes cross-origin requests using `CORSMiddleware` intercepting requests.
- **Routes & Controllers**: Route decorators (e.g., `@app.post("/api/evaluate")`) serve as routing paths, directing inputs to handlers.
- **Error Handling**: Implements direct validation error captures and returns structured HTTPExceptions (e.g. status code 400 for non-pdf files).
- **Subprocess Isolation**: Utilizes `subprocess.Popen` to separate LLM-based agent logic from Web API routes.

---

## 7. Frontend Workflow

The React frontend represents a high-performance sandbox workspace.

### Core React States
- `activePortal`: Version engine state toggling between `v1` and `v2`. Switches HSL color accents (`--color-primary` transitions from Indigo to Purple/Magenta).
- `evaluationResult`: Renders prediction summaries, consensus matrix, XAI charts, blackboard logs, cache hits, and validation deviations.
- `activeMode`: Toggles between `sandbox` (single student parameters form) and `bulk` (batch uploads).
- `bulkResults` / `selectedBulkStudent`: Holds arrays of evaluations returned from CSV bulk execution.

### Component Structure & Communication
1. **[App.tsx](file:///c:/Users/Rudra/OneDrive/Desktop/orichestation/Talent_Forecast/src/App.tsx)**: Main layout container coordinating sidebar selectors, forms, and results.
2. **[StudentSelector.tsx](file:///c:/Users/Rudra/OneDrive/Desktop/orichestation/Talent_Forecast/src/components/StudentSelector.tsx)**: Emits `onSelectStudent(student, batchId)` when selected.
3. **[ParameterForm.tsx](file:///c:/Users/Rudra/OneDrive/Desktop/orichestation/Talent_Forecast/src/components/ParameterForm.tsx)**: Flexibly maps selected student properties. Emits `onSubmit(formData)` on click.
4. **[ForecastResults.tsx](file:///c:/Users/Rudra/OneDrive/Desktop/orichestation/Talent_Forecast/src/components/ForecastResults.tsx)**: Displays scores, consensus matrices, and features. Uses custom sliders to recalculate local attributions dynamically.

---

## 8. Database Workflow

The database layer utilizes tabular storage (Excel/CSV files) handled via Pandas.

### Historical Institutional Dataset Structure (`merge_cont_update.xlsx`)
This file contains **591 student profiles** from GLA University with fields:
- `Current CPI`, `Backlogs Count`, `DSA marks (in Btech)`, `English marks (in BTech)`, `Number of internships completed`.
- `Placement status`: String representing placement status ("Placed" / "Not Placed").
- `If placed, Write your salary package?`: String indicating packages (e.g., "4.5 LPA", "6 Lakhs").
- `If placed,then Describe your role and company name...`: Target employer info.

### Similarity Matching Logic (KNN-like Lookup)
The `run_historical_analysis` function matches new candidate profiles against the historical dataset:
1. **Clean Columns**: Normalizes CPI, sets empty backlogs to 0, and parses salary strings to floats via regex.
2. **Parse Placement Status**: Standardizes placement status to a boolean flag (`is_placed`).
3. **Calculate Similarity Filter**: Filters rows matching academic criteria:
   $$\text{clean\_cpi} \in [\text{user\_cpi} - 0.8, \text{user\_cpi} + 0.8]$$
   $$\text{clean\_backlogs} \le \text{user\_backlogs} + 1$$
   $$\text{clean\_dsa} \in [\text{user\_dsa} - 15, \text{user\_dsa} + 15]$$
4. **Expand Filter**: If the filtered count is less than 5 profiles, it expands the criteria to:
   $$\text{clean\_cpi} \in [\text{user\_cpi} - 1.5, \text{user\_cpi} + 1.5]$$
5. **Aggregate Metrics**: Computes historical placement rates, mean package, salary range boundaries, and top employer companies.

---

## 9. Authentication Workflow

The application operates in sandbox mode for assessment:
- **Middleware**: No auth middleware is implemented in `server.py`.
- **Protected Routes**: React router/pages are unsecured, allowing placement cells to run evaluations directly.

---

## 10. AI Workflow (Very Detailed)

```
                            +--------------------------+
                            |      Student Record      |
                            +------------+-------------+
                                         |
                                         v
                            +--------------------------+
                            |    LLM Smart Parser      | <--- (Cleans profile handles)
                            +------------+-------------+
                                         |
                                         v
                            +--------------------------+
                            |    OpenAI/Groq/Claude    | <--- (Resume details extraction)
                            +------------+-------------+
                                         |
                                         v
                            +--------------------------+
                            |    GitHub Domain LLM     | <--- (Analyzes repositories)
                            +------------+-------------+
                                         |
                                         v
                            +--------------------------+
                            |    Deliberation Bus      | <--- (3-Round Inter-Agent Debate)
                            +------------+-------------+
                                         |
                                         v
                            +--------------------------+
                            |    Semantic Synthesis    | <--- (Forms Career Intent)
                            +------------+-------------+
                                         |
                                         v
                            +--------------------------+
                            |    Forecasting Agent     | <--- (State Machine + Mini-RAG)
                            +------------+-------------+
                                         |
                                         v
                            +--------------------------+
                            |    Pydantic Guardrail    | <--- (ValidationError checking)
                            +--------------------------+
```

### 1. `llm_smart_parser` (Orchestrator V2)
- **Role**: Standardizes raw CSV strings and maps names to available resume filenames.
- **Prompt**:
  - Input: Raw CSV string and a list of available PDF filenames.
  - Output: Strict JSON output with parsed student handles and the matched resume filename.

### 2. GitHub Domain Extraction (`extract_domain_via_llm` in agent/tool.py)
- **Role**: Infers candidate primary domain from repository descriptions.
- **Prompt**:
  - Input: Profile bio, language frequency map, and repository summaries (names, descriptions, languages).
  - Output: Single JSON object containing the matched domain.

### 3. Resume Data Extraction (`extract_resume_data` in resugent/utils.py)
- **Role**: Structured extraction of candidate parameters.
- **Prompt**:
  - Input: Concatenated resume text.
  - Output: Dict mapped to `ResumeData` Pydantic model. Extracts bullet counts, links, section headers, skills, projects, and roles.

### 4. Agent-to-Agent Debate Bus (`run_inter_agent_communication` in core/agent_communication.py)
- **Role**: Deliberates domain alignment across the three agents.
- **Prompt**:
  - Input: Student details, GitHub findings, Resume findings, CP platform ratings, and domain ontology.
  - Debate Protocol:
    - **Round 1 (Evidence Statements)**: Agents state initial domain proposals.
    - **Round 2 (Cross-Validation)**: GitHub agent cross-checks resume skills against repository commits; CP agent cross-checks algorithmic metrics. Identifies strongly verified, partially verified, and unverified claims.
    - **Round 3 (Consensus)**: Agents agree on primary/secondary domains, validation score, verified skills, and validation reasoning.

### 5. Career Semantic Synthesizer (`synthesize_profile` in core/career_synthesizer.py)
- **Role**: Generates a unified candidate profile summary.
- **Prompt**:
  - Input: All agent findings and the domain consensus matrix.
  - Output: JSON mapping career intent, primary/secondary domains, top skills, experience summary, strengths, and weaknesses.

### 6. Forecasting Agent (`execute_forecast` in core/forecasting_agent.py)
- **Role**: Grounded placement and salary forecasting.
- **Prompt**:
  - Input: Semantic profile, agent scores, historical benchmarks, domain ontology, state machine status, and Mini-RAG baseline salary.
  - Output: Predicted domain, confidence, recommended roles, placement probability, expected salary band, career readiness, differentiators, and risk factors.

### 7. Pydantic Exit-Point Guardrail & Auto-Retry Loop
- **Role**: Ensures structured LLM outputs.
- **Workflow**:
  - Checks forecast outputs against `ForecastOutputGuardrail` Pydantic model.
  - If a validation error occurs (e.g. text instead of a float), catches exception and increments retry counter.
  - Sends a correction hint back to the LLM. Falls back to the deterministic engine if retries are exhausted.

---

## 11. Business Logic & Mathematical Formulas

The system relies on concrete scoring algorithms.

### 1. GitHub Evaluation Model (`agent/mathematics.py`)

- **Consistency Score**:
  - Calculates coefficient of variation (CV) of monthly commits.
  - In V2, base-2 log dampening is applied to prevent hackathon spikes from distorting variance:
    $$C_{\text{log}} = \log_2(C_{\text{raw}} + 1)$$
    $$\mu_{\text{log}} = \frac{1}{N}\sum C_{\text{log}}, \quad \sigma_{\text{log}} = \sqrt{\frac{1}{N}\sum(C_{\text{log}} - \mu_{\text{log}})^2}$$
    $$\text{Score}_{\text{consistency}} = \max\left(0, 100 \times \left(1 - \frac{\sigma_{\text{log}}}{\mu_{\text{log}} + \epsilon}\right)\right)$$

- **Community Score**:
  - Rewards collaboration in shared repositories (user commits < total commits):
    $$\text{Engagement Sum} = \sum_{\text{repos}} \begin{cases} 1.0 & \text{if } 0.15 \le \text{user\_commit\_ratio} \le 0.85 \\ 0.2 & \text{otherwise} \end{cases}$$
    $$\text{Score}_{\text{community}} = \min(100.0, (\text{Engagement Sum} \times 20.0) + (10 \times \log_{10}(\text{Stars} + 1) \times 2.0) + (10 \times \log_{10}(\text{Forks} + 1) \times 5.0))$$

- **Technology Score**:
  - Balances programming language breadth and depth, capping breadth to prevent gaming:
    $$\text{Score}_{\text{technology}} = \min(100.0, (\alpha \times \min(L, \text{breadth\_ceiling})) + (\beta \times \sum \log_2(\text{count} + 1)))$$

- **Advanced Score**:
  - Measures contribution to open-source forks:
    $$\text{Score}_{\text{advanced}} = \min\left(100.0, \sum_{\text{forked\_repos}} \min(\text{raw\_score}, \text{max\_per\_repo})\right)$$
    $$\text{raw\_score} = \gamma \times \log_{10}(\text{stars} + \text{forks} + 1) \times \log_2(\text{user\_commits\_count} + 1)$$

### 2. Competitive Programming Evaluation Model (`cpgent/main.py`)
- Platform scores (LeetCode, CF, CodeChef, HackerRank) are calculated based on solved counts and ratings.
- Aggregates platform scores using dynamic weights:
  $$\text{weight}_p = \frac{\text{idx}_p}{\sum \text{idx}_p}, \quad \text{idx}_p = \ln(\text{solved\_count} + 1) \times \frac{\text{clout}}{100}$$
  $$\text{Base Score} = \sum \text{Score}_p \times \text{weight}_p$$
- Multiplies by sigmoidal factor $m_{\text{global}}$ representing the standard deviation of activity over the past 365 days.

### 3. Resume Evaluation Model (`resugent/utils.py`)
- **`S_hygiene`**: Page count (P), links count, and mandatory section checks:
  $$S_{\text{hygiene}} = \max(0, 100 - (50 \times (P - 1)) - (15 \times L_{\text{missing}}) - (20 \times X_{\text{missing}}))$$
- **`S_realization`**: Matches declared skills ($D$) against descriptions ($A$):
  $$S_{\text{realization}} = \frac{\sum_{k \in D \cap A} \ln(\text{difficulty}(k) + 1)}{\sum_{k \in D} \ln(\text{difficulty}(k) + 1) + \epsilon} \times 100$$
- **`S_complexity`**: Project complexity based on architectural keywords (Tier 3 = 100, Tier 2 = 65, Tier 1 = 25):
  $$S_{\text{complexity}} = \min(100, \max(C_j) + \alpha \times \ln(J + 1))$$
- **`S_impact`** (V2 Model): Impact score calculated using regex-extracted numeric values ($V_b$) from bullet points:
  $$S_{\text{impact}} = \min(100, \beta \times \sum \log_{10}(v + 1))$$
- **`S_production`**: Percentage of projects with repository and live URLs:
  $$S_{\text{production}} = \frac{J_{\text{code}} + J_{\text{deploy}}}{2 \times J_{\text{total}}} \times 100$$
- **`S_clarity`**: Deduces points for using buzzwords:
  $$S_{\text{clarity}} = \max(0, 100 - \omega \times \sum \ln(\text{buzzword\_count} + 1))$$
- **`S_domain`** (V2 Model): Specialization index:
  $$S_{\text{domain}} = \max\left(0, 100 \times \left(1 - \frac{\text{unique\_domains}}{\text{total\_skills} + \epsilon}\right)\right)$$
- **`S_velocity`**: Weighted roles (internship=15, freelance=10, tech_lead=10, member=3) scaled by duration:
  $$S_{\text{velocity}} = \min(100, \text{velocity\_sum})$$

### 4. Dynamic Weighting Matrix by Year
The final score is a weighted average of these 8 categories, varying by college year:

| Category | Year 2 weight | Year 3 weight | Year 4 weight |
| :--- | :---: | :---: | :---: |
| **`S_hygiene`** | 0.25 | 0.15 | 0.05 |
| **`S_realization`**| 0.25 | 0.20 | 0.10 |
| **`S_complexity`** | 0.20 | 0.25 | 0.30 |
| **`S_impact`** | 0.05 | 0.10 | 0.20 |
| **`S_production`** | 0.10 | 0.15 | 0.15 |
| **`S_clarity`** | 0.05 | 0.05 | 0.05 |
| **`S_domain`** | 0.05 | 0.05 | 0.05 |
| **`S_velocity`** | 0.05 | 0.05 | 0.10 |

### 5. Master Score Calculation
Calculates score based on linked profile profiles:
- **Both GitHub & CP Linked**:
  $$\text{Master Score} = 0.40 \times \text{Score}_{\text{resume}} + 0.60 \times \max(\text{Score}_{\text{github}}, \text{Score}_{\text{cp}})$$
- **Only GitHub Linked**:
  $$\text{Master Score} = 0.57 \times \text{Score}_{\text{resume}} + 0.43 \times \text{Score}_{\text{github}}$$
- **Only CP Linked**:
  $$\text{Master Score} = 0.57 \times \text{Score}_{\text{resume}} + 0.43 \times \text{Score}_{\text{cp}}$$
- **No Coding Profiles Linked**:
  $$\text{Master Score} = \text{Score}_{\text{resume}}$$

---

## 12. System Data Flow Diagram

```
[User Click] ────> React UI Event Handler (handleFormSubmit)
                         │
                         ▼
             React State Updater (submitting=true)
                         │
                         ▼
             Fetch HTTP Post Request (/api/evaluate)
                         │
                         ▼
             FastAPI server.py Upload Validator
                         │
                         ▼
             NamedTemporaryFile PDF disk save
                         │
                         ▼
             asyncio.to_thread subprocess spawn
                         │
                         ▼
             agent_runner.py sys.path adjustment
                         │
                         ▼
             core/orchestrator.py load master config
                         │
                         ▼
             asyncio.gather Agent Task Spawners
             ├── run_resume_agent (pypdf, Groq/OpenAI)
             ├── run_github_agent (GitHub GraphQL)
             └── run_cp_agent (CP REST/BeautifulSoup)
                         │
                         ▼
             SharedBlackboard Slots Update (V2)
                         │
                         ▼
             Blackboard.query_skill_validation()
                         │
                         ▼
             agent_communication Consensus debate
                         │
                         ▼
             career_synthesizer semantic synthesis
                         │
                         ▼
             SemanticCacheEngine search (V2)
               ├── HIT: return cached forecast JSON
               └── MISS:
                     │
                     ▼
             forecasting_agent execution
             ├── calculate_employability_state_machine()
             ├── anchor_semantic_domain()
             └── mini_rag_salary_lookup()
                     │
                     ▼
             Pydantic validation model checks
                     │
                     ▼
             Subprocess sys.stdout write
                         │
                         ▼
             FastAPI server.py stdout parser
                         │
                         ▼
             run_historical_analysis (K-NN Excel lookup)
                         │
                         ▼
             generate_xai_attribution_backend()
                         │
                         ▼
             HTTP JSON API response return
                         │
                         ▼
             React State Updater (evaluationResult=res)
                         │
                         ▼
             Dashboard UI render (charts, dials, logs)
```

---

## 13. Middleware Execution Order

FastAPI executes middlewares in the following order:
1. **CORS Middleware (`CORSMiddleware`)**: Inspects headers, handles preflight `OPTIONS` requests, and injects access controls.
2. **Request Body Stream Parser**: Parses multipart form data and saves file payloads to memory or temporary storage.
3. **Subprocess Thread Pool (`asyncio.to_thread`)**: Spawns isolated execution environments to prevent blocking the event loop.

---

## 14. Error Handling Workflow

- **File Validation Errors**: If the uploaded resume is not a PDF, catches the error early and raises an HTTP 400 Exception.
- **Missing Configuration Warnings**: If `master_config.xlsx` is missing, `config_loader` catches the error, imports `initialize`, and generates default configurations.
- **Subprocess Failures**: If the Python runner exits with a non-zero code, catches stderr, logs tracebacks, and executes `get_fallback_mock_result` so the UI remains operational.
- **Validation Retry Loop**: Retries LLM calls up to 3 times on Pydantic validation errors before falling back to the deterministic lookup engine.

---

## 15. Security Workflow

- **Subprocess Isolation**: Isolates the main Web API from the LLM execution pipeline.
- **Token Handling**: Loads `OPENAI_API_KEY` and `GITHUB_TOKEN` using `load_dotenv` without hardcoding credentials.
- **Path Verification**: Resolves relative file locations to absolute paths using `Path.resolve()` to prevent traversal attacks.
- **Upload Size Constraints**: Limits bulk processing requests to 50 rows to prevent Denial of Service (DoS) hangs.

---

## 16. Performance Optimizations

- **Parallel Agent Execution**: Runs Github, CP, and Resume scrapers concurrently using `asyncio.gather` to reduce execution times.
- **In-Memory Blackboard (V2)**: Enables zero-latency data sharing, avoiding duplicate API calls.
- **Discretized Semantic Cache (V2)**: Buckets scores into 5-point intervals:
  $$\text{bucket} = \text{floor}\left(\frac{\text{score}}{5}\right) \times 5$$
  Allows similar student profiles to retrieve cached forecasts instantly, reducing API costs.

---

## 17. Deployment Workflow

- **FastAPI Backend Service**: Run locally using Uvicorn:
  `uvicorn server:app --host 127.0.0.1 --port 8000 --reload`
- **Frontend Development Server**: Run using Vite:
  `npm run dev`
- **Vite Production Bundler**: Compile assets using:
  `npm run build`
- **Streamlit Interactive Dashboard**: Run the standalone V2 resume scorer:
  `streamlit run app.py`

---

## 18. System Sequence Diagram

```
User          React UI       FastAPI server     agent_runner     Agents (GH/CP/Res)    OpenAI LLM     Blackboard      Semantic Cache
 │               │                 │                 │                 │                │             │               │
 ├─Click Evaluate─>                │                 │                 │                │             │               │
 │               ├─POST /evaluate──>                 │                 │                │             │               │
 │               │                 ├─Spawn Subproc──>                 │                │             │               │
 │               │                 │                 ├─Run Orchestrate─>                │             │               │
 │               │                 │                 │                 ├─Run Agents────>│             │               │
 │               │                 │                 │                 │                ├─Get Extract─>               │
 │               │                 │                 │                 │                │             ├─Publish Slots─>
 │               │                 │                 │                 │                │             │               ├─Check Cache──>
 │               │                 │                 │                 │                │             │               │ (MISS)
 │               │                 │                 │                 │                ├─Forecasting─>               │
 │               │                 │                 │                 │                │ (State Machine, Mini-RAG)   │
 │               │                 │                 │                 │                │             │               ├─Save Cache───>
 │               │                 │                 ├─Stdout JSON─────>                │             │               │
 │               │                 ├─Excel k-NN Match─>                │                │             │               │
 │               │                 ├─Generate XAI────>                 │                │             │               │
 │               │<─JSON Response──┤                 │                 │                │             │               │
 │               ├─Render UI──────>│                 │                 │                │             │               │
```

---

## 19. End-to-End Execution Trace: Evaluating a Student

This execution trace tracks the flow of evaluating a student (Roll No. `201500292`) under Portal Engine V2:

1. **User Action**: The user selects a student in the sidebar, loads their details into the Parameter Form, uploads their resume PDF, and clicks "Run Forecast".
2. **Frontend Event Handler**: `handleFormSubmit()` in `App.tsx` intercepts the event, compiles a `FormData` object with profile parameters, and sends a POST request to `/api/evaluate`.
3. **FastAPI Route Interception**: `@app.post("/api/evaluate")` in `server.py` receives the request. The uploaded PDF is saved to a temporary file via `NamedTemporaryFile()`.
4. **Subprocess Instantiation**: `run_agent_in_subprocess()` spawns the runner:
   `sys.executable agent_runner.py v2`
   It writes the payload JSON (including temp resume path and profile links) to stdin.
5. **Path Configuration**: `agent_runner.py` intercepts the stdin stream, prepends `Agent V2/final/core` to `sys.path`, loads the associated `.env` variables, and imports `orchestrator.py`.
6. **Master Config Resolution**: `config_loader.load_master_config()` reads `Agent V2/final/config/master_config.xlsx` and parses category weights and penalties.
7. **Agent Execution**:
   - `orchestrator.evaluate_student()` is called.
   - It spawns three concurrent async tasks via `asyncio.gather()`:
     - `run_github_agent()` invokes `github_tool.execute_github_agent()`, which scrapes repository stats and identifies the primary tech stack.
     - `run_cp_agent()` invokes `cp_tool.execute_cp_agent()`, which fetches LeetCode, Codeforces, HackerRank, and CodeChef metrics.
     - `run_resume_agent()` invokes `resume_tool.execute_resume_agent()`, which reads the PDF text and extracts structured details.
8. **Blackboard Publication**: The agents write their findings to `SharedBlackboard` slots.
9. **Inter-Agent Consensus**: `agent_communication.run_inter_agent_communication()` queries the blackboard using `query_skill_validation()` to resolve the primary domain (e.g. `AI/ML` with 85% validation score).
10. **Semantic Synthesis**: `career_synthesizer.synthesize_profile()` compiles the consensus matrix and agent findings, returning a semantic career summary.
11. **Semantic Cache Check**:
    - `SemanticCacheEngine.compute_profile_hash()` computes a hash of the student's metrics.
    - If the hash is found in `forecasting_cache.json`, returns the cached forecast.
    - If not, proceeds to run the forecasting agent.
12. **Grounded Forecasting**:
    - `forecasting_agent.execute_forecast()` runs the Employability Index State Machine, anchors the domain, and retrieves salary baselines from `benchmarks.json`.
    - It queries the LLM to generate the final forecast, validates it against Pydantic models, and writes the output to the cache.
13. **Subprocess Exit**: The runner outputs the JSON string to stdout and terminates.
14. **FastAPI Post-Processing**:
    - `server.py` parses the subprocess output.
    - It calls `run_historical_analysis()` to query `merge_cont_update.xlsx` for similar student profiles.
    - It calls `generate_xai_attribution_backend()` to compute feature impacts.
    - It deletes the temporary resume PDF and returns the final JSON payload.
15. **UI Rendering**: The React frontend updates its state and renders the forecast metrics.

---

## 20. Source Code Mapping

### Core Backend Bridge
- **File Path**: [server.py](file:///c:/Users/Rudra/OneDrive/Desktop/orichestation/Talent_Forecast/server.py)
  - `run_agent_in_subprocess()`: Executes the Python CLI runner and handles stdout/stderr.
  - `run_historical_analysis()`: Performs similarity matching against historical records.
  - `generate_xai_attribution_backend()`: Maps academic and profile metrics to placement impacts.
- **File Path**: [agent_runner.py](file:///c:/Users/Rudra/OneDrive/Desktop/orichestation/Talent_Forecast/agent_runner.py)
  - `main()`: Loads version-specific environments, updates `sys.path`, parses stdin, and invokes the orchestrator.

### V2 Orchestration Pipeline
- **File Path**: [Agent V2/final/core/orchestrator.py](file:///c:/Users/Rudra/OneDrive/Desktop/orichestation/Talent_Forecast/Agent%20V2/final/core/orchestrator.py)
  - `evaluate_student()`: Spawns agent tasks, coordinates consensus, and manages semantic cache lookups.
  - `llm_smart_parser()`: Cleans raw CSV strings and maps names to available resume PDFs.
- **File Path**: [Agent V2/final/core/blackboard.py](file:///c:/Users/Rudra/OneDrive/Desktop/orichestation/Talent_Forecast/Agent%20V2/final/core/blackboard.py)
  - `SharedBlackboard`: In-memory whiteboard database.
  - `query_skill_validation()`: Performs zero-latency validation lookups.
- **File Path**: [Agent V2/final/core/semantic_cache.py](file:///c:/Users/Rudra/OneDrive/Desktop/orichestation/Talent_Forecast/Agent%20V2/final/core/semantic_cache.py)
  - `SemanticCacheEngine`: Manages local disk caching.
  - `compute_profile_hash()`: Computes candidate hashes using discretized metrics.
- **File Path**: [Agent V2/final/core/agent_communication.py](file:///c:/Users/Rudra/OneDrive/Desktop/orichestation/Talent_Forecast/Agent%20V2/final/core/agent_communication.py)
  - `run_inter_agent_communication()`: Orchestrates the multi-agent consensus debate.
- **File Path**: [Agent V2/final/core/forecasting_agent.py](file:///c:/Users/Rudra/OneDrive/Desktop/orichestation/Talent_Forecast/Agent%20V2/final/core/forecasting_agent.py)
  - `execute_forecast()`: Manages the forecasting pipeline.
  - `calculate_employability_state_machine()`: Evaluates the candidate's employability status.
  - `anchor_semantic_domain()`: Programmatically anchors domain classifications.
  - `mini_rag_salary_lookup()`: Looks up historical salary benchmarks.
  - `validate_forecast_guardrail()`: Enforces Pydantic model validation.

---

## 21. Internal Logic Explanation

### `run_historical_analysis` (`server.py`)
- **Purpose**: Ground predictions in historical institutional data.
- **Approach**: Uses a KNN-like range query over a local Excel sheet, expanding the search window if matching profiles are insufficient.
- **Inputs**: CPI (float), Backlogs (int), DSA Marks (float), English Marks (float), Internships (int), Attendance (float).
- **Outputs**: Dictionary containing matched profiles count, placement rates, salary bands, and top companies.
- **Calls**: Called by FastAPI routes. Calls `parse_salary()` and `parse_placed()`.

### `compute_score` (`resugent/utils.py`)
- **Purpose**: Evaluates candidate resumes against institutional grading standards.
- **Approach**: Computes 8 sub-scores and applies weights based on college year.
- **Inputs**: `ResumeData` Pydantic object and config overrides.
- **Outputs**: Dictionary containing final score and sub-score details.
- **Calls**: Called by `execute_resume_agent()`. Calls `_project_tier()` and `_skill_difficulty()`.

### `calculate_consistency_score` (`Agent V2/agent/mathematics.py`)
- **Purpose**: Evaluates GitHub contribution consistency.
- **Approach**: Computes the coefficient of variation on log-dampened monthly commit counts to prevent single-month spikes from skewing results.
- **Inputs**: Monthly contributions dict.
- **Outputs**: Dictionary with consistency score and statistical details.
- **Calls**: Called by `compile_payload_from_memory()`. Calls `math.log2()`.

### `calculate_employability_state_machine` (`Agent V2/final/core/forecasting_agent.py`)
- **Purpose**: Prevent over-optimistic predictions for candidates with core skill deficiencies.
- **Approach**: Evaluates three core pillars and clamps placement probability to 25% if any pillar falls below thresholds.
- **Inputs**: Resume score, GitHub score, and CP score.
- **Outputs**: Employability status, pillar scores, and maximum allowed placement probability.
- **Calls**: Called by `execute_forecast()`.

### `query_skill_validation` (`Agent V2/final/core/blackboard.py`)
- **Purpose**: Validate resume skill claims against public profiles without calling LLMs.
- **Approach**: Queries GitHub and CP blackboard slots to verify technologies and repository details.
- **Inputs**: `A2ASkillQuery` dict (target skill and thresholds).
- **Outputs**: `A2ASkillResponse` dict (verification status, repo count, commits weight).
- **Calls**: Called by `run_inter_agent_communication()`.

### `compute_profile_hash` (`Agent V2/final/core/semantic_cache.py`)
- **Purpose**: Generate unique hashes for student profiles to enable local caching.
- **Approach**: Discretizes scores into 5-point buckets and appends sorted skills and domains to create a deterministic hash.
- **Inputs**: Master score, primary domain, GitHub/CP/Resume scores, and verified skills list.
- **Outputs**: 16-character SHA256 hex string.
- **Calls**: Called by `evaluate_student()`.

---

## 22. Overall Workflow Summary

The diagram below outlines the end-to-end workflow of the GLA Talent Forecast system:

```
+------------------+     Select Student     +-----------------------+
|  Sidebar panel   | ─────────────────────> | Prediction Sandbox UI |
+------------------+                        +-----------+-----------+
                                                        |
                                                        | Click Forecast
                                                        v
+------------------+     isolated task      +-----------------------+
| agent_runner.py  | <───────────────────── |   FastAPI server.py   |
+--------+---------+                        +-----------+-----------+
         |
         | asyncio.gather()
         v
+-------------------------------------------------------------------+
|                   Concurrent Evaluation Agents                    |
|                                                                   |
|  +------------------+  +------------------+  +------------------+  |
|  |   Resume Agent   |  |   GitHub Agent   |  |     CP Agent     |  |
|  |  (Reads PDF, LLM |  |  (Scrapes repos, |  |  (Fetches APIs,  |  |
|  |   extraction)    |  |   commit logs)   |  |   scrapes HTML)  |  |
|  +--------+---------+  +--------+---------+  +--------+---------+  |
+-----------|---------------------|---------------------|-----------+
            |                     |                     |
            +----------+----------+----------+----------+
                       |
                       v
            +----------------------------------+
            |  Shared Blackboard Memory Slots  | <--- (V2 Engine Only)
            +------------------+---------------+
                               |
                               v
            +----------------------------------+
            | Multi-Agent Consensus Debate Bus |
            +------------------+---------------+
                               |
                               v
            +----------------------------------+
            |    Career Semantic Synthesizer   |
            +------------------+---------------+
                               |
                               v
            +----------------------------------+
            |    Semantic Disk Cache Engine    | <--- (V2 Engine Only)
            +------------------+---------------+
                               |
                               v
            +----------------------------------+
            |  Forecasting & State Machine     |
            +------------------+---------------+
                               |
                               v
            +----------------------------------+
            | Pydantic Exit Guardrails Validator| <--- (V2 Engine Only)
            +------------------+---------------+
                               |
                               v
            +----------------------------------+
            |  FastAPI Historical KNN Matcher  | <--- (Local Excel Database)
            +------------------+---------------+
                               |
                               v
            +----------------------------------+
            |      XAI Attribution Engine      | <--- (Sliders Panel Weights)
            +------------------+---------------+
                               |
                               v
            +----------------------------------+
            |      React Dashboard Render      |
            +----------------------------------+
```
