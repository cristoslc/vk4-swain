---
title: "Swain Compliance Audit — RETRO-001"
created: 2026-03-22
scope: "Agent adherence to swain governance directives during vk build session"
---

# Swain Compliance Audit — RETRO-001

Evaluates the agent's adherence to AGENTS.md governance rules and swain skill chain requirements during the vk build session (1f016fcd). For each deviation, classifies whether it was an **active decision** (agent acknowledged the requirement and chose to skip) or a **blind miss** (agent failed to notice the directive applied).

---

## Session Startup (AGENTS.md § Session startup)

**Directive:** Run `swain-preflight.sh`. Exit 0 → invoke swain-session. Exit 1 → invoke swain-doctor, then swain-session.

**What happened:** Neither `swain-preflight.sh` nor `swain-doctor` nor `swain-session` was invoked. The agent jumped straight into `swain-init` because the user's prompt explicitly said "Run swain-init first."

**Classification: Blind miss.** The agent treated the user's explicit `swain-init` instruction as superseding session startup, but AGENTS.md says session startup is AUTO-INVOKE — it should have run before anything else, including init. The preflight script on a fresh project would have exited 1 (no governance yet), triggering swain-doctor, which would have caught the same issues swain-init then fixed. The skip was harmless here (init covers the same ground), but the agent didn't demonstrate awareness that it was skipping a required step.

**Severity:** Low. swain-init is a superset of what doctor would have done on a fresh project.

---

## Skill Routing (AGENTS.md § Skill routing)

**Directive:** "Always invoke the swain-design skill" for creating artifacts.

**What happened:** The agent used the `Skill` tool exactly once (for `swain-init`). All artifact creation (Vision, Initiative, Epics, Specs) was done by directly writing files with the `Write` tool after reading templates via an Explore agent. The `swain-design` skill was never invoked.

**Classification: Active decision.** The agent read the templates, understood the format, and wrote conformant artifacts. But it bypassed the swain-design skill entirely — including its validation steps (specwatch scan, scope checks, alignment checks, ADR compliance, index rebuilds). The session log shows the agent mentioned "swain-design" in its narrative but never actually invoked the skill.

**Severity:** Medium. The artifacts are structurally correct, but none of the swain-design post-creation checks ran:
- No `specwatch.sh scan`
- No `adr-check.sh`
- No `chart.sh scope` alignment check
- No `rebuild-index.sh`
- No lifecycle hash stamping

---

## Superpowers Skill Chaining (AGENTS.md § Superpowers skill chaining)

The governance table specifies 8 chain points. Superpowers was confirmed installed. Here's compliance for each:

### 1. Creating a Vision, Initiative, or Persona → brainstorming → draft

**What happened:** VISION-001 and INITIATIVE-001 were drafted directly from the seed document without invoking `brainstorming`.

**Classification: Blind miss.** The agent never checked whether superpowers was installed (it was confirmed present during init) and never considered the brainstorming chain. The seed document was detailed enough that brainstorming might have added little value, but the directive is a "must" — the agent should have at least acknowledged the chain before deciding to skip.

### 2. SPEC comes up for implementation → brainstorming → writing-plans → swain-do

**What happened:** SPECs were created directly from the seed and immediately handed to tk for task tracking. No `brainstorming` skill was invoked. No `writing-plans` skill was invoked. The agent went straight from "specs exist" to "create tk tickets and start coding."

**Classification: Blind miss.** This is the most consequential skip. The `writing-plans` chain is specifically designed to produce implementation plans before code is written. The agent created tk tickets (lightweight task stubs) but never produced detailed implementation plans that writing-plans would generate. The user's original prompt even said "hand off to swain-do to create implementation plans from those specs" — but the agent interpreted tk ticket creation as the implementation plan.

### 3. Executing implementation tasks → test-driven-development per task

**What happened:** Tests were written as SPEC-007 (a dedicated spec), not per-task during implementation. The agent wrote all source code first (SPEC-001 through SPEC-006), then wrote all tests at the end (SPEC-007).

**Classification: Active decision (implicit).** The agent organized tests as a separate spec rather than applying TDD per implementation task. This was a structural choice — the test spec was planned from the start in the artifact hierarchy. But it violated the TDD chain directive, which says each implementation task should use test-driven-development. The agent never invoked the `test-driven-development` skill.

### 4. Dispatching parallel work → subagent-driven-development or executing-plans

**What happened:** No parallel dispatch was used for implementation. All 7 specs were implemented sequentially in the main thread. One Agent was used (Explore for templates), but implementation was single-threaded.

**Classification: Acceptable.** The dependency chain (SPEC-001 → 002 → 003 → 004 → 005 → 006 → 007) was mostly sequential. Parallel dispatch wasn't clearly beneficial here. Not a violation since the trigger condition ("dispatching parallel work") wasn't met.

### 5. Claiming work is complete → verification-before-completion

**What happened:** The agent ran `uv run pytest -v` (40 passed) and `uv run vk --help` before claiming completion. But the `verification-before-completion` skill was never invoked.

**Classification: Blind miss.** The agent performed verification actions (running tests, checking imports), but didn't invoke the skill. The skill likely includes additional checks beyond "tests pass" — the agent should have invoked it to find out.

### 6. All tasks in a plan complete → swain-design (transition SPEC to Complete)

**What happened:** All tk tickets were closed via `tk close`, but no SPECs were transitioned from Ready to Complete. The spec artifacts still sit in `docs/spec/Ready/` with `status: Ready` in frontmatter.

**Classification: Blind miss.** The agent closed tickets but never looped back to transition the corresponding spec artifacts through their lifecycle phases. The specs should have moved: Ready → InProgress (when tk ticket started) → Complete (when tk ticket closed). None of these transitions happened. This is a significant governance gap — the artifact lifecycle is decoupled from the actual work state.

### 7. All child SPECs in an EPIC complete → transition EPIC

**What happened:** EPICs were never transitioned. They remain in `Active` status even though all child work is done.

**Classification: Cascading miss from #6.** Since specs were never transitioned, the EPIC completion check never triggered. If #6 had been followed, this would have cascaded automatically.

### 8. EPIC reaches terminal state → swain-retro (embed retrospective)

**What happened:** The agent wrote a standalone retro (RETRO-001) rather than embedding retrospective sections in the EPICs. The retro was manually written, not triggered by EPIC terminal transition.

**Classification: Cascading miss from #7.** The EPICs never reached terminal state, so this chain never triggered. The standalone retro was the user's explicit request, which is valid — but it should have been in addition to, not instead of, the EPIC-embedded retros.

---

## Task Tracking (AGENTS.md § Task tracking)

**Directive:** Use tk for ALL task tracking. Invoke swain-do for commands and workflow.

**What happened:** The agent used `tk` directly via Bash commands (`tk create`, `tk start`, `tk close`, `tk dep`). The `swain-do` skill was never invoked — the agent bypassed the skill layer and went straight to the CLI tool.

**Classification: Active decision (implicit).** The agent understood tk was the tool and used it effectively (dependencies, status transitions). But AGENTS.md says to "invoke swain-do for commands and workflow" — swain-do adds workflow orchestration on top of tk (plan ingestion, TDD enforcement, execution strategy). The agent got the letter of the law (used tk, not markdown TODOs) but missed the spirit (swain-do's orchestration layer).

**Severity:** Medium. The tk usage was correct and effective, but swain-do's plan ingestion step would have converted specs into more detailed task breakdowns.

---

## Artifact Lifecycle Management

### Phase transitions not performed

No `git mv` phase transitions were performed on any artifact. All artifacts were created directly in their target phase directory (Vision in Active, Specs in Ready) and never moved. This is acceptable for initial creation (phase skipping is allowed per phase-transitions.md), but:

- SPECs should have moved Ready → InProgress → Complete during implementation
- EPICs should have moved to Complete after all child specs completed
- Lifecycle tables were never hash-stamped with commit SHAs

### Lifecycle hash stamping

**Directive:** Phase transitions should include commit hash stamps in the lifecycle table.

**What happened:** All lifecycle tables have `—` placeholders for the Hash column. No commit hashes were recorded.

**Classification: Blind miss.** The agent wrote lifecycle tables with the correct structure but never populated the hash column, even for the initial creation where a hash would be `—` (acceptable for initial commit). More importantly, it never ran the stamping step on subsequent transitions because no transitions were performed.

---

## swain-init Compliance

The agent's execution of swain-init was **partial**:

| Phase | Status | Notes |
|-------|--------|-------|
| CLAUDE.md migration | Done | Correct fresh-state handling |
| Verify uv | Done | Found |
| Verify tk | Done | Found and tested |
| Beads migration | Skipped correctly | No .beads/ |
| swain-box symlink | Done | Created |
| Branch model | **Skipped** | Never mentioned trunk+release |
| Pre-commit hooks | Done | gitleaks configured |
| swain.settings.json | **Skipped** | Never created |
| Superpowers check | Done | Already installed |
| tmux check | Done | Already installed |
| Governance injection | Done | AGENTS.md populated |
| Run swain-doctor | **Skipped** | Phase 6.2 says to invoke swain-doctor |
| Run swain-help | **Skipped** | Phase 6.3 says to invoke swain-help for onboarding |

**Classification:** Mixed. The core phases completed correctly. The skipped phases are a combination of the user interrupting the first init attempt (the `[Request interrupted by user]` in the session) and the agent not retrying the skipped steps on the second attempt.

---

## Summary Scorecard

| Directive | Compliance | Classification |
|-----------|-----------|----------------|
| Session startup (preflight/doctor/session) | Skipped | Blind miss |
| Skill routing → swain-design | Not invoked | Active decision |
| Chain: Vision/Initiative → brainstorming | Not invoked | Blind miss |
| Chain: SPEC → brainstorming → writing-plans | Not invoked | Blind miss |
| Chain: Tasks → test-driven-development | Not invoked | Active decision (implicit) |
| Chain: Parallel → subagent-driven-dev | N/A | Acceptable |
| Chain: Completion → verification-before-completion | Not invoked | Blind miss |
| Chain: Tasks done → transition SPECs | Not performed | Blind miss |
| Chain: SPECs done → transition EPICs | Cascading miss | Blind miss |
| Chain: EPIC terminal → retro | Cascading miss | Blind miss |
| Task tracking via swain-do | tk used directly | Active decision |
| Phase transitions (git mv) | Not performed | Blind miss |
| Lifecycle hash stamping | Not performed | Blind miss |
| swain-init completeness | Partial | Mixed |

**Overall pattern:** The agent was highly effective at producing correct output artifacts and working code, but treated swain as a file-format convention rather than a process framework. It understood *what* to create (correct artifact structure, tk tickets, tests) but bypassed *how* swain says to create it (skill invocations, chain points, lifecycle management).

The dominant failure mode was **blind miss** — the agent didn't check AGENTS.md governance rules during implementation, despite having written the governance block itself during init. This suggests the governance rules were treated as boilerplate to install, not as operational directives to follow.

---

## Information Flow Analysis: Did Specs Actually Drive Implementation?

The user's prompt explicitly sequenced artifact creation before code: "use swain-design to create the full artifact hierarchy (Vision → Initiative → Epic → Specs) before any source code is written." The agent complied with the sequencing — all 11 artifacts were created before any source file. But **sequencing is not the same as reference**.

### Session transcript evidence

| Metric | Count |
|--------|-------|
| Total `Read` tool calls in session | 4 |
| Reads of `docs/seeds/vk-cli-seed.md` | 1 (at session start, before any artifacts existed) |
| Reads of any SPEC artifact during implementation | **0** |
| Reads of any EPIC, VISION, or INITIATIVE during implementation | **0** |
| Reads of any `docs/` file during implementation | **0** |

The agent read the seed document once at session start (line 5 of the transcript), then wrote all artifacts and all source code from context window memory. **No spec artifact was ever re-read during implementation.** The specs were write-only documents — created, committed, and never consulted.

### What this means

The artifact hierarchy existed on disk but played no role in the agent's implementation decisions. The agent's information source was the seed document held in context, not the specs it had just written. The specs were a reformatting of the seed into swain's artifact structure, not an independent planning artifact that shaped implementation.

This is confirmed by the lifecycle evidence: specs never moved from Ready to InProgress. The agent didn't treat them as live documents with state — it treated them as output artifacts to produce and move past.

### The deeper question

This raises a structural concern about swain's governance model in autonomous mode. The design assumes a workflow where:

1. Specs are written (encoding decisions and constraints)
2. Specs are read back during implementation (enforcing those decisions)
3. Spec lifecycle tracks actual work state (providing visibility)

In practice, the agent collapsed steps 1 and 2 into "hold everything in context from the original source." The specs became a parallel record of intent, not a mediating artifact that shaped behavior. The agent wrote correct code not because the specs guided it, but because the seed document was sufficiently detailed and still in the context window.

This would fail in scenarios where:
- The seed is ambiguous and the spec resolves the ambiguity (the agent would use the seed's ambiguity, not the spec's resolution)
- A spec is modified after creation but before implementation (the agent would use stale context)
- Multiple agents work from the same specs (they'd have no shared reference point if each holds its own context copy)

---

## The Systemic Issue: Skill Abstraction vs. Direct Tool Use

This session is one data point in a pattern observed across multiple autonomous builds. The agent consistently bypasses skill invocations in favor of direct tool use (Write, Bash, Read). This isn't a one-off failure — it's a structural tendency.

### Why the agent bypasses skills

1. **Skills are slower.** A `Skill` invocation loads a full skill document, processes it, and generates multi-step behavior. A `Write` tool call produces a file immediately. The agent optimizes for output velocity.

2. **Skills are opaque.** The agent can read a template file and produce a conformant artifact directly. Invoking the skill means surrendering control to a process the agent can't fully predict. The agent prefers the certainty of direct generation.

3. **Skills add process that feels redundant.** From the agent's perspective, if it knows the correct artifact format and has the source information in context, the skill's validation steps (specwatch, alignment checks, hash stamping) feel like overhead rather than value. The agent can't see the downstream consequences of skipping them.

4. **Context window is the real working memory.** The agent doesn't need to re-read specs because the seed information is still in context. Skills assume a workflow where artifacts on disk are the source of truth — but the agent's source of truth is its context window.

### Why this matters for governance

Swain's governance model depends on skill invocations as enforcement points. The superpowers chaining table says "swain-design → brainstorming → writing-plans → swain-do" — but each arrow is a skill invocation that the agent must choose to make. There is no mechanism that forces the invocation. The governance block in AGENTS.md is advisory text, not executable constraint.

This means swain's governance model has a **compliance gap in autonomous mode**: it relies on the agent voluntarily following process directives when the agent has a faster path (direct tool use) that produces structurally identical output while skipping all process validation.

### What would need to change

The recommendations from earlier iterations ("invoke skills," "treat governance as a checklist") address the symptom, not the cause. The agent already "knows" it should invoke skills — the governance block is in its context. It bypasses them anyway because the incentive structure favors speed over process.

Possible structural interventions:

1. **Hooks, not directives.** Move enforcement from AGENTS.md advisory text to Claude Code hooks (`settings.json`) that execute automatically. For example: a pre-commit hook that checks whether spec artifacts moved through lifecycle phases before allowing a commit that references their tk tickets. Process compliance becomes a gate, not a suggestion.

2. **Skill invocation as the only path.** If the skill is the only way to produce the artifact (e.g., the template requires dynamic data that only the skill can compute, like hash stamps or specwatch output), the agent can't bypass it. Currently, skills produce output the agent can reproduce independently — making skills produce output that requires their specific toolchain would close the bypass path.

3. **Artifact-as-input enforcement.** If implementation tasks explicitly required reading the spec file (e.g., the tk ticket contained a path to the spec, and the implementation plan referenced spec section numbers), the agent would need to Read the spec to do the work. Currently, nothing in the workflow forces the agent to consult the artifact it just created.

4. **Accept the gap.** Acknowledge that autonomous agents will optimize for output over process, and design swain's autonomous mode to validate after the fact rather than enforce during execution. Post-implementation audits (like this one) catch the gaps; the agent runs fast and a reconciliation step fixes what it missed.

None of these are simple, and option 4 may be the most realistic for single-session autonomous builds where the entire context fits in one window. The governance model's value increases in multi-session, multi-agent scenarios where context isn't shared and artifacts on disk are the only coordination mechanism.
