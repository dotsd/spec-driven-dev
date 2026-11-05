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

## ⚡ Quickstart

### 1. Prerequisites

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** package manager

### 2. Install the CLI

Install the tool globally using `uv`:

```bash
uv tool install git+https://github.com/hasanrafiq-goog/spec-driven-dev.git
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

2. **Capture existing repository norms in the constitution**:

   ```text
   /speckit-constitution Align with our existing patterns in src/: FastAPI, SQLAlchemy 2.0, pytest, and 90%+ branch coverage.
   ```

3. **Specify the enhancement or fix**:

   ```text
   /speckit-specify Fix issue where expired JWT refresh tokens cause a 500 error instead of a 401 Unauthorized response in /auth/refresh.
   ```

4. **Plan with codebase context**:

   ```text
   /speckit-plan
   ```

   The agent inspects existing models, database migrations, and routers to design a surgical change that avoids regressions.

5. **Execute and verify**:

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

## 🛠️ CLI Utilities

Check environment health:

```bash
specify check
```

Manage extensions:

```bash
specify extension list
specify extension add bug
```

Inspect registered artifacts:

```bash
specify artifact list
```

---

## 📄 License

MIT License.
