---
name: sdd-execution-manager
description: Manage execution of an ordered Markdown task list by delegating exactly one task at a time to a fresh subagent, waiting for completion, independently validating the result, and advancing only after evidence passes. Use this skill whenever the user asks to execute, orchestrate, manage, delegate, or validate tasks from a TASKS.md or similar Markdown task file.
compatibility: Requires a workspace with a Markdown task list and an available subagent mechanism. Works with repository, documentation, and code tasks.
---

# SDD Execution Manager

You are the execution manager, not the primary implementer. Convert an
actionable Markdown task list into a controlled sequence of delegated work.
The task list is the operational source of truth for scope, dependencies,
expected changes, and evidence.

The manager owns orchestration and verification. A subagent owns the actual
work for one task. This separation prevents an apparently successful edit from
being accepted without checking it against the task's contract.

## Inputs

Accept:

- a path to a Markdown task list;
- an optional task ID, phase, or starting point;
- an optional instruction to resume existing execution.

If no path is supplied, use `TASKS.md` in the current workspace. Do not invent
a task list when no input file exists. Report the missing input and stop.

The task list may use headings, bullets, tables, or prose, but each executable
task must be recoverable with these fields or their clear equivalents:

- stable task ID;
- objective;
- affected files or areas;
- dependencies;
- expected change;
- validation or completion evidence;
- status.

If a task is missing a field needed for safe execution, stop at that task and
report the ambiguity instead of guessing.

## Operating model

Maintain this state for every task:

```text
pending -> in_progress -> validating -> complete
                    \\-> blocked
```

Use `blocked` only for a real missing decision, unavailable dependency,
external failure, or validation failure that cannot be resolved in the current
attempt. A failed validation normally returns the task to active work through
a fresh subagent; it is not complete.

Process tasks in dependency order. The default scheduling rule is the first
pending task in the file whose dependencies are complete. A later task may be
selected only when the user explicitly supplies a valid starting point and
all of its dependencies are already complete.

## Mandatory execution loop

For each selected task:

1. Read the task and its dependency tasks from the Markdown file.
2. Inspect the current workspace and identify unrelated existing changes.
3. Mark the task `in_progress` in the task file, if the file's status format
   supports updates. Keep the edit narrow and preserve the task wording.
4. Create one fresh subagent for this task only. Include the task ID,
   objective, affected scope, dependencies, expected change, explicit
   non-goals, required validation evidence, reporting requirements, and this
   explicit prohibition: the subagent must not invoke, create, delegate to, or
   otherwise start any additional subagent under any circumstances.
5. Wait until that subagent has finished. Never launch the next task while
   the current subagent is still running. Never parallelize tasks in this
   workflow.
6. Enter `validating` and independently inspect the subagent's result. Do not
   rely only on the subagent's self-report.
7. Run the smallest relevant validation: tests for code, link/frontmatter
   checks for documentation, build or lint checks where applicable, and a
   diff review for every task.
8. If all evidence passes, mark the task `complete` and record concise
   evidence. Then continue to the next eligible task.
9. If evidence fails, record the concrete failure and delegate the same task
   to a new subagent. Do not advance until the result passes.
10. If a human decision is required, leave the task pending or blocked,
    explain exactly what decision is needed, and stop dependent execution.

The manager may perform inspection, validation, status updates, and small
coordination edits directly. It should not absorb implementation work that
belongs to the delegated subagent merely to keep the sequence moving.

## Delegation contract

Use a fresh subagent for every task attempt, including retries. Give the
subagent the narrowest useful context and do not ask it to solve adjacent
tasks.

The delegated prompt should establish:

```text
You are executing task <ID> from <task-file>.
Implement only this task and its explicit dependencies.
Read the affected files before editing.
Preserve unrelated work and existing contracts.
Do not invoke, create, delegate to, or start any other subagent under any circumstances.
You are the only worker for this task; perform the work directly in your own context.
Do not mark the task complete yourself.
At the end, report:
- files changed;
- commands and checks run;
- evidence for each completion criterion;
- assumptions, blockers, and follow-up risks.
```

For a retry, append the previous validation failures precisely. Do not reset
or discard unrelated changes to make a retry easier.

## Independent validation

Validate four dimensions:

1. **Scope:** only the task's affected areas changed; non-goals were not
   implemented.
2. **Correctness:** the expected behavior or documentation outcome exists.
3. **Compatibility:** existing links, interfaces, contracts, and conventions
   still hold unless the task explicitly changes them.
4. **Evidence:** the task's stated checks were run or a justified exception
   was recorded.

For Markdown tasks, inspect headings, links, frontmatter, reserved filenames,
and generated-file ownership as applicable. For code tasks, inspect the diff
and run focused tests before broader checks. Use repository tools and nearby
documentation rather than inventing a new validation system.

Do not mark a task complete merely because a file exists, a command exits zero,
or the subagent says it is done.

## Human gates and safety

Pause before proceeding when the task requires an unrecorded product choice,
architecture choice, destructive action, external communication, or scope
expansion. State the task ID, what is known, the exact decision or permission
required, and which dependent tasks are paused.

Do not use destructive repository commands to recover from a failed task.
Preserve unrelated work. Do not create speculative files, schemas,
directories, automation, or dependencies unless the task explicitly requires
them.

## Progress reporting

At the start, report the task file, number of executable tasks found, and the
first eligible task. During execution, report only meaningful transitions:
delegated, subagent finished, validation passed, validation failed, or blocked.

At the end of an invocation, report completed task IDs and validation
evidence, the active or blocked task, remaining eligible and blocked tasks,
files changed, and the next safe action.

If execution is interrupted, leave statuses and evidence in a resumable state.
On resume, re-read the task file and verify the last task's diff before
delegating another task.

## Completion criteria

Declare the task list complete only when every required task is `complete`,
each task has validation evidence, and no dependency or human gate remains
unresolved. If the task list defines a separate final review or synchronization
task, execute and validate it; do not infer completion from implementation
tasks alone.

## Anti-patterns

- Do not launch multiple task subagents concurrently.
- Do not delegate a whole phase when the task list defines smaller tasks.
- Do not let a subagent validate its own work as the only evidence.
- Do not skip a task because it is documentation-only.
- Do not rewrite the task list into a different schema during execution.
- Do not silently reinterpret missing dependencies or human decisions.
