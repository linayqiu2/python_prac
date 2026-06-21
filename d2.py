# ============================================================
# D2 DEBUGGING SMALL FUNCTIONS — QUESTIONS
# ============================================================

'''
Q1. Deduplicate event records by event_id

Expected behavior:
Return a new list containing only the first record for each event_id.
Ignore records missing event_id.
Do not mutate input records.
Preserve input order of first occurrences.

Buggy code:
'''

def dedupe_events(events):
    seen = set()
    output = []

    for e in events:
        event_id = e["event_id"]

        if event_id in seen:
            e["duplicate"] = True
            continue

        seen.add(event_id)
        e["duplicate"] = False
        output.append(e)

    return output


'''
Q2. Merge user settings safely

Expected behavior:
Merge default settings with user overrides.
Nested dictionaries should be merged one level deep.
Do not mutate either input dictionary.

Example:
defaults = {
    "theme": "light",
    "notifications": {"email": True, "sms": False},
}
overrides = {
    "notifications": {"sms": True}
}

Expected:
{
    "theme": "light",
    "notifications": {"email": True, "sms": True},
}

Buggy code:
'''

def merge_settings(defaults, overrides):
    result = defaults

    for key, value in overrides.items():
        if isinstance(value, dict):
            result[key].update(value)
        else:
            result[key] = value

    return result


'''
Q3. Parse simple log lines

Expected behavior:
Parse log lines like:
"ts=100 user_id=42 status=500 endpoint=/chat"

Return a list of dictionaries:
[
    {"ts": 100, "user_id": "42", "status": 500, "endpoint": "/chat"}
]

Rules:
- Ignore malformed tokens without "=".
- Ignore lines missing ts or status.
- Convert ts and status to integers.
- Keep user_id and endpoint as strings if present.
- Skip lines with invalid integer values.

Buggy code:
'''

def parse_logs(lines):
    output = []

    for line in lines:
        record = {}
        parts = line.split(" ")

        for part in parts:
            key, value = part.split("=")
            record[key] = value

        record["ts"] = int(record["ts"])
        record["status"] = int(record["status"])

        output.append(record)

    return output


'''
Q4. Top K items by score

Expected behavior:
Given a list of records with "item_id" and "score", return the top k item_ids.
Sort by score descending.
Break ties by smaller item_id.
Ignore records missing item_id or score.
If k <= 0, return [].

Buggy code:
'''

def top_k_items(records, k):
    records.sort(key=lambda r: r["score"])
    result = []

    for i in range(k):
        result.append(records[i]["item_id"])

    return result


'''
Q5. Accumulate user history

Expected behavior:
append_event(history, user_id, event) should return a dictionary mapping user_id to a list of events.
It should not share state across independent calls unless history is explicitly passed.
It should not mutate the event object.

Buggy code:
'''

def append_event(user_id, event, history={}):
    if user_id not in history:
        history[user_id] = []

    event["processed"] = True
    history[user_id].append(event)

    return history


'''
Q6. Build rows from columns

Expected behavior:
Given:
columns = ["user_id", "event"]
values = [
    [1, "login"],
    [2, "purchase"],
]

Return:
[
    {"user_id": 1, "event": "login"},
    {"user_id": 2, "event": "purchase"},
]

Rules:
- Skip rows whose length does not match columns.
- Each output row should be an independent dictionary.

Buggy code:
'''

def rows_from_columns(columns, values):
    output = []
    row = {}

    for vals in values:
        for i in range(len(columns)):
            row[columns[i]] = vals[i]
        output.append(row)

    return output


'''
Q7. Rolling 7-day active users

Expected behavior:
Given events with "user_id" and "date" as YYYY-MM-DD strings, return a dictionary:
date -> number of distinct users active in the 7-day window ending on that date, inclusive.

For date D, include events with dates from D-6 through D inclusive.
Ignore malformed records.

Buggy code:
'''

from datetime import datetime, timedelta

def rolling_7d_active_users(events):
    by_date = {}

    for e in events:
        d = datetime.strptime(e["date"], "%Y-%m-%d").date()
        by_date.setdefault(d, []).append(e["user_id"])

    result = {}

    for d in by_date:
        users = []
        start = d - timedelta(days=7)

        for event_date, user_ids in by_date.items():
            if event_date > start and event_date < d:
                users.extend(user_ids)

        result[d.isoformat()] = len(users)

    return result


'''
Q8. Conversion within 24 hours of exposure

Expected behavior:
Given exposures and events:
- exposures have user_id, exposed_at
- events have user_id, event, ts
Return fraction of exposed users who purchased within 24 hours after first exposure.
Use first exposure per user.
Deduplicate converted users.
Ignore events before exposure.
Return None if no exposed users.

Timestamps are integer hours.

Buggy code:
'''

def conversion_within_24h(exposures, events):
    exposure_time = {}

    for x in exposures:
        exposure_time[x["user_id"]] = x["exposed_at"]

    converted = 0

    for e in events:
        if e["event"] == "purchase":
            user_id = e["user_id"]
            if e["ts"] - exposure_time[user_id] <= 24:
                converted += 1

    return converted / len(exposures)


'''
Q9. p95 latency by endpoint

Expected behavior:
For each endpoint, compute p95 latency using nearest-rank method.
rank = ceil(0.95 * n)
Return the value at rank - 1 in sorted order.
Ignore missing or None latency.
Return {} if no valid records.

Buggy code:
'''

import math

def p95_latency_by_endpoint(requests):
    values = {}

    for r in requests:
        endpoint = r["endpoint"]
        latency = r.get("latency_ms")

        if latency:
            values.setdefault(endpoint, []).append(latency)

    result = {}

    for endpoint, nums in values.items():
        nums.sort()
        idx = math.ceil(0.95 * len(nums))
        result[endpoint] = nums[idx]

    return result


'''
Q10. Deduped task success rate

Expected behavior:
Each task event has task_id, user_id, status.
status can be "success", "failure", or "running".

Return:
number of tasks that eventually succeeded / number of distinct tasks

Rules:
- Deduplicate by task_id.
- A task is successful if it has at least one success event.
- Ignore records missing task_id or status.
- Return None if there are no valid tasks.

Buggy code:
'''

def task_success_rate(events):
    total = 0
    success = 0

    for e in events:
        total += 1
        if e["status"] == "success":
            success += 1

    return success / total


'''
Q11. Cohort day-1 retention

Expected behavior:
signups: records with user_id and signup_date
activity: records with user_id and date

Return dictionary:
signup_date -> day_1_retention

Day-1 retained means active exactly one day after signup date.
If user signs up multiple times, use earliest signup.
Ignore malformed dates and missing fields.

Buggy code:
'''

def cohort_day1_retention(signups, activity):
    signup_by_user = {}

    for s in signups:
        signup_by_user[s["user_id"]] = s["signup_date"]

    active = set()
    for a in activity:
        if a["user_id"] in signup_by_user:
            active.add(a["user_id"])

    totals = {}
    retained = {}

    for user_id, signup_date in signup_by_user.items():
        totals[signup_date] = totals.get(signup_date, 0) + 1
        if user_id in active:
            retained[signup_date] = retained.get(signup_date, 0) + 1

    return {d: retained.get(d, 0) / totals[d] for d in totals}


'''
Q12. Deterministic sample of users

Expected behavior:
Return users assigned to a sample based on deterministic bucketing.
A user is included if:
sum(ord(c) for c in seed + "|" + str(user_id)) % 100 < sample_percent

Rules:
- sample_percent must be between 0 and 100 inclusive.
- Preserve input order.
- Do not use random.
- Do not use Python built-in hash().
- Ignore None user_id.

Buggy code:
'''

import random

def deterministic_sample_users(user_ids, sample_percent, seed):
    output = []

    for user_id in user_ids:
        if random.random() * 100 <= sample_percent:
            output.append(user_id)

    return output


'''
Q13. Retry API call

Expected behavior:
Call api_call(payload).
Retry up to max_retries times after failures.
A failure is an exception or a response with status_code >= 500.
Do not retry 4xx errors.
Return the first successful response.
Return None if all retries fail.

Assume response has .status_code.

Buggy code:
'''

def call_with_retry(api_call, payload, max_retries):
    attempts = 0

    while attempts < max_retries:
        try:
            response = api_call(payload)
            if response.status_code == 200:
                return response
            else:
                attempts += 1
        except Exception:
            return None

    return response


'''
Q14. Parse model API response

Expected behavior:
Given a response dictionary from a model API, extract:
- request_id
- model
- output_text
- prompt_tokens
- completion_tokens

Rules:
- Return None if request_id or model is missing.
- output_text should be "" if missing.
- token counts should default to 0 if missing.
- Do not crash on missing nested fields.

Buggy code:
'''

def parse_model_response(resp):
    return {
        "request_id": resp["request_id"],
        "model": resp["model"],
        "output_text": resp["choices"][0]["message"]["content"],
        "prompt_tokens": resp["usage"]["prompt_tokens"],
        "completion_tokens": resp["usage"]["completion_tokens"],
    }


'''
Q15. Write exposure log once

Expected behavior:
log_exposure_once should append an exposure event only if that user_id + experiment_id pair has not already been logged.

Rules:
- Do not log duplicates.
- Do not mutate the input event.
- Return True if logged, False if duplicate or invalid.
- Invalid if user_id or experiment_id is missing.

Buggy code:
'''

def log_exposure_once(event, exposure_log):
    key = event["user_id"]

    if key in exposure_log:
        return False

    event["logged"] = True
    exposure_log[key] = event
    return True


'''
Q16. Validate rollout config

Expected behavior:
Validate rollout config:
{
    "experiment_id": "exp_123",
    "variants": {"control": 50, "treatment": 50},
    "salt": "abc"
}

Rules:
- experiment_id must be non-empty string.
- salt must be non-empty string.
- variants must be a non-empty dict.
- variant names must be non-empty strings.
- weights must be non-negative integers.
- bool weights are invalid.
- total weight must equal 100.

Buggy code:
'''

def validate_rollout_config(config):
    if not config["experiment_id"]:
        return False

    if "variants" not in config:
        return False

    total = 0
    for variant, weight in config["variants"].items():
        if weight < 0:
            return False
        total += weight

    return total <= 100


'''
Q17. Batch process events with partial failures

Expected behavior:
Given events and a process_event function:
- Process each valid event independently.
- Continue processing if one event fails.
- Return {"success": n, "failed": m, "errors": [...]}.
- Missing event_id is invalid and should count as failed.
- errors should include event_id when available and error message.

Buggy code:
'''

def batch_process_events(events, process_event):
    success = 0

    for e in events:
        process_event(e)
        success += 1

    return {
        "success": success,
        "failed": 0,
        "errors": [],
    }


'''
Q18. Simple cache wrapper

Expected behavior:
get_user_profile(user_id, fetch_user, cache) should:
- Return cached profile if present.
- Otherwise fetch profile using fetch_user(user_id).
- Store fetched profile in cache.
- Return None if user_id is None or fetch fails.
- Do not let callers mutate cached profile accidentally.

Buggy code:
'''

def get_user_profile(user_id, fetch_user, cache={}):
    if user_id in cache:
        return cache[user_id]

    profile = fetch_user(user_id)
    cache[user_id] = profile
    return profile


'''
Q19. Rate limit checker

Expected behavior:
Given request timestamps for one user, decide whether a new request at current_ts is allowed.
Allow at most max_requests in the previous window_seconds, inclusive of current_ts and exclusive of current_ts - window_seconds.

Function should return True if allowed, False if rate-limited.

Buggy code:
'''

def is_allowed_request(previous_timestamps, current_ts, max_requests, window_seconds):
    count = 0

    for ts in previous_timestamps:
        if current_ts - window_seconds <= ts <= current_ts:
            count += 1

    if count <= max_requests:
        return True
    return False


'''
Q20. Backfill checkpoint update

Expected behavior:
You are processing daily partitions in order.
Given partitions and process_partition, return the latest successfully processed partition.

Rules:
- If processing a partition fails, stop immediately.
- Do not mark failed partition as processed.
- Return previous checkpoint if no new partition succeeds.
- Partitions are strings in YYYY-MM-DD format and may be unsorted.
- Only process partitions greater than previous_checkpoint.

Buggy code:
'''

def run_backfill(partitions, previous_checkpoint, process_partition):
    checkpoint = previous_checkpoint

    for p in partitions:
        if p >= previous_checkpoint:
            checkpoint = p
            process_partition(p)

    return checkpoint


# ============================================================
# D2 ANSWER KEY
# ============================================================

'''
Q1 Answer Key

Main bugs:
1. Direct e["event_id"] can raise KeyError.
2. Missing event_id records should be ignored.
3. Mutates input records by adding "duplicate".
4. Duplicate records should simply be skipped, not modified.
5. Returning original dict references may be okay if not mutated, but safer to return copies.
6. event_id=None should likely be treated as invalid unless explicitly allowed.

Correct fix direction:
- Use e.get("event_id").
- Skip missing/None event_id.
- Use a seen set.
- Append dict(e) to avoid mutation surprises.
'''


'''
Q2 Answer Key

Main bugs:
1. result = defaults aliases the original defaults dict.
2. Nested result[key].update(value) mutates defaults nested dict.
3. Crashes if overrides has a nested dict for a key missing in defaults.
4. If defaults has non-dict and override has dict, result[key].update fails.
5. Only handles dict override values, not dict default values carefully.
6. Does not copy nested dictionaries.

Correct fix direction:
- Create a new result dict.
- For each defaults key, shallow-copy nested dicts.
- For overrides:
  - if both existing result[key] and override value are dicts, merge into a new dict.
  - otherwise assign a copied value if dict.
'''


'''
Q3 Answer Key

Main bugs:
1. part.split("=") crashes for malformed tokens without "=".
2. part.split("=") can produce more than 2 pieces if value contains "=".
3. Missing ts/status causes KeyError.
4. Invalid integer values cause ValueError.
5. Empty tokens from repeated spaces can cause errors.
6. Does not skip malformed lines.

Correct fix direction:
- Split line into tokens.
- For each token, only process if "=" in token.
- Use token.split("=", 1).
- Require ts and status.
- Convert ts/status inside try/except.
- Skip malformed lines.
'''


'''
Q4 Answer Key

Main bugs:
1. Mutates input records with records.sort().
2. Sorts ascending by score, should be descending.
3. No tie-breaker by smaller item_id.
4. Direct key access crashes on malformed records.
5. If k > valid records, index error.
6. If k <= 0, should return [].
7. Does not filter missing score/item_id.

Correct fix direction:
- Build valid list.
- Sort with key=lambda r: (-r["score"], r["item_id"]).
- Return first k item_ids.
- Do not mutate input.
'''


'''
Q5 Answer Key

Main bugs:
1. Mutable default argument history={} persists across calls.
2. Function signature order is confusing relative to expected append_event(history, user_id, event).
3. Mutates event by adding "processed".
4. Stores original event object, so caller mutations later affect history.
5. No handling of missing/None user_id.
6. No way to pass empty explicit history safely if default is shared.

Correct fix direction:
- Use history=None default.
- If history is None, create {}.
- Copy event before adding metadata.
- Avoid mutating caller-owned event.
'''


'''
Q6 Answer Key

Main bugs:
1. row = {} created once outside loop, so every output element references same dict.
2. Does not skip rows whose length does not match columns.
3. vals[i] can raise IndexError.
4. If vals is longer than columns, extra values silently ignored instead of skip.
5. Does not handle empty columns explicitly.
6. Output rows are not independent.

Correct fix direction:
- For each vals, first check len(vals) == len(columns).
- Create row = {} inside outer loop.
- Fill row and append.
'''


'''
Q7 Answer Key

Main bugs:
1. Direct key access can crash on malformed records.
2. Does not dedupe users; uses list instead of set.
3. Window start should be D - 6 days, not D - 7 days.
4. Conditions exclude current date because event_date < d.
5. Conditions are confusing; expected window is start <= event_date <= d.
6. Does not handle malformed dates.
7. Only computes result for dates that appear in by_date, which may be acceptable unless calendar completeness is required.

Correct fix direction:
- Parse valid records only.
- Store users in sets by date.
- For each date D, union users from D-6 through D inclusive.
'''


'''
Q8 Answer Key

Main bugs:
1. For duplicate exposures, uses last exposure instead of first.
2. Does not handle malformed exposure records.
3. KeyError if purchase user was not exposed.
4. Counts purchase before exposure if e["ts"] - exposure_time[user_id] is negative.
5. Does not dedupe converted users; multiple purchases inflate numerator.
6. Denominator uses len(exposures), not distinct exposed users.
7. Return should be None if no exposed users.
8. Should require 0 <= event_ts - exposed_at <= 24.

Correct fix direction:
- Build first_exposure per user.
- Denominator = len(first_exposure).
- Iterate purchase events, require exposed user and timestamp within [0, 24].
- Add user to converted set.
'''


'''
Q9 Answer Key

Main bugs:
1. Direct r["endpoint"] can raise KeyError.
2. if latency excludes latency 0.
3. Does not skip None correctly.
4. idx should be rank - 1, not rank.
5. For n=1, idx becomes 1 and errors.
6. nums.sort() mutates internal list; not input, but sorted(nums) is cleaner.
7. Does not handle empty values safely.

Correct fix direction:
- Filter valid records.
- Include latency == 0.
- rank = ceil(0.95 * n)
- idx = rank - 1.
'''


'''
Q10 Answer Key

Main bugs:
1. Counts events, not distinct tasks.
2. Multiple events for the same task inflate denominator.
3. Multiple success events inflate numerator.
4. Direct key access can crash on malformed records.
5. Does not ignore missing task_id/status.
6. Return should be None if no valid tasks.
7. "eventually succeeded" means any success event per task.

Correct fix direction:
- Track all valid task_ids in a set.
- Track successful task_ids in a set.
- Return len(successful_tasks) / len(all_tasks).
'''


'''
Q11 Answer Key

Main bugs:
1. Duplicate signups use last signup, not earliest.
2. Activity is counted for any date, not exactly signup_date + 1.
3. Direct key access can crash.
4. Malformed dates not handled.
5. Active set loses activity date information.
6. Users active before signup could count incorrectly.
7. Missing fields can crash.

Correct fix direction:
- Parse signup dates and keep earliest per user.
- Build activity pairs (user_id, date).
- For each user, check whether (user_id, signup_date + 1 day) exists.
- Aggregate by signup cohort date.
'''


'''
Q12 Answer Key

Main bugs:
1. Uses random, so sample is not deterministic.
2. Does not use seed.
3. Uses <= sample_percent; boundary should be bucket < sample_percent.
4. Does not validate sample_percent range.
5. Does not ignore None user_id.
6. Does not preserve deterministic assignment across calls.
7. sample_percent=0 can still include users due to random condition if random is 0.

Correct fix direction:
- Validate 0 <= sample_percent <= 100.
- For each non-None user_id:
  bucket = sum(ord(c) for c in seed + "|" + str(user_id)) % 100
  include if bucket < sample_percent.
'''


'''
Q13 Answer Key

Main bugs:
1. while attempts < max_retries may mean total attempts excludes initial attempt depending on interpretation.
2. Catches exception and immediately returns None instead of retrying.
3. Retries all non-200 statuses, including 4xx, but 4xx should not retry.
4. Treats only 200 as success; other 2xx may be success depending on API.
5. Returns response even if response may be undefined when all attempts raised exceptions.
6. No backoff/sleep, though that may be optional for small function.
7. Does not increment attempts on exception.

Correct fix direction:
- Define total attempts as max_retries + 1 or clarify.
- Retry exceptions and 5xx.
- Do not retry 4xx.
- Return first response with status_code < 500 and not 4xx failure according to spec.
- Return None after all attempts fail.
'''


'''
Q14 Answer Key

Main bugs:
1. Missing request_id crashes, should return None.
2. Missing model crashes, should return None.
3. Missing choices crashes.
4. Empty choices list crashes.
5. Missing message/content crashes; output_text should default to "".
6. Missing usage crashes; token counts should default to 0.
7. Missing prompt_tokens/completion_tokens should default to 0.

Correct fix direction:
- Check request_id and model using resp.get().
- Safely navigate choices.
- Safely navigate usage.
- Default output_text to "" and tokens to 0.
'''


'''
Q15 Answer Key

Main bugs:
1. Key only uses user_id, but uniqueness should be user_id + experiment_id.
2. Direct field access crashes on missing fields.
3. Does not reject invalid event missing user_id or experiment_id.
4. Mutates event by adding "logged".
5. Stores original event object, allowing caller mutation to affect log.
6. exposure_log could contain keys with different structure depending on design.

Correct fix direction:
- key = (user_id, experiment_id).
- Return False if missing either.
- If key exists, return False.
- Store dict(event), optionally with logged_at if provided externally.
'''


'''
Q16 Answer Key

Main bugs:
1. Direct config["experiment_id"] can crash if missing.
2. Does not validate config is dict.
3. Does not validate experiment_id is string.
4. Does not validate salt exists or is non-empty string.
5. Does not validate variants is non-empty dict.
6. Does not validate variant names are strings/non-empty.
7. Does not reject bool weights.
8. Does not check weights are integers.
9. Allows total < 100 because it uses <= 100; should equal 100.

Correct fix direction:
- Validate config type.
- Validate experiment_id and salt.
- Validate variants dict.
- Loop through name/weight with strict type checks.
- Reject bool.
- Require total == 100.
'''


'''
Q17 Answer Key

Main bugs:
1. One failing event stops entire batch.
2. Missing event_id is not counted as failed.
3. Does not collect errors.
4. failed count always 0.
5. No try/except around process_event.
6. Does not include event_id when available.
7. Does not distinguish invalid input from processing exception.

Correct fix direction:
- Initialize success, failed, errors.
- For each event:
  - if missing event_id: failed += 1, append error.
  - else try process_event(e).
  - on exception: failed += 1, append error.
  - else success += 1.
'''


'''
Q18 Answer Key

Main bugs:
1. Mutable default cache={} persists across calls.
2. user_id=None should return None.
3. fetch_user exceptions are not handled.
4. Returns cached profile object directly, so caller can mutate cached value.
5. Stores fetched profile object directly, so external mutation may affect cache.
6. Does not handle fetch_user returning None explicitly.
7. No validation of cache argument.

Correct fix direction:
- Use cache as required argument or default None.
- If cache is None, create local cache.
- Return None for user_id is None.
- Wrap fetch in try/except.
- Store and return shallow copies if profile is a dict.
'''


'''
Q19 Answer Key

Main bugs:
1. Window should be exclusive of current_ts - window_seconds, but code uses <= lower bound.
2. To decide whether new request is allowed, you need to count previous requests in window and allow if count < max_requests, not <=.
3. If max_requests <= 0, should likely return False.
4. Does not ignore future timestamps > current_ts? It excludes them, okay.
5. Does not validate window_seconds.
6. Boundary at current_ts is okay if previous_timestamps can include current request; but function says previous timestamps, so current_ts usually not included.

Correct fix direction:
- Count timestamps where current_ts - window_seconds < ts <= current_ts.
- Return count < max_requests.
- Validate max_requests > 0 and window_seconds > 0.
'''


'''
Q20 Answer Key

Main bugs:
1. Partitions may be unsorted; should sort before processing.
2. Processes p >= previous_checkpoint, but should process p > previous_checkpoint.
3. Updates checkpoint before process_partition succeeds.
4. If process_partition fails, failed partition may be incorrectly marked processed.
5. Does not stop on failure.
6. Does not handle exceptions.
7. If no partition succeeds, should return previous_checkpoint.
8. May reprocess previous checkpoint due to >=.

Correct fix direction:
- Sort partitions.
- For each p in sorted(partitions):
  - skip p <= previous_checkpoint.
  - try process_partition(p)
  - if success, checkpoint = p
  - if failure, break
- Return checkpoint.
'''