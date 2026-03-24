# Agent Studio Structure Research — CoVe 2026
> Deep research: March 2026 | Sources: 15+ repos, official Anthropic docs, framework comparisons
> **Status**: COMPLETE — ready for FLUXION agent studio implementation

---

## 1. Claude Code Agent Definition — Official Format (2026)

### Frontmatter Schema (COMPLETE)

Agents are defined as `.md` files with YAML frontmatter. Only `name` and `description` are required.

```yaml
---
name: my-agent                    # REQUIRED — lowercase + hyphens only
description: When to use this     # REQUIRED — max 1024 chars, 3rd person
tools: Read, Grep, Glob, Bash    # OPTIONAL — inherits all if omitted
disallowedTools: Write, Edit     # OPTIONAL — denylist (applied before tools)
model: sonnet                    # OPTIONAL — sonnet|opus|haiku|inherit|full-model-id
permissionMode: default          # OPTIONAL — default|acceptEdits|dontAsk|bypassPermissions|plan
maxTurns: 50                     # OPTIONAL — max agentic turns
skills:                          # OPTIONAL — skills to preload into context
  - api-conventions
  - error-handling
mcpServers:                      # OPTIONAL — MCP servers (inline or reference)
  - playwright:
      type: stdio
      command: npx
      args: ["-y", "@playwright/mcp@latest"]
  - github                       # reference to already-configured server
hooks:                           # OPTIONAL — lifecycle hooks (PreToolUse, PostToolUse, Stop)
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate.sh"
memory: project                  # OPTIONAL — user|project|local
background: false                # OPTIONAL — true = always background
effort: high                     # OPTIONAL — low|medium|high|max (Opus 4.6 only)
isolation: worktree              # OPTIONAL — worktree = isolated git copy
---

System prompt goes here in Markdown.
The agent receives ONLY this prompt + basic env details.
NOT the full Claude Code system prompt.
```

### Scope & Priority (highest wins)

| Location | Scope | Priority |
|----------|-------|----------|
| `--agents` CLI flag (JSON) | Current session only | 1 (highest) |
| `.claude/agents/` | Current project | 2 |
| `~/.claude/agents/` | All projects (user) | 3 |
| Plugin `agents/` directory | Where plugin enabled | 4 (lowest) |

### Tool Restriction Patterns

```yaml
# Allowlist — ONLY these tools available
tools: Read, Grep, Glob, Bash

# Denylist — inherit everything EXCEPT these
disallowedTools: Write, Edit

# Restrict which sub-agents can be spawned
tools: Agent(worker, researcher), Read, Bash

# Allow any sub-agent
tools: Agent, Read, Bash
```

### Memory Scopes

| Scope | Location | Use case |
|-------|----------|----------|
| `user` | `~/.claude/agent-memory/<name>/` | Cross-project knowledge |
| `project` | `.claude/agent-memory/<name>/` | Project-specific, git-shared |
| `local` | `.claude/agent-memory-local/<name>/` | Project-specific, NOT in git |

When memory is enabled: agent gets a `MEMORY.md` file (first 200 lines injected into prompt), plus Read/Write/Edit tools auto-enabled.

### Built-in Agents

| Agent | Model | Tools | Purpose |
|-------|-------|-------|---------|
| **Explore** | Haiku | Read-only | Fast codebase search |
| **Plan** | Inherit | Read-only | Research for planning |
| **General-purpose** | Inherit | All | Complex multi-step tasks |

---

## 2. Skills vs Agents — Key Distinction

| Aspect | Agents (subagents) | Skills |
|--------|-------------------|--------|
| Context | Own isolated context window | Runs in main conversation |
| System prompt | Custom (replaces default) | Injected into existing |
| Tool access | Configurable per agent | Inherits from session |
| Memory | Persistent across sessions | No persistent memory |
| Nesting | Cannot spawn other subagents | Can reference other skills |
| Best for | Isolated tasks, parallel work | Reusable knowledge/patterns |

### Skill Best Practices (Anthropic Official)

**SKILL.md frontmatter:**
```yaml
---
name: processing-pdfs           # lowercase, hyphens, max 64 chars
description: Extracts text and tables from PDF files. Use when working with PDF files.
---
```

**Key rules:**
- Keep SKILL.md body **under 500 lines**
- Description in **3rd person** (never "I can help you")
- Include **when to use** in description, not just what it does
- Use **progressive disclosure** — main file points to reference files
- References **one level deep** only (no nested chains)
- Name with **gerund form**: `processing-pdfs`, `testing-code`
- Test with **all model tiers** (Haiku, Sonnet, Opus)

---

## 3. Multi-Agent Studio Structures — Best Repos (2026)

### A. contains-studio/agents — 8 Departments, 37 Agents

**The best organizational model for a product company.** 8 functional departments:

| Department | Agents | Key Roles |
|-----------|--------|-----------|
| **Engineering** (7) | rapid-prototyper, backend-architect, frontend-developer, mobile-app-builder, ai-engineer, devops-automator, test-writer-fixer |
| **Product** (3) | trend-researcher, feedback-synthesizer, sprint-prioritizer |
| **Marketing** (7) | growth-hacker, content-creator, tiktok-strategist, twitter-engager, instagram-curator, reddit-community-builder, app-store-optimizer |
| **Design** (5) | whimsy-injector, ui-designer, brand-guardian, ux-researcher, visual-storyteller |
| **Project Management** (3) | (coordination, sprint, tracking) |
| **Studio Operations** (5) | analytics-reporter, finance-tracker, infrastructure-maintainer, legal-compliance-checker, support-responder |
| **Testing** (5) | (QA, E2E, integration, regression, performance) |
| **Bonus** (2) | (morale, support) |

**Key pattern:** Description field has 3-4 detailed usage examples. System prompts are 500+ words. Color-coded for visual identification.

### B. lst97/claude-code-sub-agents — 33 Agents, 7 Categories

```
agents/
├── development/         (11 agents)
├── infrastructure/      (5 agents)
├── quality-testing/     (5 agents)
├── data-ai/             (8 agents)
├── security/            (1 agent)
├── specialization/      (2 agents)
└── business/            (1 agent)
```

**Key pattern:** JSON request/response protocol between agents. Meta-orchestrator agent (`agent-organizer`) coordinates workflows.

### C. VoltAgent/awesome-claude-code-subagents — 127+ Agents, 10 Categories as Plugins

| Category | Plugin Name | Count | Examples |
|----------|------------|-------|----------|
| Core Development | `voltagent-core-dev` | 10 | api-designer, frontend-dev, fullstack |
| Language Specialists | `voltagent-lang` | 30+ | typescript-pro, python-pro, rust-engineer |
| Infrastructure | `voltagent-infra` | 16 | cloud-architect, kubernetes-specialist |
| Quality & Security | `voltagent-qa-sec` | 14 | code-reviewer, penetration-tester |
| Data & AI | `voltagent-data-ai` | 13 | llm-architect, prompt-engineer |
| Developer Experience | `voltagent-dev-exp` | 13 | dx-optimizer, git-workflow-manager |
| Specialized Domains | `voltagent-domains` | 12 | fintech-engineer, seo-specialist |
| Business & Product | `voltagent-biz` | 11 | product-manager, content-marketer |
| Meta & Orchestration | `voltagent-meta` | 11 | workflow-orchestrator, task-distributor |
| Research & Analysis | `voltagent-research` | 7 | competitive-analyst, trend-analyst |

**Key pattern:** Plugin-based distribution. Model tier strategy (Opus for critical, Haiku for fast ops).

### D. vijaythecoder/awesome-claude-agents — 24 Agents, 4 Teams

| Team | Count | Key Roles |
|------|-------|-----------|
| **Orchestrators** (3) | Tech Lead, Project Analyst, Team Configurator |
| **Framework Specialists** (13) | Laravel, Django, Rails, React, Vue experts |
| **Universal Experts** (4) | Backend, Frontend, API Architect, Tailwind |
| **Core Team** (4) | Code Archaeologist, Reviewer, Performance, Docs |

**Key pattern:** Team Configurator auto-detects project stack and maps agents.

### E. wshobson/agents — 112 Agents, 72 Plugins, 146 Skills

**Most sophisticated architecture.** Model tier strategy:

| Tier | Model | Agent Count | Purpose |
|------|-------|-------------|---------|
| 1 | Opus 4.6 | 42 | Critical architecture, security, code review |
| 2 | Inherit | 42 | Complex tasks (user chooses model) |
| 3 | Sonnet 4.6 | 51 | Support with intelligence |
| 4 | Haiku 4.5 | 18 | Fast operational tasks |

**16 workflow orchestrators** for complex operations (full-stack feature dev, security audit, migration).

### F. Gentleman-Programming/agent-teams-lite — Orchestrator + 9 Agents

**Spec-Driven Development (SDD) pattern:**

```
EXPLORER → PROPOSER → SPEC WRITER → DESIGNER → TASK PLANNER → IMPLEMENTER → VERIFIER → ARCHIVER
```

**Key insight:** Orchestrator NEVER does real work. Delegates everything. Saves 50-70% tokens.

### G. kourosh-forti-hands/agent-team-templates — 3 Team Topologies

| Topology | Pattern | Use Case |
|----------|---------|----------|
| **Solo** | Sequential Task() calls | Least expensive |
| **Squad** | One persistent team | Task dependencies across phases |
| **Swarm** | Per-wave team creation | Maximum parallel throughput |

Both models share 7 phases: Bootstrap → Assessment → Foundation → Features → Client Integration → Deployment → Validation.

---

## 4. obra/superpowers — The Gold Standard Skill Framework

**Core philosophy:** If a skill applies, you MUST use it. No skipping on "simple" tasks.

**5 automatic skills:**
1. **Brainstorming** — Before writing code. Refines ideas through questions.
2. **Git Worktrees** — After design approval. Isolated workspace.
3. **Writing Plans** — Breaks work into 2-5 min tasks with exact file paths.
4. **Test-Driven Development** — RED-GREEN-REFACTOR strictly enforced.
5. **Subagent-Driven Development** — Dispatches fresh subagent per task with two-stage review.

**Writing Skills skill** teaches creating new skills with TDD:
- No skill without a failing test first
- Description states **when to use** (not what it does)
- Token budgets: <150 words for getting-started, <500 words for others
- CSO (Claude Search Optimization): include error messages, symptoms, synonyms
- Bulletproof against rationalization — explicit loophole closing

---

## 5. Agent Teams (Official Claude Code Feature)

**Experimental feature** (requires Opus 4.6 + env var).

### Lead-Teammate Model
- **Lead**: Breaks tasks, spawns teammates, synthesizes
- **Teammates**: Independent 1M context windows, claim tasks via lock files

### Coordination
- Git-based task claiming (`.claude/tasks/` directory)
- Peer-to-peer messaging between teammates
- Optimal team size: **2-3 agents** (>5 causes coordination overhead)

### Real-World Metrics (Anthropic Internal)
- Code screening: 50% faster
- PR merges/day: 67% more
- New work created: 27% of tasks wouldn't exist without AI

---

## 6. Framework Comparison (CrewAI, AutoGen, Agency-Swarm)

| Framework | Pattern | Best For |
|-----------|---------|----------|
| **CrewAI** | Role-driven + hierarchical manager | Team-based with clear roles |
| **AutoGen** | Event-driven async conversations | Enterprise scalability |
| **LangGraph** | State machine graph | Complex conditional flows |
| **Agency-Swarm** | Agent-initiated handoffs | Flexible routing |

**2025-2026 trend:** Moving from centralized orchestration toward agent-initiated handoffs (Swarm pattern). Modular ecosystems where a LangGraph "brain" might orchestrate a CrewAI "marketing team."

---

## 7. What Agents Does FLUXION Actually Need?

### Recommended Agent Studio for Indie Desktop App + Landing + Video Marketing

Based on all research, here's the **minimum viable agent studio** for FLUXION:

#### TIER 1 — Core Development (MUST HAVE)

```
.claude/agents/
├── dev-frontend.md          # React 19 + TypeScript + Tauri UI
├── dev-backend.md           # Rust/Tauri commands + SQLite
├── dev-voice-agent.md       # Python voice pipeline (Sara)
├── code-reviewer.md         # Security + quality + TypeScript strict
├── debugger.md              # Root cause analysis + fix
```

#### TIER 2 — Quality & Architecture (HIGH VALUE)

```
├── test-writer.md           # Unit + integration + E2E tests
├── performance-optimizer.md # Bundle size, latency, memory
├── db-architect.md          # SQLite migrations, WAL, queries
├── ux-auditor.md            # Accessibility, responsive, PMI UX
```

#### TIER 3 — Marketing & Growth (REVENUE CRITICAL)

```
├── landing-optimizer.md     # Conversion optimization, copy, A/B
├── video-producer.md        # Storyboard, ffmpeg, Veo 3 prompts
├── seo-specialist.md        # YouTube SEO, meta tags, schema
├── copywriter-pmi.md        # Italian PMI copy, PAS formula
```

#### TIER 4 — Operations & Infrastructure

```
├── cf-worker-deployer.md    # Cloudflare Workers + Pages deploy
├── release-manager.md       # Build, sign, package, distribute
├── support-automator.md     # FAQ generation, self-service docs
```

#### TIER 5 — Meta & Orchestration

```
├── research-agent.md        # Deep research CoVe 2026 pattern
├── plan-executor.md         # GSD phase planning + execution
```

**Total: 17 agents** — focused, no bloat.

### What's Commonly MISSING in Most Setups

Based on analyzing 15+ repos and 300+ agent definitions:

1. **Domain-specific language agents** — Most repos are English-only. FLUXION needs Italian PMI vocabulary, legal terms, fiscal language baked into agents.

2. **Revenue/conversion agents** — Engineering teams over-index on dev agents. Marketing/conversion agents are rare but critical for indie products.

3. **Cross-agent memory** — Few setups use the `memory` field. Agents that accumulate project knowledge over time are dramatically more effective.

4. **Model tier strategy** — Most use `inherit` for everything. The best setups (wshobson) use Opus for critical tasks, Sonnet for support, Haiku for fast ops. Saves cost without losing quality.

5. **Hooks for validation** — PreToolUse hooks are underutilized. They can enforce coding standards, prevent destructive commands, validate SQL queries automatically.

6. **Skill preloading** — The `skills` field is rarely used but powerful. Injecting domain knowledge (API conventions, coding standards) into agents at startup eliminates repeated context-building.

7. **Background agents** — Few setups leverage `background: true` for long-running tasks (test suites, research, builds).

8. **Isolation via worktrees** — `isolation: worktree` gives agents their own git copy. Critical for parallel development but almost never used.

9. **Progressive disclosure in descriptions** — Most descriptions are vague ("helps with code"). The best trigger on specific scenarios with 3-4 concrete examples.

10. **Operations agents** — Legal compliance, finance tracking, analytics reporting are almost always missing. Critical for indie businesses.

---

## 8. Best Practices Summary — Gold Standard Agent Definition

### Template: Perfect Agent Definition

```markdown
---
name: dev-frontend
description: >
  React 19 + TypeScript frontend development specialist for Tauri desktop apps.
  Use when: implementing UI components, fixing TypeScript errors, adding
  responsive layouts, integrating with Tauri commands, or polishing UX for
  Italian PMI users. Triggers on: tsx files, component creation, CSS/styling,
  accessibility audits, form validation.
tools: Read, Edit, Write, Bash, Grep, Glob
model: sonnet
memory: project
skills:
  - fluxion-tauri-architecture
  - ui-ux-conventions
effort: high
---

You are a senior frontend developer specializing in React 19 + TypeScript
for Tauri 2.x desktop applications targeting Italian PMI (1-15 employees).

## Core Rules
- TypeScript strict mode: zero `any`, zero `@ts-ignore`
- All component props typed with interfaces
- Italian field names in API: `servizio`, `data`, `ora`, `cliente_id`
- Responsive from 1366x768 to 4K
- Follow existing component patterns in src/components/

## Before Making Changes
1. Read the relevant existing components
2. Check src/types/ for existing type definitions
3. Verify with `npm run type-check` after every edit

## Output Format
- Explain the approach in 2-3 sentences
- Make atomic changes (one concern per edit)
- Verify type-check passes before reporting done

## What NOT to Do
- Never use `console.log` in production code
- Never add dependencies without checking alternatives
- Never modify Rust/Tauri commands (backend team only)
```

### Checklist for Writing Agent Definitions

- [ ] `name`: lowercase + hyphens, descriptive
- [ ] `description`: 3rd person, includes "Use when:" triggers, 100-200 chars
- [ ] `tools`: Explicit allowlist (not inherit-all) for safety
- [ ] `model`: Chosen by task complexity (haiku=fast, sonnet=balanced, opus=critical)
- [ ] `memory`: `project` for shared knowledge, `user` for cross-project
- [ ] `skills`: Preload relevant domain knowledge
- [ ] System prompt: Under 500 lines, focused on ONE domain
- [ ] Includes "What NOT to Do" section (prevents common mistakes)
- [ ] Includes verification step ("run type-check", "run tests")
- [ ] Tested with real tasks before deploying

---

## Sources

### Official Documentation
- [Claude Code Subagents](https://code.claude.com/docs/en/sub-agents) — Complete official reference
- [Skill Authoring Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — Anthropic official guide
- [Claude Code Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

### GitHub Repositories (Agent Collections)
- [contains-studio/agents](https://github.com/contains-studio/agents) — 8-department studio structure (37 agents)
- [lst97/claude-code-sub-agents](https://github.com/lst97/claude-code-sub-agents) — 33 agents, 7 categories
- [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) — 127+ agents, plugin-based
- [vijaythecoder/awesome-claude-agents](https://github.com/vijaythecoder/awesome-claude-agents) — 24 agents, 4 teams
- [wshobson/agents](https://github.com/wshobson/agents) — 112 agents, 72 plugins, model tier strategy
- [Gentleman-Programming/agent-teams-lite](https://github.com/Gentleman-Programming/agent-teams-lite) — SDD orchestrator + 9 agents
- [kourosh-forti-hands/agent-team-templates](https://github.com/kourosh-forti-hands/agent-team-templates) — Solo/Squad/Swarm topologies
- [obra/superpowers](https://github.com/obra/superpowers) — Gold standard skill framework
- [FlorianBruniaux/claude-code-ultimate-guide](https://github.com/FlorianBruniaux/claude-code-ultimate-guide/blob/main/guide/workflows/agent-teams.md) — Agent teams guide

### Framework Comparisons
- [Top 10 AI Agent Frameworks 2026](https://o-mega.ai/articles/langgraph-vs-crewai-vs-autogen-top-10-agent-frameworks-2026)
- [Multi-Agent Frameworks for Enterprise](https://www.adopt.ai/blog/multi-agent-frameworks)
- [CrewAI vs LangGraph vs AutoGen](https://www.datacamp.com/tutorial/crewai-vs-langgraph-vs-autogen)

### Guides & Articles
- [Claude Agent Skills Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)
- [Best Practices for Claude Code Subagents](https://www.pubnub.com/blog/best-practices-for-claude-code-sub-agents/)
- [Superpowers: Complete Guide 2026](https://www.pasqualepillitteri.it/en/news/215/superpowers-claude-code-complete-guide)
- [Build SaaS with AI 2026](https://www.swfte.com/blog/build-saas-with-ai-2026)
- [One-Person Startup with Claude Code](https://stormy.ai/blog/one-person-billion-dollar-startup-claude-code-ai-agents)
