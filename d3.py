# ============================================================
# D3 EXPERIMENT CORRECTNESS — QUESTIONS
# ============================================================

'''
Q1. Non-sticky random assignment

Context:
You are launching an experiment for a new ChatGPT onboarding flow.
Users should be assigned 50/50 to control or treatment.
Assignment should be sticky at the user level.

Buggy code:
'''

import random
from datetime import datetime

def maybe_show_new_onboarding(user_id):
    if random.random() < 0.5:
        variant = "treatment"
        show_new_onboarding(user_id)
        log_event({
            "user_id": user_id,
            "event": "exposure",
            "variant": variant,
            "ts": datetime.now(),
        })
    else:
        variant = "control"

    return variant


'''
Your tasks:
1. Identify at least 6 experiment correctness issues.
2. Explain how each issue can bias experiment metrics.
3. Propose fixes.
4. What fields should be logged for reliable analysis?
'''


'''
Q2. Exposure logged only after successful treatment action

Context:
You are testing a 1-month free-trial prompt.
Treatment users should see a trial prompt.
If they accept, the billing system starts a free trial.

Buggy code:
'''

def maybe_start_trial(user_id, variant):
    if variant == "treatment":
        response = billing_api.start_trial(user_id)

        if response.status_code == 200:
            log_exposure(user_id=user_id, variant=variant)
            log_trial_started(user_id=user_id)

        return response.status_code == 200

    return False


'''
Your tasks:
1. Identify at least 6 experiment correctness issues.
2. Distinguish exposure, treatment delivery, and conversion.
3. Explain how this code biases conversion rate.
4. Propose an experiment-safe flow.
'''


'''
Q3. Eligibility check uses post-treatment behavior

Context:
You are testing whether a new assistant memory feature improves retention.
The experiment should include users eligible at the time of assignment.

Buggy code:
'''

def assign_memory_experiment(user_id):
    recent_messages = count_messages(user_id, days=7)

    if recent_messages >= 5:
        variant = deterministic_assign(user_id, "memory_exp_v1")
        save_assignment(user_id, variant)
        return variant

    return "not_eligible"


'''
Later, the analysis code does this:
'''

def analyze_memory_experiment(users):
    eligible_users = []

    for user_id in users:
        if count_messages(user_id, days=7) >= 5:
            eligible_users.append(user_id)

    return compare_retention(eligible_users)


'''
Your tasks:
1. Identify at least 5 experiment correctness issues.
2. Explain why eligibility must be snapshotted.
3. Explain how post-treatment filtering creates bias.
4. Propose a corrected assignment + analysis design.
'''


'''
Q4. Assignment unit mismatch

Context:
You are testing a new model-routing policy.
The assignment should be at user level so that each user has a consistent experience.

Buggy code:
'''

def route_request(user_id, request_id, prompt):
    bucket = stable_hash(request_id) % 100

    if bucket < 50:
        model = "old_model"
        variant = "control"
    else:
        model = "new_model"
        variant = "treatment"

    log_request({
        "user_id": user_id,
        "request_id": request_id,
        "variant": variant,
        "model": model,
    })

    return call_model(model, prompt)


'''
Analysis code:
'''

def compute_user_satisfaction(request_logs):
    scores = {}

    for row in request_logs:
        scores.setdefault(row["user_id"], []).append(row["satisfaction_score"])

    return {
        user_id: sum(vals) / len(vals)
        for user_id, vals in scores.items()
    }


'''
Your tasks:
1. Identify at least 5 experiment correctness issues.
2. Explain why request-level assignment may be wrong here.
3. Explain how mixed user exposure affects user-level outcomes.
4. Propose a corrected assignment unit and analysis grain.
'''


'''
Q5. Variant definition changes mid-experiment

Context:
You are running an experiment on an API feature.
During the experiment, the treatment changes from model A to model B, but the variant name remains "treatment".

Buggy code:
'''

def assign_api_experiment(user_id, current_date):
    variant = deterministic_assign(user_id, "api_exp")

    if variant == "treatment":
        if current_date < "2026-07-01":
            model = "model_A"
        else:
            model = "model_B"
    else:
        model = "baseline_model"

    log_assignment({
        "user_id": user_id,
        "experiment_id": "api_exp",
        "variant": variant,
        "model": model,
        "date": current_date,
    })

    return model


'''
Analysis code:
'''

def analyze_api_experiment(assignments, outcomes):
    return compare_metric(
        treatment_users=[a["user_id"] for a in assignments if a["variant"] == "treatment"],
        control_users=[a["user_id"] for a in assignments if a["variant"] == "control"],
        outcomes=outcomes,
    )


'''
Your tasks:
1. Identify at least 5 experiment correctness issues.
2. Explain why changing treatment semantics mid-experiment is dangerous.
3. Explain how to version variants properly.
4. Propose analysis options after such a change.
'''


'''
Q6. Sample ratio mismatch check

Context:
You expect a 50/50 assignment between control and treatment.
You write a quick SRM check.

Buggy code:
'''

def check_srm(assignments):
    control = 0
    treatment = 0

    for row in assignments:
        if row["variant"] == "control":
            control += 1
        else:
            treatment += 1

    ratio = control / treatment

    if ratio < 0.45 or ratio > 0.55:
        return True

    return False


'''
Your tasks:
1. Identify at least 6 issues in the SRM check.
2. Explain what SRM means and why it matters.
3. Explain what unit should be counted.
4. Propose a better SRM check.
'''


'''
Q7. Event-level analysis instead of user-level analysis

Context:
You are testing whether a new ChatGPT answer-ranking feature improves user satisfaction.
Each user can submit many feedback events.

Buggy code:
'''

def satisfaction_by_variant(assignments, feedback_events):
    user_variant = {
        a["user_id"]: a["variant"]
        for a in assignments
    }

    sums = {"control": 0, "treatment": 0}
    counts = {"control": 0, "treatment": 0}

    for e in feedback_events:
        variant = user_variant[e["user_id"]]
        sums[variant] += e["rating"]
        counts[variant] += 1

    return {
        v: sums[v] / counts[v]
        for v in sums
    }


'''
Your tasks:
1. Identify at least 5 experiment correctness issues.
2. Explain when event-level averaging is wrong.
3. Explain how power users can dominate results.
4. Propose a user-level analysis.
'''


'''
Q8. Conversion attribution window bug

Context:
You are testing whether an onboarding email increases paid subscription.
Users are exposed at exposed_at.
A conversion is a subscription within 7 days after exposure.

Buggy code:
'''

def conversion_rate(assignments, subscriptions):
    exposed_users = set()
    converted_users = set()

    for a in assignments:
        exposed_users.add(a["user_id"])

    for s in subscriptions:
        if s["user_id"] in exposed_users:
            converted_users.add(s["user_id"])

    return len(converted_users) / len(exposed_users)


'''
Your tasks:
1. Identify at least 6 experiment correctness issues.
2. Explain why time windows matter.
3. Explain why pre-exposure conversions must be excluded.
4. Propose corrected attribution logic.
'''


'''
Q9. Missing denominator logging

Context:
You are evaluating an agent feature.
The metric should be:
successful agent tasks / started agent tasks

Buggy code:
'''

def run_agent_task(user_id, task):
    try:
        result = agent.execute(task)

        if result.status == "success":
            log_event({
                "user_id": user_id,
                "event": "agent_success",
                "task_id": task.id,
            })

        return result

    except Exception:
        log_event({
            "user_id": user_id,
            "event": "agent_failure",
            "task_id": task.id,
        })
        return None


'''
Analysis code:
'''

def agent_success_rate(events):
    success = 0
    failure = 0

    for e in events:
        if e["event"] == "agent_success":
            success += 1
        elif e["event"] == "agent_failure":
            failure += 1

    return success / (success + failure)


'''
Your tasks:
1. Identify at least 6 instrumentation / experiment correctness issues.
2. Explain why started-task logging is necessary.
3. Explain how missing denominator events bias success rate.
4. Propose better logging.
'''


'''
Q10. Offline evaluation leakage

Context:
You are evaluating a new model ranking policy offline before launch.
The model was trained using historical user feedback.
You evaluate it on recent feedback logs.

Buggy code:
'''

def offline_eval(model, feedback_logs):
    correct = 0
    total = 0

    for row in feedback_logs:
        features = {
            "prompt": row["prompt"],
            "user_id": row["user_id"],
            "previous_feedback": row["feedback_score"],
        }

        prediction = model.predict(features)

        if prediction == row["feedback_score"]:
            correct += 1

        total += 1

    return correct / total


'''
Your tasks:
1. Identify at least 6 evaluation correctness issues.
2. Explain leakage risks.
3. Explain why offline evaluation may not match online impact.
4. Propose a safer offline + online evaluation plan.
'''


# ============================================================
# D3 EXPERIMENT CORRECTNESS — ANSWER KEY
# ============================================================

'''
Q1 Answer Key — Non-sticky random assignment

Issues:
1. Uses random.random(), so assignment is not sticky.
2. Same user can receive different variants across visits.
3. Assignment is not persisted.
4. Control exposure is not logged.
5. Treatment exposure is logged only after treatment display, not at assignment/exposure boundary.
6. Uses datetime.now(), likely local timezone and not UTC.
7. No experiment_id, assignment_id, salt, variant version, or eligibility snapshot.
8. No logging of failed treatment delivery.
9. No idempotency key for exposure logging.
10. No way to reproduce assignment later.

Metric impact:
- Treatment/control groups become contaminated.
- Control denominator may be missing.
- Exposure-based metrics overcount treatment and undercount control.
- Repeated users may appear in both groups.
- Analysis becomes non-reproducible.

Fixes:
- Use deterministic user-level bucketing with stable salt.
- Persist assignment once per user.
- Log exposure for both variants when user becomes exposed.
- Use UTC timestamps.
- Include experiment_id, variant, assignment unit, salt/version, eligibility state, request_id/session_id.
- Make exposure logging idempotent.

Good logging fields:
user_id, experiment_id, variant, assignment_unit, assignment_salt, assignment_version,
eligible_at_assignment, exposed_at_utc, request_id/session_id, exposure_event_id,
surface, country/device if relevant, logging_version.
'''


'''
Q2 Answer Key — Exposure logged only after successful treatment action

Issues:
1. Exposure is logged only after billing success.
2. Users who saw treatment but failed billing are missing from exposure denominator.
3. Control users have no exposure logs.
4. Treatment delivery, exposure, acceptance, and conversion are mixed together.
5. No idempotency key for billing API call.
6. No retry/timeout/error handling around billing.
7. No logging of prompt shown, prompt accepted, billing attempted, billing failed.
8. variant is passed in rather than validated from persisted assignment.
9. No timestamp fields.
10. Function returns False for control, which can be confused with failed treatment.

Metric impact:
- Conversion rate among exposed treatment users is inflated because only successful starts are logged.
- Billing failures disappear from denominator.
- Cannot distinguish poor product behavior from downstream billing failure.
- Cannot compare treatment/control properly.

Fixes:
- Persist assignment first.
- Log exposure when prompt is actually shown.
- Log user action separately: accepted/dismissed.
- Log billing attempt separately.
- Log billing success/failure separately.
- Use idempotency key for billing.
- Use retries only with idempotency.
- Include timestamps and request IDs.

Experiment-safe flow:
assignment -> eligibility check snapshot -> show prompt -> log exposure ->
if accepted: log_accept -> call billing with idempotency key -> log billing_result -> log conversion if success.
'''


'''
Q3 Answer Key — Eligibility check uses post-treatment behavior

Issues:
1. Analysis recomputes eligibility later using post-treatment data.
2. count_messages(days=7) can be affected by treatment itself.
3. Eligibility is not snapshotted at assignment time.
4. Assignment may be saved only for eligible users, making denominator unclear.
5. Users who become eligible after treatment effects can enter analysis incorrectly.
6. Users who were eligible at assignment but later inactive may be excluded.
7. No eligibility timestamp/version.
8. No clear analysis population: intent-to-treat vs exposed vs treated.

Metric impact:
- Post-treatment filtering creates selection bias.
- Treatment can increase messages, causing more treatment users to qualify.
- Estimated retention lift can be inflated or reversed.
- Analysis is not reproducible.

Fixes:
- Define eligibility based only on pre-assignment data.
- Snapshot eligibility features at assignment.
- Store assignment and eligibility timestamp.
- Analyze all assigned eligible users as primary intent-to-treat.
- Optionally do secondary exposed/treated analysis with clear caveats.

Correct design:
At assignment time, compute prior_7d_messages using data before assignment_at.
Store user_id, experiment_id, variant, assignment_at, eligibility_features.
Analysis uses stored assignment table, not recomputed eligibility.
'''


'''
Q4 Answer Key — Assignment unit mismatch

Issues:
1. Assignment uses request_id, not user_id.
2. Same user can receive both old and new model.
3. User-level satisfaction outcome is affected by mixed exposure.
4. Request-level randomization may be valid only for request-level outcomes, not user-level outcomes.
5. Analysis aggregates user satisfaction without knowing exposure share per user.
6. No persisted assignment.
7. No experiment_id or assignment unit logged.
8. Potential carryover effects: one response can influence future prompts/satisfaction.
9. Treatment/control interference within the same user journey.

Metric impact:
- User-level treatment effect is diluted.
- Users can be contaminated across variants.
- Satisfaction may reflect mixed experiences.
- Standard errors may be wrong if treating requests as independent.

Fixes:
- Randomize at user level if measuring user-level outcomes.
- Persist user assignment.
- Analyze at same grain as randomization.
- If request-level randomization is intentional, use request-level outcomes and account for clustered users.
- Log assignment_unit and exposure share.

Correct grain:
For retention/satisfaction over time: user-level assignment.
For latency or per-request success: request-level may be acceptable, but analysis should cluster by user if needed.
'''


'''
Q5 Answer Key — Variant definition changes mid-experiment

Issues:
1. Treatment meaning changes from model_A to model_B mid-experiment.
2. Same variant label hides two different treatments.
3. Analysis pools model_A and model_B together.
4. Calendar time is confounded with model version.
5. Users assigned before and after change may have different experiences.
6. No variant_version or treatment_version.
7. Deterministic assignment does not account for versioning.
8. Rollout change may coincide with seasonality or traffic mix changes.

Metric impact:
- Treatment effect estimate becomes uninterpretable.
- Bad model_A and good model_B can cancel out.
- Time trends can be mistaken for model effects.
- Users may get inconsistent treatment over time.

Fixes:
- Version treatment explicitly: treatment_model_A, treatment_model_B or treatment_v1/v2.
- Log model_version and config_version.
- Freeze treatment definition during experiment when possible.
- If change is necessary, start a new experiment or segment analysis by version/time.
- Consider excluding transition period.

Analysis options:
1. Analyze pre-change model_A vs control.
2. Analyze post-change model_B vs control.
3. Treat as two separate experiments.
4. If enough overlap, include date fixed effects, but still report version-specific effects.
'''


'''
Q6 Answer Key — Sample ratio mismatch check

Issues:
1. Counts rows, not unique assignment units.
2. Treats every non-control as treatment, hiding invalid variants.
3. ratio = control / treatment is not the right check for 50/50 threshold.
4. Threshold 0.45 to 0.55 on ratio is wrong because expected ratio control/treatment is 1.
5. Division by zero possible.
6. Does not compare observed counts to expected allocation.
7. Does not use statistical test or tolerance based on sample size.
8. Direct key access can crash.
9. Duplicate assignments can distort counts.
10. Does not check assignment before exposure separately.

What SRM means:
Sample ratio mismatch occurs when observed allocation proportions differ materially from expected assignment proportions. It suggests assignment, logging, eligibility, or data pipeline issues.

Correct unit:
Usually unique randomized unit: user_id/account_id/workspace_id/request_id depending on experiment design.

Better check:
- Deduplicate by assignment unit.
- Count valid variants.
- Compare observed counts to expected counts.
- Use chi-square goodness-of-fit or exact binomial for 2 variants.
- Alert when p-value is very small, e.g. p < 0.001.
- Also check invalid/missing variants and duplicate assignments.
'''


'''
Q7 Answer Key — Event-level analysis instead of user-level analysis

Issues:
1. Averages events, not users.
2. Power users with many feedback events dominate metric.
3. Duplicate feedback events can inflate influence.
4. Missing assignment for feedback user causes KeyError.
5. Duplicate/conflicting assignments not handled.
6. Does not handle missing rating.
7. Does not separate exposure from assignment.
8. Counts post-treatment feedback only if feedback exists, causing selection bias if treatment changes feedback likelihood.
9. No guardrail for different feedback propensity by variant.

Metric impact:
- Variant with more active users can dominate event-weighted metric.
- If treatment causes more feedback, event-level average may shift due to composition.
- User-level satisfaction effect may differ from event-level rating average.

Fixes:
- Primary analysis should aggregate per user first:
  user_avg_rating = average rating per assigned user.
- Then compare mean user_avg_rating by variant.
- Include users with no feedback depending on metric definition, or analyze feedback propensity separately.
- Deduplicate assignments.
- Handle missing ratings.
- Use intent-to-treat denominator where appropriate.
'''


'''
Q8 Answer Key — Conversion attribution window bug

Issues:
1. Counts any subscription ever, not within 7 days.
2. Does not require subscription after exposure.
3. Pre-exposure conversions are counted.
4. Does not use exposed_at.
5. Denominator is all assigned users, not necessarily exposed users depending on intended metric.
6. Does not dedupe exposures or use first exposure.
7. Does not handle missing timestamps.
8. Does not compute by variant.
9. Division by zero if no exposed users.
10. Does not handle users with multiple subscriptions.

Metric impact:
- Inflates conversion by counting old conversions.
- Can attribute conversions that happened before treatment.
- Bias differs if treatment/control have different pre-existing conversion rates.
- Cannot estimate causal effect by variant.

Fixes:
- Build first_exposure per user and variant.
- For each subscription, require:
  subscription_ts >= exposed_at
  subscription_ts < exposed_at + 7 days or <= depending definition.
- Deduplicate converted users.
- Compute conversion by variant.
- Decide whether primary denominator is assigned eligible users or exposed users.
'''


'''
Q9 Answer Key — Missing denominator logging

Issues:
1. Does not log agent_task_started.
2. Only logs success or exception failure.
3. Non-exception unsuccessful results may not be logged as failure.
4. If logging success/failure fails, task outcome disappears.
5. Does not log variant/model/version.
6. Does not log latency, cost, tool calls, failure reason, or status code.
7. No task attempt number.
8. No idempotent event_id.
9. Success/failure denominator only includes terminal logged outcomes, not started tasks.
10. If agent crashes before try block or task.id missing, denominator is lost.

Metric impact:
- Success rate is biased upward if failures are unlogged.
- Tasks that hang, timeout, or are abandoned disappear.
- Cannot distinguish no-start, start, success, failure, timeout.
- Cannot compute reliable funnel.

Fixes:
- Log task_started before execution.
- Log terminal status for every started task: success, failure, timeout, canceled.
- Use idempotent task_id + attempt_id.
- Include experiment_id, variant, model_version, user_id, timestamps, latency, cost, failure_reason.
- Monitor started vs terminal event mismatch.

Better metric:
successful tasks / started tasks, with started task event as denominator.
Also track terminal_event_coverage = terminal_events / started_events.
'''


'''
Q10 Answer Key — Offline evaluation leakage

Issues:
1. Uses feedback_score as an input feature and target, direct label leakage.
2. user_id may allow memorization of user-specific labels.
3. Evaluation logs may overlap with training data.
4. No train/test time split.
5. Exact equality prediction == feedback_score may be wrong for continuous/ordinal scores.
6. Feedback logs are selected only from users who gave feedback, causing selection bias.
7. Offline feedback may not reflect online task success.
8. Historical feedback was generated under old policy, so counterfactual evaluation is biased.
9. No handling of missing/malformed fields.
10. No segment analysis.
11. Does not evaluate guardrails: latency, safety, hallucination, cost.

Metric impact:
- Offline accuracy is inflated by leakage.
- Model may look good offline but fail online.
- Selection bias means feedback-giving users are not representative.
- Policy change may alter distribution of prompts and feedback.

Fixes:
- Remove post-outcome fields from features.
- Use time-based holdout after training window.
- Ensure no overlap between training and eval data.
- Use appropriate metrics: RMSE/correlation for scores, ranking metrics if ranking.
- Evaluate on human-labeled or adjudicated samples where possible.
- Segment by prompt type, user type, language, model version.
- Follow with online A/B test or staged rollout.
- Include guardrails: latency, cost, safety, factuality, user retention/task success.
'''