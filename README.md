# 🚀 Spec-Driven Development Toolkit (`spec-driven-dev`)

> **Build with specifications, plan with architecture, and implement with autonomous coding agents.**

A modern toolkit designed to bring structured, repeatable **Spec-Driven Development (SDD)** to AI coding agents, with first-class native support for Google **Jetski**, **Antigravity**, **Claude Code**, **Cursor**, **GitHub Copilot**, and **Codex**.

---

## 💡 The Philosophy

> *"Specifications don't serve code — code serves specifications."*

Instead of raw prompts that lead to hallucination, context drift, and brittle hacks, `spec-driven-dev` inverts software development:

1. **The Specification is the Source of Truth**: Requirements, invariants, and acceptance criteria are written and tested first.
2. **Deterministic Gating**: Every phase (Constitution → Specification → Planning → Task Decomposition → Implementation → Convergence) is validated before code is produced.
3. **Autonomous Verification**: Agents don't guess when they're done—they verify against the spec until the system converges.

---

## ✨ Key Features & Capabilities

### 1. 🛡️ Deterministic Multi-Stage Gating Pipeline

Spec Kit eliminates AI hallucinations and context drift through an airtight, multi-stage gating process where every phase produces verified, reviewable markdown artifacts:

- **Phase 0 — Project Constitution (`/speckit-constitution`)**: Establish non-negotiable architectural boundaries, coding standards, typing requirements, and testing bars.
- **Phase 1 — Feature Specification (`/speckit-specify`)**: Generate crystal-clear PRDs, user stories, acceptance scenarios (Gherkin style), and measurable success criteria.
- **Phase 1.5 — Socratic Clarification (`/speckit-clarify`)**: Proactively interviews you on up to 5 critical ambiguities and edge cases before technical design begins.
- **Phase 2 — Architectural Planning (`/speckit-plan`)**: Designs technical architecture, database schemas, interfaces, contracts (`contracts/`), and technical prerequisites (`research.md`, `quickstart.md`).
- **Phase 2.5 — Requirements Checklists (`/speckit-checklist`)**: Generates custom requirements-quality verification checklists—acting as "unit tests for your requirements" before breaking work into tasks.
- **Phase 3 — Dependency Task Decomposition (`/speckit-tasks`)**: Breaks implementation plans into discrete, ordered tasks with explicit phase grouping and parallel markers (`[P]`).
- **Phase 3.5 — Cross-Artifact Consistency Analysis (`/speckit-analyze`)**: Non-destructively audits `spec.md` ↔ `plan.md` ↔ `tasks.md` for gaps, orphan tasks, or contradictions before writing code.
- **Phase 4 — Test-Driven Implementation (`/speckit-implement`)**: Builds features incrementally task-by-task, running automated tests and marking tasks complete in real-time.
- **Phase 5 — Self-Healing Convergence (`/speckit-converge`)**: Performs an authoritative spec-to-code gap assessment, comparing the codebase against the spec and appending any missing work as actionable tasks until 100% converged.

### 2. 🤖 Universal Multi-Agent Native Support

One unified toolkit that adapts natively to your team's preferred AI coding assistant:

- **Google Jetski & Antigravity**: Native skills integration in `~/.gemini/skills/` with instant slash-command discovery in the chat UI.
- **Claude Code**: First-class native `.claude/` commands and `CLAUDE.md` instructions.
- **Cursor Agent**: Custom `.cursorrules` and workspace skills.
- **GitHub Copilot**: Tailored agent prompts in `.github/copilot-instructions.md`.
- **Windsurf, Codex, Kimi, Kilocode, Bob, & 20+ more**: Native adapters ensuring consistent project structure across diverse agent fleets.

### 3. 📂 Specification-as-Code Artifact Architecture

Every phase creates version-controlled, human-readable markdown artifacts under `specs/<feature>/`:

- `spec.md`: Functional requirements, user stories, acceptance criteria, and measurable business outcomes.
- `plan.md`: Architectural blueprint, technical choices, and implementation phases.
- `data-model.md`: Domain models, database schemas, and entity relationships.
- `contracts/`: Strict interface definitions (TypeScript interfaces, JSON Schema, OpenAPI, etc.).
- `tasks.md`: Actionable task list with dependencies and progress markers (`- [x]`).
- `quickstart.md`: Step-by-step validation and verification runbook.
- `checklists/`: Custom requirements-quality review checklists.

### 4. 🧠 Unified Architecture Memory & Knowledge Graph

Spec Kit maintains a continuously synchronized, category-based architectural memory in `.specify/memory/architecture/` that unifies technical code, functional PRDs, specifications, and issue tracking:

- **Multi-Language AST Analysis**: Automatically discovers API routes, handlers, database entities, domain models, and import graphs across Python, TypeScript/JavaScript, Go, Rust, Java, SQL, and Prisma.
- **Unified Functional & Work Traceability Matrix**: Connects functional PRDs (`docs/`), active Spec Kit feature specifications (`specs/**`), and JIRA tickets directly to their implementing code components, endpoints, and data models.
- **Modular Knowledge Categories**:
  - `overview.md`: System summary, detected tech stacks, directory conventions, and visual Mermaid system topology.
  - `api-surface.md`: Exhaustive catalog of exposed HTTP/RPC endpoints, CLI commands, and entrypoint handlers.
  - `domain-models.md`: Complete dictionary of database schemas, ORM models, Pydantic models, Zod schemas, and types.
  - `traceability.md`: Functional requirements (`FR-###`, `REQ-###`, `US-###`) and JIRA work tickets mapped to code.
  - `dependencies.md`: Inter-module dependency coupling, hotspots, and blast-radius risk ratings for refactoring.
  - `test-map.md`: Test suite architecture mapping source components to test coverage.
- **Sub-Second Delta Refreshes**: Employs SHA-256 file-hash caching (`.specify/cache/architecture_cache.json`) to re-parse only changed files, keeping memory up to date in milliseconds (~100 ms).
- **Background SDD Integration**: `/speckit-plan` consults existing architecture models to avoid schema duplication, `/speckit-implement` delta-refreshes memory upon task completion, and `/speckit-converge` uses traceability to verify all requirements are implemented.

### 5. 🔌 Extensibility, Lifecycle Hooks & Community Catalog

- **Lifecycle Hook System**: Define custom pre- and post-execution hooks in `.specify/extensions.yml` (`before_plan`, `after_plan`, `before_implement`, `after_implement`, `before_converge`, etc.) to trigger custom linters, security scanners, or automated CI notifications.
- **Extensions & Bundles**: Discover, install, and author reusable Spec Kit extensions, presets, and workflows with `specify extension`, `specify preset`, and `specify bundle`.
- **Automation Workflows**: Script and execute multi-step agent workflows deterministically using `specify workflow`.

---

## ⚡ Quickstart

### 1. Prerequisites

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** package manager

### 2. Install the CLI

Install the tool globally using `uv`:

```bash
uv tool install git+https://github.com/dotsd/spec-driven-dev.git
```

### 3. Initialize in Any Project Directory

Navigate to your project (or an empty folder) and initialize it for your agent:

```bash
# For Google Jetski / Antigravity:
specify init . --integration jetski

# For Claude Code:
specify init . --integration claude

# For Cursor Agent:
specify init . --integration cursor-agent
```

> **Note for Jetski Users**: When initializing with `--integration jetski`, all `/speckit-*` slash commands are automatically linked into `~/.gemini/skills/` so they appear immediately in your chat UI!

---

## 🔄 The SDD Agent Workflow

Run each phase in your agent chat, reviewing outputs along the way:

```text
/speckit-constitution Create principles focused on clean architecture, strict typing, and 100% test coverage.
/speckit-specify Build an asynchronous API health monitoring tool with a live terminal TUI and desktop alerts.
/speckit-plan Use Python 3.12, asyncio, httpx, and Rich for live terminal rendering.
/speckit-tasks
/speckit-implement
/speckit-converge
```

### Slash Commands Reference

| Slash Command | Stage | Purpose |
| :--- | :---: | :--- |
| **`/speckit-code-analyze`** | Audit | Deep architectural analysis: extracts AST, maps functional PRDs/JIRA tickets to code, and builds `.specify/memory/architecture/`. |
| **`/speckit-constitution`** | 0 | Sets non-negotiable project quality bars, tech stack boundaries, and rules. |
| **`/speckit-specify`** | 1 | Generates the functional specification (PRD, user stories, acceptance criteria). |
| **`/speckit-clarify`** | 1.5 | Active interview mode: agent asks targeted questions to resolve ambiguities before planning. |
| **`/speckit-plan`** | 2 | Designs the architecture, technical dependencies, data models, and interface contracts. |
| **`/speckit-checklist`** | 2.5 | Generates requirements-quality verification checklists. |
| **`/speckit-tasks`** | 3 | Decomposes the plan into discrete, dependency-ordered, agent-executable tasks. |
| **`/speckit-analyze`** | 3.5 | Cross-checks consistency between the spec, plan, and tasks to detect gaps before writing code. |
| **`/speckit-implement`** | 4 | Executes tasks incrementally, running automated tests at each step. |
| **`/speckit-converge`** | 5 | Self-healing verification loop comparing actual code against spec until "Converged". |

---

## 🎯 Common User Journeys (CUJs)

### Journey 1: Greenfield Project (Starting from Scratch)

When starting a brand-new project—either from an idea or pre-existing product documentation:

1. **Initialize the workspace**:

   ```bash
   specify init . --integration jetski
   ```

2. **Establish the project constitution**:
   Define non-negotiable tech stack choices, code style, testing bar, and architecture constraints:

   ```text
   /speckit-constitution We build a Next.js 15 app with React Server Components, TypeScript strict mode, Tailwind CSS, and Vitest for testing. All API endpoints must validate input with Zod.
   ```

3. **Ingest requirements or draft the spec**:
   If you have pre-existing PRDs, design documents, or notes, reference or paste them directly:

   ```text
   /speckit-specify Build the MVP described in docs/prd.md with user registration, team workspaces, and role-based permissions.
   ```

4. **Stress-test and clarify ambiguities**:

   ```text
   /speckit-clarify
   ```

   The agent interviews you on up to 5 critical edge cases before designing architecture.

5. **Generate architecture & validate requirements**:

   ```text
   /speckit-plan
   /speckit-checklist
   ```

   `/speckit-plan` designs the system architecture, dependencies, and data schemas. `/speckit-checklist` generates requirements-quality checklists ("unit tests for your requirements") verifying completeness, testability, and edge cases before task breakdown.

6. **Decompose tasks & audit consistency**:

   ```text
   /speckit-tasks
   /speckit-analyze
   ```

   `/speckit-tasks` generates a dependency-ordered task graph. `/speckit-analyze` acts as a quality gate, non-destructively verifying cross-artifact consistency across `spec.md`, `plan.md`, and `tasks.md` to catch coverage gaps or orphaned requirements before writing code.

7. **Implement and converge**:

   ```text
   /speckit-implement
   /speckit-converge
   ```

   The agent builds the project step-by-step with automated tests until the implementation satisfies every acceptance criterion.

---

### Journey 2: Brownfield Project (Existing Codebase Enhancements & Bug Fixes)

When adding a feature or fixing a bug in an existing repository:

1. **Bootstrap Spec Kit into the repo**:

   ```bash
   specify init . --integration jetski
   ```

2. **Map existing codebase architecture & functional documents**:
   Audit the repository to generate the system topology, routes, schemas, and PRD/ticket traceability:

   ```text
   /speckit-code-analyze docs/prd
   ```

   *(Or run `specify architecture generate` via CLI).*

3. **Capture existing repository norms in the constitution**:

   ```text
   /speckit-constitution Align with our existing patterns in src/: FastAPI, SQLAlchemy 2.0, pytest, and 90%+ branch coverage.
   ```

4. **Specify the enhancement or fix**:

   ```text
   /speckit-specify Fix issue where expired JWT refresh tokens cause a 500 error instead of a 401 Unauthorized response in /auth/refresh.
   ```

5. **Plan with codebase context**:

   ```text
   /speckit-plan
   ```

   The agent inspects existing models, database migrations, and routers to design a surgical change that avoids regressions.

6. **Execute and verify**:

   ```text
   /speckit-tasks
   /speckit-analyze
   /speckit-implement
   /speckit-converge
   ```

   The agent breaks work into tasks, audits cross-artifact consistency with `/speckit-analyze`, implements regression tests first, applies the fix, and runs your test suite to ensure green CI.

---

### Journey 3: Mid-Flight Spec Evolution (Handling Missed Requirements)

When you discover mid-way (or after converging) that a requirement was missed or changed:

1. **Update the Spec in-place (do not edit code directly)**:

   ```text
   /speckit-specify We also need a 15-minute expiration window on password reset links and an audit log event written on reset.
   ```

   The agent updates `specs/<feature>/spec.md` with the new requirements without erasing prior context.

2. **Update the plan & append new tasks**:

   ```text
   /speckit-plan
   /speckit-tasks
   ```

   The agent preserves completed tasks (`- [x]`) and appends only the new tasks needed for the requirement change.

3. **Implement remaining work**:

   ```text
   /speckit-implement
   /speckit-converge
   ```

   The agent executes the newly added unchecked tasks and brings the codebase back into full convergence with the updated spec.

---

### Journey 4: Safe Architectural Refactoring

When restructuring complex legacy code without altering business behavior:

1. **Create a characterization spec**:

   ```text
   /speckit-specify Refactor legacy billing calculation service in src/services/billing.py into a modular strategy pattern without changing any existing calculation outputs or API responses.
   ```

2. **Design target architecture and test matrix**:

   ```text
   /speckit-plan
   ```

   Generates a refactoring plan that maps current behavior to the new architecture.

3. **Decompose, build safety harnesses, and execute**:

   ```text
   /speckit-tasks
   /speckit-implement
   /speckit-converge
   ```

   The agent creates comprehensive characterization tests first, refactors module-by-module, and verifies parity against existing test suites.

---

## 📁 Repository Structure

When initialized, projects store version-controlled artifacts in `.specify/`:

```text
my-project/
├── .specify/
│   ├── memory/
│   │   └── constitution.md     # Project principles & core guidelines
│   ├── templates/              # Standard templates for specs, plans, and tasks
│   └── workflows/              # Pipeline definitions
├── specs/                      # Feature specifications & plans
│   └── 001-my-feature/
│       ├── spec.md             # Functional requirements
│       ├── plan.md             # Architecture & technical design
│       ├── data-model.md       # Entity models
│       ├── contracts/          # Interface schemas (JSON Schema, OpenAPI, etc.)
│       ├── tasks.md            # Actionable implementation tasks
│       └── quickstart.md       # End-to-end verification runbook
└── src/                        # Your application source code
```

---

## 🛠️ CLI Utilities Reference

The `specify` CLI provides a complete set of command-line tools for managing projects, extensions, agent integrations, and workflows:

### 1. Project Initialization & Diagnostics

```bash
# Check environment health, installed dependencies, and tool prerequisites
specify check

# Initialize Spec Kit in the current directory for a specific agent
specify init . --integration jetski
specify init . --integration claude

# Display CLI version, architecture, and environment details
specify version
```

### 2. Extension & Community Catalog Management

Extend your Spec-Driven Development workflow with community-contributed extensions and review tools:

```bash
# List all currently installed extensions
specify extension list

# Search for available extensions in the official catalog
specify extension search security

# Install an extension from the catalog
specify extension add bug

# View detailed metadata for an extension
specify extension info bug

# Remove an extension
specify extension remove bug
```

### 3. Workflow Automation & Execution

Script and orchestrate multi-step autonomous pipelines deterministically:

```bash
# List all registered workflows
specify workflow list

# Inspect workflow step graph and execution DAG
specify workflow info feature-pipeline

# Execute an automation workflow
specify workflow run feature-pipeline
```

### 4. Presets, Bundles & Artifact Introspection

```bash
# Discover pre-configured rule presets
specify preset list

# Discover and install curated multi-extension bundles
specify bundle list

# Introspect registered commands, templates, scripts, and lifecycle hooks
specify artifact list
```

### 5. In-Place Self Upgrades

```bash
# Check for newer releases and preview upgrade changes
specify self check

# Upgrade specify-cli in place to the latest release
specify self upgrade
```

---

## 📄 License

MIT License.
