# ============================================================
# D4 PRODUCT-CONTEXT INTEGRATED DEBUGGING — QUESTIONS
# ============================================================

'''
Q1. ChatGPT daily active users

Context:
You are analyzing ChatGPT usage.
Each event may contain:
- user_id
- event
- date

Expected behavior:
Return date -> number of distinct active users on that date.
Ignore records missing user_id or date.
Do not count None user_id.
Do not mutate input.

Buggy code:
'''

def daily_active_users(events):
    result = {}

    for e in events:
        date = e["date"]
        user_id = e["user_id"]

        if date not in result:
            result[date] = 0

        result[date] += 1
        e["counted"] = True

    return result


'''
Q2. ChatGPT message-to-response success rate

Context:
Each conversation event has:
- conversation_id
- event
- ts

Events can include:
- "user_message"
- "assistant_response"
- "error"

Expected behavior:
Compute:
number of user_message events that receive assistant_response before the next user_message
/
number of user_message events

Events may be unsorted.
Analyze separately by conversation_id.

Buggy code:
'''

def message_response_success_rate(events):
    total_messages = 0
    successful_messages = 0
    waiting_for_response = False

    for e in events:
        if e["event"] == "user_message":
            total_messages += 1
            waiting_for_response = True

        if e["event"] == "assistant_response" and waiting_for_response:
            successful_messages += 1
            waiting_for_response = False

    return successful_messages / total_messages


'''
Q3. API developer activation

Context:
You are analyzing API developer onboarding.
A developer is activated if they have at least one successful API request.
Successful means 200 <= status_code < 300.

Expected behavior:
Return a set of developer_ids with at least one successful request.
status_code may be int or numeric string.
Ignore malformed records.

Buggy code:
'''

def activated_developers(requests):
    activated = []

    for r in requests:
        status = r["status_code"]

        if status >= 200 and status <= 300:
            activated.append(r["developer_id"])

    return activated


'''
Q4. Time to first successful API request

Context:
signups has:
- developer_id
- signup_ts

requests has:
- developer_id
- ts
- status_code

Expected behavior:
Return developer_id -> time from earliest signup to first successful request after signup.
Timestamps are integer hours.
Ignore requests before signup.

Buggy code:
'''

def time_to_first_success(signups, requests):
    signup_time = {}

    for s in signups:
        signup_time[s["developer_id"]] = s["signup_ts"]

    result = {}

    for r in requests:
        if r["status_code"] == 200:
            developer_id = r["developer_id"]
            result[developer_id] = r["ts"] - signup_time[developer_id]

    return result


'''
Q5. p95 latency by model version

Context:
Each request has:
- model_version
- latency_ms

Expected behavior:
Return model_version -> p95 latency using nearest-rank method:
rank = ceil(0.95 * n)
index = rank - 1

Ignore missing or None latency.
Include latency 0.
Do not mutate input.

Buggy code:
'''

import math

def p95_latency_by_model(requests):
    latencies = {}

    for r in requests:
        model = r["model_version"]
        latency = r.get("latency_ms")

        if latency:
            latencies.setdefault(model, []).append(latency)

    result = {}

    for model, values in latencies.items():
        values.sort()
        idx = math.ceil(0.95 * len(values))
        result[model] = values[idx]

    return result


'''
Q6. Cost per successful task

Context:
Each task attempt has:
- task_id
- cost
- status

status can be:
- "success"
- "failure"
- "timeout"

Expected behavior:
Return:
total cost across all valid attempts / number of distinct tasks that eventually succeeded

A task succeeds if it has at least one success event.
Cost includes failed attempts too.
Return None if no task succeeded.

Buggy code:
'''

def cost_per_successful_task(tasks):
    total_cost = 0
    successes = 0

    for t in tasks:
        if t["status"] == "success":
            successes += 1
            total_cost += t["cost"]

    return total_cost / successes


'''
Q7. Agent tool-call failure rate by tool

Context:
Each tool call has:
- task_id
- tool_name
- status

status can be "success" or "failure".

Expected behavior:
Return tool_name -> failure rate.
Denominator is all valid tool calls for that tool.
Ignore invalid statuses.

Buggy code:
'''

def tool_failure_rate_by_tool(tool_calls):
    failures = {}
    totals = {}

    for c in tool_calls:
        tool = c["tool_name"]

        if c["status"] == "failure":
            failures[tool] = failures.get(tool, 0) + 1
        else:
            totals[tool] = totals.get(tool, 0) + 1

    return {
        tool: failures.get(tool, 0) / totals[tool]
        for tool in totals
    }


'''
Q8. Agent task completion within time limit

Context:
Each event has:
- task_id
- event
- ts

Events:
- "started"
- "completed"
- "failed"

Expected behavior:
Return fraction of distinct started tasks that completed within max_minutes after first start.

Rules:
- Use first started timestamp per task.
- Completion must be after start and within max_minutes.
- Events may be unsorted.
- Return None if no tasks started.

Buggy code:
'''

def completion_rate_within_minutes(events, max_minutes):
    started = set()
    completed = set()

    for e in events:
        if e["event"] == "started":
            started.add(e["task_id"])

        if e["event"] == "completed":
            completed.add(e["task_id"])

    return len(started & completed) / len(started)


'''
Q9. ChatGPT regeneration rate

Context:
Each conversation event has:
- conversation_id
- event
- ts

Events:
- "assistant_response"
- "regenerate_clicked"

Expected behavior:
Return:
number of assistant responses followed by regenerate_clicked before next assistant_response
/
number of assistant responses

Multiple regenerate clicks after one response count once.
Analyze separately by conversation_id.

Buggy code:
'''

def regeneration_rate(events):
    responses = 0
    regenerates = 0
    last_response_seen = False

    for e in events:
        if e["event"] == "assistant_response":
            responses += 1
            last_response_seen = True

        if e["event"] == "regenerate_clicked" and last_response_seen:
            regenerates += 1

    return regenerates / responses


'''
Q10. ChatGPT Search source-click rate

Context:
Each search event has:
- search_id
- event
- ts

Events:
- "answer_shown"
- "source_clicked"

Expected behavior:
Return:
number of searches with at least one source_clicked after first answer_shown
/
number of searches with answer_shown

Events may be unsorted.
Deduplicate by search_id.

Buggy code:
'''

def source_click_rate(events):
    shown = 0
    clicked = 0

    for e in events:
        if e["event"] == "answer_shown":
            shown += 1

        if e["event"] == "source_clicked":
            clicked += 1

    return clicked / shown


'''
Q11. Enterprise workspace activation

Context:
Each workspace event has:
- workspace_id
- user_id
- event
- ts

Events:
- "workspace_created"
- "member_joined"
- "message_sent"

A workspace is activated if within 7 days after first workspace_created:
- at least 2 distinct users joined
- at least 1 message_sent occurred

Timestamps are integer days.

Buggy code:
'''

def activated_workspaces(events):
    created = {}
    joined_count = {}
    messaged = set()

    for e in events:
        workspace_id = e["workspace_id"]

        if e["event"] == "workspace_created":
            created[workspace_id] = e["ts"]

        if e["event"] == "member_joined":
            joined_count[workspace_id] = joined_count.get(workspace_id, 0) + 1

        if e["event"] == "message_sent":
            messaged.add(workspace_id)

    result = set()

    for workspace_id in created:
        if joined_count.get(workspace_id, 0) >= 2 and workspace_id in messaged:
            result.add(workspace_id)

    return result


'''
Q12. Enterprise seat utilization

Context:
seats:
- workspace_id
- user_id

events:
- workspace_id
- user_id
- event

A seat is utilized if that user sent at least one message in the workspace.

Expected behavior:
Return workspace_id -> utilized_seats / total_seats.

Buggy code:
'''

def seat_utilization_by_workspace(seats, events):
    total_seats = {}
    used = {}

    for s in seats:
        workspace_id = s["workspace_id"]
        total_seats[workspace_id] = total_seats.get(workspace_id, 0) + 1

    for e in events:
        if e["event"] == "message_sent":
            workspace_id = e["workspace_id"]
            used[workspace_id] = used.get(workspace_id, 0) + 1

    return {
        workspace_id: used.get(workspace_id, 0) / total_seats[workspace_id]
        for workspace_id in total_seats
    }


'''
Q13. Pairwise model win rates

Context:
Each human eval record has:
- prompt_id
- model_a
- model_b
- winner

winner is "a", "b", or "tie".

Expected behavior:
Return model_name -> win_rate.
win_rate = wins / non_tie_comparisons.
Ties do not count in numerator or denominator.
If a model only appears in ties, win_rate should be None.

Buggy code:
'''

def model_win_rates(eval_records):
    wins = {}
    totals = {}

    for r in eval_records:
        model_a = r["model_a"]
        model_b = r["model_b"]
        winner = r["winner"]

        totals[model_a] = totals.get(model_a, 0) + 1
        totals[model_b] = totals.get(model_b, 0) + 1

        if winner == "a":
            wins[model_a] = wins.get(model_a, 0) + 1
        elif winner == "b":
            wins[model_b] = wins.get(model_b, 0) + 1

    return {
        model: wins.get(model, 0) / totals[model]
        for model in totals
    }


'''
Q14. Hallucination report rate by model

Context:
Each assistant response log has:
- response_id
- model_version
- user_reported_issue

user_reported_issue can be:
- None
- "hallucination"
- "unsafe"
- "other"

Expected behavior:
Return model_version -> fraction of distinct responses reported as hallucination.

Rules:
- Denominator is distinct response_id per model.
- Numerator is distinct response_id per model where issue == "hallucination".
- If same response_id appears with conflicting model_version, use first valid model_version.

Buggy code:
'''

def hallucination_report_rate_by_model(responses):
    total = {}
    hallucinations = {}

    for r in responses:
        model = r["model_version"]

        total[model] = total.get(model, 0) + 1

        if r["user_reported_issue"] == "hallucination":
            hallucinations[model] = hallucinations.get(model, 0) + 1

    return {
        model: hallucinations.get(model, 0) / total[model]
        for model in total
    }


'''
Q15. Prompt category distribution

Context:
Each prompt has:
- prompt_id
- category

Expected behavior:
Return category -> fraction of distinct prompts in that category.

Rules:
- Deduplicate by prompt_id.
- Use first category seen for each prompt_id.
- Ignore missing prompt_id or category.

Buggy code:
'''

def category_distribution(prompts):
    counts = {}
    total = 0

    for p in prompts:
        category = p["category"]
        counts[category] = counts.get(category, 0) + 1
        total += 1

    return {
        category: counts[category] / total
        for category in counts
    }


'''
Q16. API developer day-N retention

Context:
A developer is active on a date if they made at least one successful API request that day.
Successful means 200 <= status_code < 300.

signups:
- developer_id
- signup_date

requests:
- developer_id
- date
- status_code

Expected behavior:
Return fraction of signup developers active exactly N days after earliest signup.

Buggy code:
'''

from datetime import datetime, timedelta

def developer_day_n_retention(signups, requests, n):
    signup_dates = {}

    for s in signups:
        signup_dates[s["developer_id"]] = datetime.strptime(s["signup_date"], "%Y-%m-%d").date()

    active = set()

    for r in requests:
        if r["status_code"] == 200:
            active.add(r["developer_id"])

    retained = 0

    for developer_id in signup_dates:
        if developer_id in active:
            retained += 1

    return retained / len(signup_dates)


'''
Q17. Model rollout guardrail summary

Context:
Each metric row has:
- variant
- latency_ms
- error
- cost

Expected behavior:
Return by variant:
{
    "control": {
        "avg_latency_ms": ...,
        "error_rate": ...,
        "avg_cost": ...
    },
    ...
}

Rules:
- latency, error, and cost can have separate valid denominators.
- error must be boolean.
- Return None for a metric if no valid denominator.

Buggy code:
'''

def rollout_guardrail_summary(rows):
    result = {}

    for r in rows:
        variant = r["variant"]

        if variant not in result:
            result[variant] = {
                "latency_sum": 0,
                "errors": 0,
                "cost_sum": 0,
                "count": 0,
            }

        result[variant]["latency_sum"] += r["latency_ms"]
        result[variant]["cost_sum"] += r["cost"]

        if r["error"]:
            result[variant]["errors"] += 1

        result[variant]["count"] += 1

    output = {}

    for variant, vals in result.items():
        output[variant] = {
            "avg_latency_ms": vals["latency_sum"] / vals["count"],
            "error_rate": vals["errors"] / vals["count"],
            "avg_cost": vals["cost_sum"] / vals["count"],
        }

    return output


'''
Q18. User-level feedback rating by variant

Context:
assignments:
- user_id
- variant

feedback:
- user_id
- rating

Expected behavior:
Compute average user-level rating by variant:
1. For each assigned user, average their ratings.
2. For each variant, average across users.

Do not average raw feedback events directly.

Buggy code:
'''

def user_level_rating_by_variant(assignments, feedback):
    user_variant = {
        a["user_id"]: a["variant"]
        for a in assignments
    }

    sums = {}
    counts = {}

    for f in feedback:
        variant = user_variant[f["user_id"]]
        sums[variant] = sums.get(variant, 0) + f["rating"]
        counts[variant] = counts.get(variant, 0) + 1

    return {
        variant: sums[variant] / counts[variant]
        for variant in sums
    }


'''
Q19. Subscription funnel by variant

Context:
assignments:
- user_id
- variant

events:
- user_id
- event
- ts

Funnel steps:
1. paywall_seen
2. checkout_started
3. subscribed

Expected behavior:
Return:
variant -> {
    "assigned_users": ...,
    "paywall_seen_users": ...,
    "checkout_started_users": ...,
    "subscribed_users": ...
}

Rules:
- Count distinct assigned users.
- Funnel steps must happen in order.
- Events may be unsorted.
- Ignore events from unassigned users.

Buggy code:
'''

def subscription_funnel_by_variant(assignments, events):
    user_variant = {}

    for a in assignments:
        user_variant[a["user_id"]] = a["variant"]

    result = {}

    for a in assignments:
        variant = a["variant"]
        result.setdefault(variant, {
            "assigned_users": 0,
            "paywall_seen_users": 0,
            "checkout_started_users": 0,
            "subscribed_users": 0,
        })
        result[variant]["assigned_users"] += 1

    for e in events:
        variant = user_variant[e["user_id"]]

        if e["event"] == "paywall_seen":
            result[variant]["paywall_seen_users"] += 1
        elif e["event"] == "checkout_started":
            result[variant]["checkout_started_users"] += 1
        elif e["event"] == "subscribed":
            result[variant]["subscribed_users"] += 1

    return result


'''
Q20. End-to-end ChatGPT task success rate by category

Context:
tasks:
- task_id
- user_id
- started_at
- category

events:
- task_id
- event
- ts

A task is successful if:
1. it has at least one assistant_response after started_at
2. it has user_accepted within 30 minutes after started_at
3. it has no user_reported_failure within 30 minutes after started_at

Expected behavior:
Return category -> success_rate.

Buggy code:
'''

def task_success_rate_by_category(tasks, events):
    task_map = {
        t["task_id"]: t
        for t in tasks
    }

    success_by_category = {}
    total_by_category = {}

    for t in tasks:
        category = t["category"]
        total_by_category[category] = total_by_category.get(category, 0) + 1

    for e in events:
        task = task_map[e["task_id"]]
        category = task["category"]

        if e["event"] == "user_accepted":
            success_by_category[category] = success_by_category.get(category, 0) + 1

        if e["event"] == "user_reported_failure":
            success_by_category[category] = success_by_category.get(category, 0) - 1

    return {
        category: success_by_category.get(category, 0) / total_by_category[category]
        for category in total_by_category
    }


# ============================================================
# D4 PRODUCT-CONTEXT INTEGRATED DEBUGGING — ANSWER KEY
# ============================================================

'''
Q1 Answer Key — ChatGPT DAU

Main bugs:
1. Counts events, not distinct users.
2. Direct e["date"] can crash on malformed records.
3. Direct e["user_id"] can crash.
4. Counts user_id=None.
5. Mutates input by adding "counted".
6. Does not use sets per date.

Metric impact:
DAU is inflated by users with multiple events.
Malformed records can break the whole job.
Input mutation can corrupt downstream processing.

Fix direction:
Use date -> set(user_id).
Skip missing date/user_id and None user_id.
Return date -> len(user_set).
Do not mutate events.
'''


'''
Q2 Answer Key — Message-to-response success rate

Main bugs:
1. Processes all conversations together instead of per conversation.
2. Does not sort by conversation_id and timestamp.
3. Direct field access can crash.
4. Does not handle no user_message denominator.
5. A response in one conversation can satisfy a message in another conversation.
6. Does not correctly reset state when another user_message occurs before response.
7. Does not ignore malformed records.

Metric impact:
Success rate can be badly inflated or deflated due to cross-conversation contamination and unsorted logs.

Fix direction:
Group valid events by conversation_id.
Sort each conversation by ts.
For each user_message, check whether assistant_response appears before next user_message.
Return successes / total_user_messages, or None if denominator is zero.
'''


'''
Q3 Answer Key — API developer activation

Main bugs:
1. Returns list, not set; duplicates possible.
2. Uses <= 300, but 300 is not 2xx success.
3. Does not handle numeric string status_code.
4. Direct field access can crash.
5. Does not skip malformed status codes.
6. Does not ignore missing developer_id.
7. Does not exclude developer_id=None.

Metric impact:
Activation count can be inflated by duplicate successful requests and by treating 300 as success.

Fix direction:
Convert status_code safely to int.
Check 200 <= status < 300.
Add developer_id to set if valid and non-None.
'''


'''
Q4 Answer Key — Time to first successful API request

Main bugs:
1. Uses last signup, not earliest signup.
2. Does not ignore requests before signup.
3. Overwrites result with later successful requests instead of first success.
4. Treats only status_code == 200 as success, excluding other 2xx.
5. KeyError for requests from developers without signup.
6. Direct field access can crash.
7. Does not handle malformed status codes.
8. Does not handle malformed timestamps.

Metric impact:
Time-to-activation can be negative, too large, or based on wrong event.
Developers can be incorrectly included/excluded.

Fix direction:
Build earliest signup per developer.
For each successful request after signup, keep minimum request ts.
Return request_ts - signup_ts.
'''


'''
Q5 Answer Key — p95 latency by model

Main bugs:
1. Direct model_version access can crash.
2. if latency excludes latency 0.
3. Does not skip latency=None explicitly.
4. idx should be rank - 1.
5. For one value, current idx is out of range.
6. values.sort() mutates internal list; use sorted(values) for clarity.
7. Does not validate latency numeric if needed.

Metric impact:
p95 can be wrong or crash, especially for small groups.
Latency 0 is incorrectly dropped.

Fix direction:
Filter valid model_version and latency_ms is not None.
Use rank = ceil(0.95 * n), idx = rank - 1.
Use sorted copy.
'''


'''
Q6 Answer Key — Cost per successful task

Main bugs:
1. Only includes cost of successful attempts; requirement says all attempts.
2. Counts success events, not distinct successful tasks.
3. Duplicate success events inflate denominator.
4. Direct field access can crash.
5. Does not ignore missing/None cost.
6. Does not return None if no task succeeded.
7. Does not include failed/timeout costs.

Metric impact:
Cost per success is understated if failed attempts are excluded.
Repeated success logs distort denominator.

Fix direction:
Track total_cost across all valid attempts.
Track successful_task_ids as a set.
Return total_cost / len(successful_task_ids), or None if empty.
'''


'''
Q7 Answer Key — Tool-call failure rate

Main bugs:
1. totals only increments for non-failure statuses, not all valid calls.
2. Success denominator is wrong.
3. Invalid statuses are treated as non-failure totals.
4. Direct field access can crash.
5. Missing status/tool_name not handled.
6. A tool with only failures may be absent from totals and omitted.
7. Division by zero possible depending implementation.

Metric impact:
Failure rates are inflated, deflated, or missing for high-failure tools.

Fix direction:
For valid status in {"success", "failure"}, increment total for tool.
Increment failure count only for failure.
Return failures / totals.
'''


'''
Q8 Answer Key — Agent completion within time limit

Main bugs:
1. Ignores timestamps entirely.
2. Does not use first started timestamp.
3. Counts completed even if before start.
4. Does not enforce max_minutes window.
5. Does not handle unsorted events.
6. Direct field access can crash.
7. Does not return None if no started tasks.
8. Does not dedupe properly around first start vs multiple starts.

Metric impact:
Completion rate can be inflated by late completions or pre-start completions.

Fix direction:
Build first_start_ts per task.
For completed events, require task started and start_ts <= completed_ts <= start_ts + max_minutes.
Deduplicate completed tasks.
Return len(completed) / len(started), or None.
'''


'''
Q9 Answer Key — Regeneration rate

Main bugs:
1. Processes all conversations together.
2. Does not sort by conversation and ts.
3. Multiple regenerate clicks after one response are counted multiple times.
4. Does not reset correctly at next assistant_response per conversation.
5. Direct field access can crash.
6. Does not return None if no assistant_response.
7. Regenerate before any response can be incorrectly counted depending prior state from other conversation.

Metric impact:
Regeneration rate can be inflated by repeated clicks or cross-conversation state leakage.

Fix direction:
Group by conversation_id.
Sort by ts.
For each assistant_response, open a pending response.
If regenerate_clicked occurs before next assistant_response, mark that response regenerated once.
Return regenerated_responses / total_responses.
'''


'''
Q10 Answer Key — Source-click rate

Main bugs:
1. Counts events, not distinct searches.
2. Counts source_clicked before answer_shown.
3. Counts multiple clicks for same search multiple times.
4. Does not use first answer_shown.
5. Does not handle unsorted events.
6. Direct field access can crash.
7. Does not return None if no answer_shown.

Metric impact:
Click rate can exceed 1 or be inflated by repeated clicks.
Attribution is wrong if click happened before answer was shown.

Fix direction:
Build first_answer_shown_ts per search_id.
Then find searches with any source_clicked after shown_ts.
Return clicked_searches / shown_searches.
'''


'''
Q11 Answer Key — Workspace activation

Main bugs:
1. Uses latest workspace_created, not first.
2. Does not enforce 7-day activation window.
3. Counts joined events, not distinct joined users.
4. Counts events before workspace creation.
5. Counts message_sent outside window.
6. Direct field access can crash.
7. Missing user_id on member_joined not handled.
8. Events may be unsorted, but logic assumes order.

Metric impact:
Activation is inflated by old joins/messages or duplicate joined events.

Fix direction:
Find first created_ts per workspace.
For events within [created_ts, created_ts + 7], collect distinct joined users and message flag.
Activated if len(joined_users) >= 2 and has_message.
'''


'''
Q12 Answer Key — Seat utilization

Main bugs:
1. Counts duplicate seat records multiple times.
2. Counts message events, not distinct utilized seats.
3. Counts users who sent messages but do not have a seat.
4. Direct field access can crash.
5. Does not dedupe workspace_id + user_id.
6. Events missing fields not handled.
7. Multiple messages by same user inflate utilization.

Metric impact:
Seat utilization can exceed 1 and be inflated by power users.

Fix direction:
Build seat_set = {(workspace_id, user_id)}.
Total seats per workspace from distinct seat_set.
Build used_set from message_sent events only if key in seat_set.
Return len(used seats) / total seats by workspace.
'''


'''
Q13 Answer Key — Pairwise model win rates

Main bugs:
1. Ties are included in denominators, but requirement says non-tie comparisons only.
2. Malformed records can crash.
3. Invalid winner values not handled.
4. Models appearing only in ties should return None, but current returns 0 / total.
5. Does not dedupe prompt_id if needed; depending eval design repeated prompt could overweight.
6. Direct field access can crash.

Metric impact:
Win rates are diluted by ties and may misrepresent model preference.

Fix direction:
For winner in {"a", "b"} only:
- Increment denominator for both models.
- Increment win for winning model.
Track models that appear in ties too.
Return None for model with zero non-tie comparisons.
'''


'''
Q14 Answer Key — Hallucination report rate

Main bugs:
1. Counts logs, not distinct response_id.
2. Duplicate logs inflate denominator and numerator.
3. Conflicting model_version should use first valid model_version, but code uses every row.
4. Direct field access can crash.
5. Missing user_reported_issue can crash.
6. Does not ignore missing response_id or model_version.
7. Same response reported multiple times can inflate numerator.

Metric impact:
Hallucination rate can be inflated by duplicate reports/logs or distorted by model conflicts.

Fix direction:
Build response_id -> first model_version.
Track response_ids with hallucination.
Then aggregate distinct response_ids by assigned model_version.
'''


'''
Q15 Answer Key — Prompt category distribution

Main bugs:
1. Counts rows, not distinct prompt_id.
2. Does not use first category for duplicate prompt_id.
3. Direct field access can crash.
4. Missing prompt_id/category not handled.
5. Division by zero if no valid prompts.
6. Repeated prompt logs distort distribution.

Metric impact:
Category distribution is biased toward prompts with duplicate logs.

Fix direction:
Build prompt_id -> first category.
Count categories over distinct prompt IDs.
Return {} if no valid prompts.
'''


'''
Q16 Answer Key — Developer day-N retention

Main bugs:
1. Uses last signup, not earliest signup.
2. Active set ignores activity date, so any successful request counts.
3. Does not check exactly signup_date + n.
4. Treats only status_code == 200 as success, excluding other 2xx.
5. Does not validate n >= 0.
6. Direct field access and date parsing can crash.
7. Does not handle malformed status_code.
8. Division by zero if no valid signups.
9. Does not dedupe developer-date pairs carefully.

Metric impact:
Retention is massively inflated because any future activity counts.

Fix direction:
Parse earliest signup date per developer.
Build set of (developer_id, request_date) for successful requests.
For each signup developer, check (developer_id, signup_date + n).
Return retained / total, or None.
'''


'''
Q17 Answer Key — Rollout guardrail summary

Main bugs:
1. Uses one shared count for latency, error, and cost, but each has separate valid denominator.
2. Direct field access can crash when latency/cost missing.
3. error missing or non-boolean not handled.
4. latency_ms=None or cost=None can crash.
5. Rows with invalid latency still counted in latency denominator.
6. Rows with invalid cost still counted in cost denominator.
7. Variants missing not handled.
8. Division by zero possible.

Metric impact:
Guardrail metrics can be wrong due to mixed denominators.
A rollout may look safe or unsafe incorrectly.

Fix direction:
For each variant, track:
latency_sum, latency_count
cost_sum, cost_count
error_count, error_denom
Compute each metric using its own denominator.
Return None when denominator is zero.
'''


'''
Q18 Answer Key — User-level feedback by variant

Main bugs:
1. Averages raw feedback events, not user-level averages.
2. Power users dominate results.
3. Feedback from unassigned users causes KeyError.
4. Duplicate assignments not handled.
5. Missing/None ratings not handled.
6. Users with no valid feedback should be excluded from rating average but variant should still appear as None if no feedback.
7. Direct field access can crash.

Metric impact:
Variant satisfaction can be biased by users who submit many ratings.

Fix direction:
Deduplicate assignments by first assignment per user.
Build ratings per assigned user.
Compute user average rating.
Then average user averages by variant.
Return None for variants with no users with valid feedback.
'''


'''
Q19 Answer Key — Subscription funnel by variant

Main bugs:
1. Duplicate assignments inflate assigned_users.
2. Last assignment wins; requirement says first assignment per user.
3. Counts events, not distinct users.
4. Does not enforce funnel order.
5. Events may be unsorted.
6. Events from unassigned users cause KeyError.
7. Duplicate events inflate step counts.
8. Direct field access can crash.
9. A subscribed event without prior paywall/checkout is counted.

Metric impact:
Funnel steps can exceed assigned users and overstate conversion.
Step progression is not valid.

Fix direction:
Deduplicate first assignment per user.
Initialize assigned_users from distinct assigned users by variant.
For each assigned user, sort their events by ts.
Track funnel progress through paywall_seen -> checkout_started -> subscribed.
Count distinct users who reach each step.
'''


'''
Q20 Answer Key — Task success rate by category

Main bugs:
1. Duplicate task records overwrite; requirement says first task record per task_id.
2. Denominator counts task rows, not distinct valid tasks.
3. Events for unknown task_id cause KeyError.
4. Does not check assistant_response condition.
5. Does not enforce user_accepted within 30 minutes.
6. Does not ignore events before started_at.
7. Does not enforce no user_reported_failure within 30 minutes.
8. Subtracting from success count for failures can produce negative success.
9. Multiple user_accepted events can double count success.
10. Direct field access can crash.
11. Missing category/started_at not handled.

Metric impact:
Success rate can be inflated, negative, or based on invalid tasks.
The metric does not match the product definition.

Fix direction:
Build first valid task per task_id.
For each task, inspect events where started_at <= ts <= started_at + 30.
A task succeeds if:
- has assistant_response in window
- has user_accepted in window
- has no user_reported_failure in window
Aggregate distinct task success by category.
Return successes / total valid tasks per category.
'''