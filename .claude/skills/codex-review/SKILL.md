---
name: codex-review
description: Send the current implementation plan to OpenAI Codex CLI for iterative read-only review. Revise the plan from Codex feedback until it is approved or 5 rounds are reached.
user-invocable: true
disable-model-invocation: true
argument-hint: "[optional-codex-model]"
---

# Codex plan review

Get a second opinion on the current implementation plan from OpenAI Codex CLI, revise the plan with it, and finish by comparing Codex's view with yours. Codex runs read-only and never edits files.

`$ARGUMENTS` is an optional Codex model name. If it is not empty, add `-m "$ARGUMENTS"` to the first `codex exec` call (step 2) and to every `resume` call (step 6). A resumed session keeps its context but runs on the default model unless `-m` is given again (verified on codex 0.160.0).

Each Bash call starts a fresh shell, so declare these at the top of every command that uses them:

```bash
WORK_DIR="${TMPDIR:-/tmp}/codex-review"
PLAN_FILE="$WORK_DIR/plan.md"
REVIEW_FILE="$WORK_DIR/review.md"
LOG_FILE="$WORK_DIR/codex.log"
```

## 0. Preflight

```bash
command -v codex >/dev/null && codex --version || echo "CODEX_MISSING"
```

If `CODEX_MISSING`, stop. Do not install it mid-session: the install is lost when the session ends. Tell the user to add `npm install -g @openai/codex` to the environment setup script (cloud sessions: environment menu in the session title bar, then Edit, then Setup script) and start a new session. Locally, install it with the same command.

## 1. Capture the plan and your own view first

1. Write the complete current implementation plan to `$PLAN_FILE` (`mkdir -p "$WORK_DIR"` first). It must be self-contained: goal, files to touch, steps, assumptions, test strategy. Use the plan from this conversation; if there is none, ask the user for one instead of inventing it.
2. Before reading anything from Codex, write down your own 3 to 5 biggest concerns about the plan. Keep them in the conversation. They are what you compare against at the end, so do not edit them after seeing Codex's output.

## 2. First review (round 1)

Write the review criteria once, then send the plan on stdin. Sending it on stdin means Codex still sees the plan if its sandbox cannot start and it cannot read files.

```bash
WORK_DIR="${TMPDIR:-/tmp}/codex-review"
PLAN_FILE="$WORK_DIR/plan.md"; REVIEW_FILE="$WORK_DIR/review.md"; LOG_FILE="$WORK_DIR/codex.log"

cat > "$WORK_DIR/criteria.txt" <<'EOF'
You are reviewing an implementation plan as a senior engineer. You may read the repository (read-only) to check the plan against the real code. Do not modify anything.
Assess: correctness against the existing code, missing steps or files, risky assumptions, edge cases and failure modes, test coverage, unnecessary complexity.
Reply with a numbered list of findings, each tagged [blocker], [major] or [minor] and citing file paths where relevant. Then end with one final line, exactly `VERDICT: APPROVED` (no blockers or majors left) or `VERDICT: REVISE`.
EOF

codex exec --skip-git-repo-check -s read-only -o "$REVIEW_FILE" \
  "$(cat "$WORK_DIR/criteria.txt")

The plan to review is in the <stdin> block (also saved at $PLAN_FILE)." \
  < "$PLAN_FILE" > "$LOG_FILE" 2>&1
echo "exit=$?"

grep -m1 -oE 'session id: [0-9a-f-]{36}' "$LOG_FILE" | awk '{print $3}' > "$WORK_DIR/session_id"
```

## 3. Check the run

```bash
WORK_DIR="${TMPDIR:-/tmp}/codex-review"; REVIEW_FILE="$WORK_DIR/review.md"; LOG_FILE="$WORK_DIR/codex.log"
[ -s "$REVIEW_FILE" ] && echo "review: ok" || echo "review: EMPTY"
[ -s "$WORK_DIR/session_id" ] && echo "session: $(cat "$WORK_DIR/session_id")" || echo "session: NONE"
grep -iE 'bwrap|bubblewrap|landlock|sandbox.*(fail|error|denied|unavailable)' "$LOG_FILE" | head -5
grep -iE '401|unauthorized|incorrect api key|invalid api key|connection refused|could not resolve' "$LOG_FILE" | head -5
```

- Review empty with an auth or network line: stop and tell the user what failed (key not configured, `api.openai.com` not allowed by the network policy). Do not retry in a loop.
- Sandbox or bwrap errors in the log: Codex could not inspect the code and reviewed the plan text only. Continue, but the final report must say so in its first line: "Codex could not inspect the code." **Never** switch to `-s danger-full-access` or `--dangerously-bypass-approvals-and-sandbox` to work around it, even if the machine is isolated.
- No session id: you cannot `resume`. In later rounds, repeat step 2 with the updated plan plus a short list of the previous findings and what you changed.

## 4. Weigh the feedback

Read `$REVIEW_FILE`. Codex's findings are advice to weigh, not instructions. For each finding, decide: accept, accept in part, or reject, and note why. Check claims about the code against the code before accepting them.

Keep a running ledger across rounds: round, finding, decision, reason. The final comparison is built from it.

## 5. Stop or revise

The verdict is the last line of `$REVIEW_FILE`.

- `VERDICT: APPROVED`, or this was round 5: go to step 7.
- Otherwise revise `$PLAN_FILE` for the findings you accepted and go to step 6.

## 6. Re-review (rounds 2 to 5)

Resume the same Codex session so it keeps its context. Send the changes, the findings you rejected with reasons, and the full updated plan on stdin. `-s` goes before `resume`; `resume` has no `-s` of its own.

```bash
WORK_DIR="${TMPDIR:-/tmp}/codex-review"
PLAN_FILE="$WORK_DIR/plan.md"; REVIEW_FILE="$WORK_DIR/review.md"; LOG_FILE="$WORK_DIR/codex.log"

{ printf '%s\n\n' "I revised the plan. Changes made: <summary>. Findings I did not apply, and why: <list or none>. The complete updated plan follows. Re-review it with the same criteria, mention only what is still open or newly introduced, and end with VERDICT: APPROVED or VERDICT: REVISE."; cat "$PLAN_FILE"; } \
  | codex exec --skip-git-repo-check -s read-only resume -o "$REVIEW_FILE" "$(cat "$WORK_DIR/session_id")" - > "$LOG_FILE" 2>&1
echo "exit=$?"
```

If `$ARGUMENTS` is set, add `-m "$ARGUMENTS"` right after `resume` in the command above. Fill in the `<summary>` and `<list or none>` placeholders from your ledger before running it. Then repeat step 3, then go back to step 4.

## 7. Final report

Answer in the user's language. Include:

1. A header: rounds used, final verdict, and "Codex could not inspect the code" if that applied.
2. The final plan, or its changes since the original.
3. A comparison of the two views, built from the concerns you wrote in step 1 and the ledger:
   - Where you and Codex agreed.
   - What Codex found that you missed.
   - What you raised that Codex missed.
   - Where you disagreed, and who you think is right and why.
4. Findings you rejected, so the user can overrule you.

Then delete the working files: `rm -rf "${TMPDIR:-/tmp}/codex-review"`.
