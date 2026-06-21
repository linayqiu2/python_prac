# ============================================================
# D5 PRODUCTION-ISH REDESIGN — QUESTIONS
# ============================================================

'''
Q1. Free-trial experiment assignment and billing activation

Context:
You are testing whether offering a 1-month free trial increases paid subscription.
Users should be assigned 50/50 to control or treatment.
Treatment users see a free-trial prompt.
If they accept, the billing system starts a free trial.

Buggy code:
'''

import random
import datetime
import requests

def maybe_start_trial(user_id):
    if random.random() < 0.5:
        variant = "trial"
    else:
        variant = "control"

    now = datetime.datetime.now()

    if variant == "trial":
        r = requests.post(
            "https://billing/start_trial",
            json={"user_id": user_id}
        )

        if r.status_code == 200:
            log_exposure(user_id, variant, now)
            log_trial_started(user_id, now)
            return True

    return False


'''
Your tasks:
1. Identify at least 10 correctness/reliability issues.
2. Explain how each issue can bias experiment metrics.
3. Redesign this flow to be production-safe and experiment-safe.
4. What events should be logged?
5. What idempotency keys would you use?
6. What monitoring/alerts would you add?
'''


'''
Q2. Model rollout router with fallback

Context:
You are rolling out a new ChatGPT model to 10% of users.
If the new model fails, the system falls back to the old model.
You want to measure whether the new model improves task success.

Buggy code:
'''

import random
import time

def answer_prompt(user_id, prompt):
    if random.random() < 0.1:
        model = "new_model"
        variant = "treatment"
    else:
        model = "old_model"
        variant = "control"

    start = time.time()

    try:
        response = call_model(model, prompt)
    except Exception:
        response = call_model("old_model", prompt)

    latency_ms = (time.time() - start) * 1000

    log_event({
        "user_id": user_id,
        "variant": variant,
        "model": model,
        "latency_ms": latency_ms,
        "success": response is not None,
    })

    return response


'''
Your tasks:
1. Identify at least 10 issues.
2. Explain how fallback can contaminate treatment measurement.
3. Distinguish assigned model, attempted model, served model, and fallback model.
4. Propose a hardened rollout design.
5. What should be logged for reliable online evaluation?
6. What guardrail metrics should be monitored?
'''


'''
Q3. Event ingestion pipeline for product metrics

Context:
Client apps send product events to an ingestion endpoint.
Events are later used for DAU, retention, funnel, and experiment analysis.

Buggy code:
'''

event_store = []

def ingest_event(event):
    event_store.append(event)

    if event["event"] == "purchase":
        update_revenue_dashboard(event["user_id"], event["amount"])

    return {"status": "ok"}


'''
Your tasks:
1. Identify at least 10 production/data-quality issues.
2. Explain how these issues affect metrics like DAU, retention, and conversion.
3. Redesign ingestion for reliability and deduplication.
4. What validation should happen at ingestion time?
5. What should be done synchronously vs asynchronously?
6. What monitoring should exist?
'''


'''
Q4. Agent task execution with tool calls

Context:
An AI agent can complete tasks by calling tools.
Tools may fail, timeout, or return partial results.
You want to measure task success and tool reliability.

Buggy code:
'''

def run_agent_task(user_id, task):
    result = {}

    for tool in task.tools:
        output = call_tool(tool, task.input)
        result[tool.name] = output

    final_answer = generate_answer(task.input, result)

    if final_answer:
        log_event({
            "user_id": user_id,
            "task_id": task.id,
            "event": "task_success",
        })
    else:
        log_event({
            "user_id": user_id,
            "task_id": task.id,
            "event": "task_failure",
        })

    return final_answer


'''
Your tasks:
1. Identify at least 10 reliability/instrumentation issues.
2. Explain why task_started and tool_attempt events are necessary.
3. Explain how missing timeout/failure logs bias task success rate.
4. Redesign the agent execution flow.
5. What should be logged per task and per tool call?
6. What monitoring/alerts would you add?
'''


'''
Q5. User feedback collection for model quality

Context:
Users can rate assistant responses with thumbs up/down and optional reason.
You want to measure hallucination reports and satisfaction by model version.

Buggy code:
'''

def submit_feedback(user_id, response_id, rating, reason=None):
    response = get_response(response_id)

    feedback = {
        "user_id": user_id,
        "response_id": response_id,
        "model": response["model"],
        "rating": rating,
        "reason": reason,
        "created_at": datetime.datetime.now(),
    }

    save_feedback(feedback)

    if rating == "down":
        send_to_eval_queue(response)

    return True


'''
Your tasks:
1. Identify at least 10 correctness/reliability issues.
2. Explain how these issues affect hallucination-rate and satisfaction metrics.
3. Propose a robust feedback logging design.
4. How would you prevent duplicate or spam feedback?
5. How would you link feedback to model/version/prompt safely?
6. What monitoring should be added?
'''


'''
Q6. Subscription webhook processing

Context:
A billing provider sends webhook events:
- trial_started
- subscription_started
- subscription_canceled
- invoice_paid

You use these events for revenue and conversion metrics.

Buggy code:
'''

subscriptions = {}

def handle_webhook(payload):
    user_id = payload["user_id"]
    event_type = payload["type"]

    if event_type == "subscription_started":
        subscriptions[user_id] = "paid"
        log_conversion(user_id)

    elif event_type == "subscription_canceled":
        subscriptions[user_id] = "canceled"

    elif event_type == "trial_started":
        subscriptions[user_id] = "trial"

    return "ok"


'''
Your tasks:
1. Identify at least 10 issues.
2. Explain why webhook idempotency matters.
3. Explain how out-of-order events can corrupt subscription state.
4. Propose a production-safe webhook handler.
5. What keys/timestamps should be stored?
6. What reconciliation job would you run?
'''


'''
Q7. Daily metric backfill job

Context:
You run a daily backfill job that computes active users and writes results to a metrics table.

Buggy code:
'''

checkpoint = None

def run_daily_backfill(dates):
    global checkpoint

    for ds in dates:
        events = read_events(ds)
        dau = len([e["user_id"] for e in events])

        write_metric("dau", ds, dau)
        checkpoint = ds

    return checkpoint


'''
Your tasks:
1. Identify at least 10 correctness/reliability issues.
2. Explain how this can corrupt historical dashboards.
3. Redesign the job to be idempotent and restartable.
4. How should checkpoints be updated?
5. How should duplicate writes be handled?
6. What data-quality checks would you add?
'''


'''
Q8. ChatGPT Search retrieval logging

Context:
ChatGPT Search retrieves web sources, shows an answer, and users may click sources.
You want to measure answer usefulness and source-click rate.

Buggy code:
'''

def answer_with_search(user_id, query):
    sources = search_web(query)
    answer = generate_answer(query, sources)

    log_event({
        "user_id": user_id,
        "event": "answer_shown",
        "query": query,
        "num_sources": len(sources),
    })

    return answer


def log_source_click(user_id, query, url):
    log_event({
        "user_id": user_id,
        "event": "source_clicked",
        "query": query,
        "url": url,
    })


'''
Your tasks:
1. Identify at least 10 instrumentation issues.
2. Explain why query text is a bad join key.
3. Explain how source-click metrics can be biased.
4. Redesign logging for answer, sources, and clicks.
5. What IDs should connect retrieval, answer, and click events?
6. What privacy considerations matter?
'''


'''
Q9. Enterprise workspace provisioning and activation

Context:
A company signs up for ChatGPT Business.
The system creates a workspace, invites members, and tracks activation.

Buggy code:
'''

def create_workspace(admin_user_id, company_domain, invited_emails):
    workspace_id = create_workspace_record(company_domain)

    for email in invited_emails:
        send_invite_email(workspace_id, email)

    log_event({
        "workspace_id": workspace_id,
        "admin_user_id": admin_user_id,
        "event": "workspace_created",
    })

    return workspace_id


'''
Your tasks:
1. Identify at least 10 production/instrumentation issues.
2. Explain how invite failures affect workspace activation metrics.
3. Propose a robust workspace creation flow.
4. What should happen if some invite emails fail?
5. What should be logged for B2B activation analysis?
6. What monitoring would you add?
'''


'''
Q10. Offline model evaluation job

Context:
You run an offline evaluation job comparing old_model and new_model on sampled prompts.
The results are used to decide whether to launch.

Buggy code:
'''

def run_offline_eval(prompts):
    wins = 0
    total = 0

    for p in prompts:
        old_answer = call_model("old_model", p["prompt"])
        new_answer = call_model("new_model", p["prompt"])

        score = judge(new_answer, old_answer)

        if score == "new_better":
            wins += 1

        total += 1

    return wins / total


'''
Your tasks:
1. Identify at least 10 evaluation/reliability issues.
2. Explain how sampling and judge bias can mislead launch decisions.
3. Explain how API failures/timeouts should be handled.
4. Propose a robust offline eval pipeline.
5. What metrics beyond win rate should be reported?
6. What online validation should follow?
'''


# ============================================================
# D5 PRODUCTION-ISH REDESIGN — ANSWER KEY
# ============================================================

'''
Q1 Answer Key — Free-trial experiment assignment and billing activation

Issues:
1. Uses random.random(), so assignment is not sticky.
2. Assignment is not persisted.
3. Control exposure is never logged.
4. Treatment exposure is logged only after billing success.
5. Exposure, prompt display, user acceptance, billing attempt, and conversion are conflated.
6. No eligibility check or eligibility snapshot.
7. Uses local datetime.now(), not UTC.
8. No timeout on billing request.
9. No retry logic for transient billing failures.
10. Retry would be unsafe without idempotency key.
11. No idempotency key for start_trial.
12. No handling of duplicate calls.
13. No logging of billing failure reasons.
14. No request_id/session_id/experiment_id/variant_version.
15. Function returns False for both control users and failed billing users.
16. No observability or alerting.

Metric impact:
- Treatment conversion is inflated because only successful billing users are logged as exposed.
- Control denominator is missing.
- Users can switch variants across calls.
- Billing failures disappear from the funnel.
- Analysis cannot distinguish prompt failure, user decline, or billing failure.

Hardened design:
1. Validate user eligibility using only pre-assignment state.
2. Deterministically assign user using stable hash(user_id, experiment_salt).
3. Persist assignment with experiment_id, variant, assigned_at_utc, eligibility snapshot.
4. When prompt is actually shown, log exposure for treatment; for control, log control exposure at comparable decision point.
5. Log prompt_shown, prompt_accepted, billing_attempted, billing_succeeded, billing_failed separately.
6. Call billing with idempotency key such as trial_start:{experiment_id}:{user_id}.
7. Use timeout + retry with exponential backoff only when idempotency is guaranteed.
8. Store outbox event transactionally before async billing if needed.
9. Use UTC timestamps.
10. Make logs idempotent by event_id.

Recommended events:
assignment_created, exposure_logged, prompt_shown, prompt_accepted, billing_attempted,
trial_started, billing_failed, prompt_dismissed.

Monitoring:
assignment ratio/SRM, exposure count by variant, billing success rate, billing latency,
duplicate idempotency keys, missing terminal events, trial_started without exposure,
exposure without assignment, API timeout/error rate.
'''


'''
Q2 Answer Key — Model rollout router with fallback

Issues:
1. Uses random.random(), so assignment is not sticky.
2. Assignment is per request, not necessarily per user.
3. Assignment is not persisted.
4. Fallback to old_model is not logged distinctly.
5. Logged model is assigned model, not necessarily served model.
6. success = response is not None is too weak.
7. If fallback succeeds, treatment may look successful even though new model failed.
8. Latency includes fallback latency but not broken down by attempt.
9. No model version/config version.
10. No timeout handling.
11. No error reason logging.
12. No prompt/request ID.
13. No guardrail logging: cost, tokens, safety, hallucination, user feedback.
14. No separation of assignment, attempt, response, fallback.

Metric impact:
- Treatment quality can be overstated if old model fallback served the answer.
- New model failure rate is hidden.
- Latency attribution is ambiguous.
- User-level outcomes may be contaminated by request-level assignment.

Hardened design:
1. Assign at correct unit: user-level for user outcomes, request-level only for request outcomes.
2. Persist assignment.
3. Log assignment_model, attempted_model, served_model, fallback_used.
4. Log each model_attempt with model_version, start/end time, status, error reason.
5. Log final response event with served_model and user-visible outcome.
6. Analyze intent-to-treat and served-treatment separately.
7. Add timeout and controlled fallback policy.
8. Use deterministic rollout bucketing with salt/version.

Guardrails:
latency p50/p95/p99, error rate, fallback rate, cost/tokens, safety flags,
hallucination reports, user satisfaction, task success, retry rate.
'''


'''
Q3 Answer Key — Event ingestion pipeline

Issues:
1. Uses in-memory event_store; data lost on process restart.
2. No event_id/idempotency key.
3. Duplicate events are not deduped.
4. No schema validation.
5. Missing user_id/event/timestamp not handled.
6. No server receive timestamp.
7. Client timestamps may be missing or untrusted.
8. Synchronous dashboard update inside ingestion path.
9. A bad purchase event can crash dashboard update.
10. No authentication or source validation.
11. No privacy/PII handling.
12. No partitioning or durable storage.
13. No dead-letter queue.
14. No monitoring for malformed/late/duplicate events.

Metric impact:
- DAU and conversion can be inflated by duplicates.
- Retention can be wrong due to bad timestamps.
- Dashboard can diverge from raw events.
- Missing events cause undercount.
- Inline side effects cause partial failure.

Hardened design:
1. Require event_id, event_name, user/account ID, client_ts, server_received_ts, source, schema_version.
2. Validate schema at ingestion.
3. Write raw event durably first.
4. Deduplicate by event_id.
5. Send valid events to queue/stream for async processing.
6. Send invalid events to dead-letter table with reason.
7. Compute dashboards asynchronously from canonical event table.
8. Make derived writes idempotent.
9. Partition events by date/server time.
10. Add backfill/replay capability.

Sync vs async:
Synchronously validate, authenticate, durably write/ack.
Asynchronously update dashboards, revenue summaries, alerts.

Monitoring:
event volume by type/source, malformed rate, duplicate rate, ingestion latency,
queue lag, late events, schema-version drift, dashboard reconciliation.
'''


'''
Q4 Answer Key — Agent task execution with tool calls

Issues:
1. No task_started event.
2. No per-tool attempt logging.
3. No timeout on tool calls.
4. One tool failure can crash entire task without logging.
5. No retry policy.
6. No idempotency for task_id/attempt_id.
7. No partial-failure representation.
8. No latency/cost logging per tool.
9. No failure reason/status code logging.
10. No model/version/config logging.
11. final_answer truthiness is not a robust success definition.
12. No user-visible completion vs internal completion distinction.
13. No terminal event guarantee.
14. No handling of duplicate task execution.

Metric impact:
- Task success rate is biased because failed/timeout starts may disappear.
- Tool reliability cannot be measured.
- Long-running tasks without terminal events vanish from denominator.
- Failures cannot be debugged by tool/model/version.

Hardened design:
1. Generate task_attempt_id.
2. Log task_started before any tool call.
3. For each tool: log tool_attempt_started.
4. Call tool with timeout.
5. Retry only safe/idempotent tools.
6. Log tool_attempt_succeeded/failed/timeout with latency, error, cost.
7. Continue or abort based on tool criticality.
8. Generate final answer.
9. Log task_completed/task_failed/task_timeout with reason.
10. Ensure every started task has terminal status via watchdog.

Logs:
task_id, task_attempt_id, user_id, experiment_id, variant, model_version,
tool_name, tool_call_id, attempt_number, status, latency_ms, error_code,
input/output size, cost, started_at_utc, ended_at_utc.

Monitoring:
terminal event coverage, tool failure rate, timeout rate, retry rate, task success,
task latency, cost per successful task, failure reason distribution.
'''


'''
Q5 Answer Key — Feedback collection

Issues:
1. Does not validate rating values.
2. Allows duplicate feedback spam.
3. Does not verify user is allowed to rate response_id.
4. Fetches response at feedback time; response metadata may have changed.
5. Does not snapshot prompt/model/version at response time.
6. Uses local datetime.now().
7. No feedback_id/idempotency key.
8. No handling when get_response fails.
9. Queueing only downvotes biases eval set.
10. reason is unvalidated/unstructured.
11. No abuse/spam/rate limiting.
12. No privacy controls for prompt/response content.
13. No schema version.
14. send_to_eval_queue may fail after save_feedback, causing inconsistent eval pipeline.

Metric impact:
- Hallucination rate can be inflated by spam/duplicates.
- Satisfaction by model may be wrong if model metadata changes.
- Eval queue biased toward negative feedback only.
- Missing failed queue sends cause incomplete eval data.

Hardened design:
1. At response generation time, store immutable response metadata: response_id, model_version, prompt_id, conversation_id, created_at.
2. On feedback, validate user-response relationship.
3. Use feedback_id or idempotency key: user_id + response_id + feedback_type.
4. Deduplicate or allow only latest feedback depending product rule.
5. Validate rating/reason taxonomy.
6. Save feedback durably with UTC timestamp.
7. Use outbox pattern for eval queue.
8. Rate-limit feedback submission.
9. Track feedback source/surface.
10. Sample both positive and negative feedback for eval.

Monitoring:
feedback volume by model/surface, duplicate rate, invalid feedback rate,
eval queue failure/lag, hallucination report rate, downvote rate, spam signals.
'''


'''
Q6 Answer Key — Subscription webhook processing

Issues:
1. No webhook signature verification.
2. No event_id idempotency.
3. Duplicate webhooks can double-log conversions.
4. Out-of-order events can corrupt state.
5. No provider timestamp/event timestamp.
6. State keyed only by user_id, not subscription_id/account_id.
7. subscription_started always logs conversion even if already paid.
8. No handling of invoice_paid.
9. No transaction around state update and log_conversion.
10. No retry/dead-letter handling.
11. No raw payload storage.
12. No reconciliation with provider.
13. Missing event types silently ignored.
14. Does not distinguish trial conversion from paid subscription.

Metric impact:
- Paid conversion can be double-counted.
- Cancellations can overwrite newer paid state if events arrive late.
- Revenue metrics can diverge from billing provider.
- Experiment conversion attribution can be wrong.

Hardened design:
1. Verify webhook signature.
2. Store raw webhook event with provider_event_id.
3. Deduplicate by provider_event_id.
4. Use subscription_id/account_id as core entity.
5. Apply state transition only if event timestamp is newer or valid transition.
6. Process in transaction: raw event, state update, derived conversion event/outbox.
7. Make conversion logging idempotent.
8. Support replay/reprocessing.
9. Send bad events to DLQ.

Stored fields:
provider_event_id, subscription_id, user_id/account_id, event_type,
provider_created_at, received_at_utc, processed_at_utc, previous_state,
new_state, invoice_id, amount, currency.

Reconciliation:
Daily compare internal subscription/revenue state against billing provider export.
Alert on missing events, duplicate events, state mismatches, revenue mismatches.
'''


'''
Q7 Answer Key — Daily metric backfill

Issues:
1. Global checkpoint is unsafe and non-durable.
2. dates may be unsorted.
3. Counts events, not distinct users.
4. Direct e["user_id"] can crash.
5. Does not skip None/missing user_id.
6. write_metric may duplicate rows on rerun.
7. checkpoint updated after write, but no transaction.
8. If write_metric partially succeeds then crash, checkpoint may be inconsistent.
9. No data-quality checks.
10. No validation of input completeness.
11. No handling of late-arriving events.
12. No partition status table.
13. No retries.
14. No logging or audit trail.

Metric impact:
- DAU inflated by multiple events per user.
- Historical metrics can be overwritten inconsistently.
- Failed jobs may skip or duplicate partitions.
- Backfills are not reproducible.

Hardened design:
1. Sort partitions.
2. Use durable job_run_id and partition status table.
3. For each ds, mark status=processing.
4. Read canonical events.
5. Compute DAU as count distinct non-null user_id.
6. Run data-quality checks.
7. Write metric with idempotent upsert keyed by metric_name + ds + version.
8. Only mark partition success after metric write succeeds.
9. On failure, mark failed and stop or continue based on policy.
10. Support rerun by overwriting same metric version or writing new version.

Checks:
event volume vs expected, null user rate, duplicate event rate,
day-over-day anomaly, input partition completeness, distinct user sanity.

Monitoring:
job success/failure, partition lag, metric anomalies, rerun counts,
write conflicts, checkpoint advancement.
'''


'''
Q8 Answer Key — Search retrieval logging

Issues:
1. No search_id/request_id to join answer_shown and source_clicked.
2. Query text is used as implicit join key and can repeat.
3. Query text may contain sensitive information.
4. Click logging lacks answer_id/source_id/rank.
5. Does not log which sources were shown.
6. Does not log retrieval latency or answer latency.
7. Does not log model/version/retrieval version.
8. Does not log whether answer generation failed.
9. No dedupe/idempotency for click events.
10. No session/conversation context.
11. No timestamp fields.
12. No privacy minimization.
13. Source-click rate can be inflated by multiple clicks.
14. Cannot distinguish clicked shown source vs arbitrary URL.

Metric impact:
- Source clicks can be attributed to the wrong answer.
- Repeat queries cause cross-contamination.
- Click rate can be overcounted.
- Cannot analyze source rank quality or retrieval failures.

Hardened design:
1. Generate search_id for each search request.
2. Generate answer_id for shown answer.
3. Log retrieval event with search_id, source_ids, source ranks, retrieval latency.
4. Log answer_shown with search_id, answer_id, model_version, source_ids shown.
5. Log source_clicked with search_id, answer_id, source_id, rank, click_ts.
6. Use URL hashes/source IDs instead of raw query/URL where possible.
7. Store raw sensitive text only with appropriate privacy controls.

IDs:
search_id, answer_id, source_id, conversation_id, request_id, user_id/session_id.

Monitoring:
retrieval failure rate, no-source rate, answer generation failure rate,
source-click rate by rank, duplicate click rate, latency, privacy redaction failures.
'''


'''
Q9 Answer Key — Enterprise workspace provisioning

Issues:
1. Workspace record created before ensuring invites are processed correctly.
2. Invite email failures are not handled.
3. No invite_id/idempotency per email.
4. Duplicate invited_emails can send duplicates.
5. No validation of email/domain.
6. No transaction/outbox around workspace creation and invite sending.
7. Logs workspace_created after invites, so failure before log loses creation event.
8. Does not log invite_sent/invite_failed/member_joined.
9. No admin authorization checks.
10. No created_at timestamp.
11. No plan/customer/account ID.
12. No partial success reporting.
13. No retry policy for email service.
14. No monitoring of invite funnel.

Metric impact:
- Workspace activation can look low because invites failed silently.
- Created workspaces may be missing from denominator.
- Duplicate invites distort invitation and join metrics.
- Cannot distinguish product onboarding failure from email delivery failure.

Hardened design:
1. Validate admin and company/domain.
2. Create workspace in transaction with workspace_created event/outbox.
3. Deduplicate invite emails.
4. Create invite records with invite_id and status=pending.
5. Send invites asynchronously via outbox/queue.
6. Update invite status: sent, failed, bounced, accepted.
7. Retry transient email failures.
8. Return workspace_id and invite status summary.
9. Log member_joined separately when invite accepted.

Logs:
workspace_created, invite_created, invite_send_attempted, invite_sent,
invite_failed, invite_accepted, member_joined, first_message_sent.

Monitoring:
workspace creation errors, invite send failure rate, invite acceptance rate,
time to first member, time to first message, activation rate, queue lag.
'''


'''
Q10 Answer Key — Offline model evaluation

Issues:
1. prompts sample may be biased/not representative.
2. No random seed or reproducible sample.
3. No prompt stratification by category/language/difficulty.
4. No handling of model API failures/timeouts.
5. If old_model fails and new_model succeeds, judge result may be misleading unless logged.
6. Judge may be biased by answer order.
7. judge(new_answer, old_answer) is not blinded/randomized.
8. No tie handling.
9. Only reports win rate, no confidence interval.
10. No latency/cost/safety metrics.
11. No repeated judging or inter-rater reliability.
12. No prompt leakage from training/eval overlap.
13. No versioning of models, prompts, judge, rubric.
14. No raw output storage/audit.
15. Division by zero if prompts empty.
16. No retry/idempotency for model calls.

Metric impact:
- Launch decision can be driven by biased sample or biased judge.
- New model can look better offline but fail online.
- Failure cases can be silently dropped or miscounted.
- No uncertainty estimate.

Hardened design:
1. Build versioned eval dataset with prompt_id, category, language, difficulty, source, holdout status.
2. Use deterministic sampling with seed and stratification.
3. Call both models with timeouts and retry policy.
4. Log model_call_attempts with status, latency, tokens, cost, error.
5. Randomize/blind answer order before judging.
6. Use versioned judge model and rubric.
7. Capture win/loss/tie/invalid.
8. Report confidence intervals and segment metrics.
9. Include guardrails: latency, cost, refusal rate, safety issues, hallucination labels.
10. Store outputs and judge rationales for audit.
11. Follow offline eval with online A/B or staged rollout.

Metrics:
win rate, tie rate, invalid rate, segment win rates, latency p95, cost per answer,
safety violation rate, factuality/hallucination rate, refusal/helpfulness rate,
API failure rate, confidence intervals.
'''