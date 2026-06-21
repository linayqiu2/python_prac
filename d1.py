
#########################################################
# D1
#########################################################
'''
Q1. Count distinct active users

Context:
You are given event logs. Each event may or may not contain "user_id".

Expected behavior:
Return the number of distinct non-null users who appear in the events.

Buggy code:
'''

def count_active_users(events):
    users = []
    for e in events:
        users.append(e["user_id"])
    return len(users)


'''
Q2. Count events by type

Context:
Each event may contain an "event" field.

Expected behavior:
Return a dictionary mapping event type to count.
Ignore records missing "event".

Buggy code:
'''

def count_events_by_type(events):
    counts = {}
    for e in events:
        event = e["event"]
        if event not in counts:
            counts[event] = 0
        else:
            counts[event] += 1
    return counts


'''
Q3. First event per user, unsorted input

Context:
Events may not be sorted. Each valid event has "user_id" and "ts".

Expected behavior:
Return a dictionary mapping each user_id to the event with the smallest timestamp.
If two events have the same timestamp for the same user, keep the earlier input record.

Buggy code:
'''

def first_event_per_user_unsorted(events):
    result = {}
    for e in events:
        user_id = e["user_id"]
        if user_id not in result:
            result[user_id] = e
        elif e["ts"] <= result[user_id]["ts"]:
            result[user_id] = e
    return result


'''
Q4. Top K users by event count

Context:
Given events with "user_id", return the top k users by number of events.
Break ties by smaller user_id.

Expected behavior:
top_k_users_by_event_count(
    [{"user_id": 3}, {"user_id": 1}, {"user_id": 1}, {"user_id": 2}, {"user_id": 2}],
    2
)
should return [1, 2].

Buggy code:
'''

def top_k_users_by_event_count(events, k):
    counts = {}
    for e in events:
        counts[e["user_id"]] = counts.get(e["user_id"], 0) + 1

    users = sorted(counts.keys(), key=lambda u: counts[u])
    return users[:k]


'''
Q5. Inner join users and events

Context:
users contains user profiles.
events contains user actions.

Expected behavior:
Return enriched events only for events whose user_id exists in users.
Preserve event order.
Do not mutate input dictionaries.
If duplicate user profiles exist, use the last profile.

Buggy code:
'''

def inner_join_users_events(users, events):
    user_map = {}
    for u in users:
        user_map[u["user_id"]] = u

    output = []
    for e in events:
        profile = user_map[e["user_id"]]
        e["country"] = profile["country"]
        output.append(e)

    return output


'''
Q6. Left join users and events

Context:
Keep all events.
If user profile is missing, set country to None.
Do not mutate input dictionaries.

Buggy code:
'''

def left_join_users_events(users, events):
    user_map = {u["user_id"]: u for u in users}
    output = []

    for e in events:
        profile = user_map.get(e["user_id"])
        country = profile["country"]
        row = e
        row["country"] = country
        output.append(row)

    return output


'''
Q7. Latest record per account

Context:
records are account snapshots.
Each valid record has "account_id" and "ds" in YYYY-MM-DD format.

Expected behavior:
Return latest record per account.
If two records for the same account have the same ds, keep the later input record.

Buggy code:
'''

def latest_record_per_account(records):
    latest = {}
    for r in records:
        account_id = r["account_id"]
        if account_id not in latest:
            latest[account_id] = r
        elif r["ds"] > latest[account_id]["ds"]:
            latest[account_id] = r
    return latest


'''
Q8. Signup-to-purchase conversion rate

Context:
Events have user_id, event, and ts.
Compute fraction of signup users who purchased after their first signup.

Expected behavior:
Denominator: users with at least one signup.
Numerator: users with at least one purchase after first signup.
Return None if no signup users.

Buggy code:
'''

def signup_to_purchase_conversion(events):
    signed_up = set()
    purchased = set()

    for e in events:
        if e["event"] == "signup":
            signed_up.add(e["user_id"])
        if e["event"] == "purchase":
            purchased.add(e["user_id"])

    return len(signed_up & purchased) / len(events)


'''
Q9. Day-7 retention

Context:
signups has user_id and signup_date.
activity has user_id and date.
Dates are YYYY-MM-DD strings.

Expected behavior:
Return fraction of signup users active exactly 7 days after earliest signup date.
Return None if no valid signup users.

Buggy code:
'''

from datetime import datetime, timedelta

def day_7_retention(signups, activity):
    signup_map = {}
    for s in signups:
        signup_map[s["user_id"]] = s["signup_date"]

    active_users = set()
    for a in activity:
        if a["user_id"] in signup_map:
            signup_date = datetime.strptime(signup_map[a["user_id"]], "%Y-%m-%d")
            activity_date = datetime.strptime(a["date"], "%Y-%m-%d")
            if activity_date >= signup_date + timedelta(days=7):
                active_users.add(a["user_id"])

    return len(active_users) / len(signup_map)


'''
Q10. Users who completed funnel in order

Context:
Given events and required steps, return users who completed all steps in order.
Events may be unsorted.

Expected behavior:
steps = ["view", "click", "purchase"]
User must do view before click before purchase.

Buggy code:
'''

def users_completed_funnel(events, steps):
    progress = {}
    completed = set()

    for e in events:
        user_id = e["user_id"]
        event = e["event"]

        if user_id not in progress:
            progress[user_id] = 0

        if event == steps[progress[user_id]]:
            progress[user_id] += 1

        if progress[user_id] == len(steps):
            completed.add(user_id)

    return completed


'''
Q11. Average latency by model

Context:
requests contains model and latency_ms.
Return average latency by model.
Ignore missing latency and latency_ms=None.
Include latency_ms=0.

Buggy code:
'''

def avg_latency_by_model(requests):
    sums = {}
    counts = {}

    for r in requests:
        model = r["model"]
        latency = r.get("latency_ms")

        if latency:
            sums[model] = sums.get(model, 0) + latency
            counts[model] = counts.get(model, 0) + 1

    return {m: sums[m] / counts[m] for m in sums}


'''
Q12. Median latency by model

Context:
Return median latency per model.
Do not mutate input lists.
Ignore missing or None latency.

Buggy code:
'''

def median_latency_by_model(requests):
    values = {}

    for r in requests:
        model = r["model"]
        latency = r["latency_ms"]
        values.setdefault(model, []).append(latency)

    result = {}
    for model, nums in values.items():
        nums.sort()
        n = len(nums)
        mid = n // 2
        if n % 2 == 1:
            result[model] = nums[mid]
        else:
            result[model] = nums[mid] + nums[mid - 1] / 2

    return result


'''
Q13. Revenue-weighted adoption rate by country

Context:
Each advertiser has account_id, country, and product_adopted.
Each spend row has account_id and spend.

Expected behavior:
For each country:
sum(spend for adopted accounts) / sum(spend for all accounts)

Buggy code:
'''

def weighted_adoption_by_country(advertisers, spend_rows):
    advertiser_map = {a["account_id"]: a for a in advertisers}
    result = {}

    for s in spend_rows:
        account_id = s["account_id"]
        country = advertiser_map[account_id]["country"]
        adopted = advertiser_map[account_id]["product_adopted"]

        if country not in result:
            result[country] = 0

        if adopted:
            result[country] += s["spend"]

    return result


'''
Q14. Sessionize events

Context:
Given events with user_id and ts in minutes.
A new session starts when the gap between consecutive events for the same user is greater than 30 minutes.

Expected behavior:
Return number of sessions per user.
Events may be unsorted.

Buggy code:
'''

def sessions_per_user(events):
    sessions = {}
    last_ts = {}

    for e in events:
        user_id = e["user_id"]
        ts = e["ts"]

        if user_id not in sessions:
            sessions[user_id] = 0

        if user_id not in last_ts or ts - last_ts[user_id] >= 30:
            sessions[user_id] += 1

        last_ts[user_id] = ts

    return sessions


'''
Q15. Users with 3 errors in a 10-minute window

Context:
Each event has user_id, ts, and status_code.
An error is status_code >= 500.

Expected behavior:
Return users who had at least 3 errors within any 10-minute inclusive window.
Events may be unsorted.

Buggy code:
'''

def users_with_3_errors_in_10_min(events):
    errors_by_user = {}

    for e in events:
        if e["status_code"] > 500:
            errors_by_user.setdefault(e["user_id"], []).append(e["ts"])

    result = set()
    for user_id, times in errors_by_user.items():
        for i in range(len(times)):
            if times[i + 2] - times[i] < 10:
                result.add(user_id)

    return result


'''
Q16. Match API requests and responses

Context:
Each log has request_id, type, and ts.
type is either "request" or "response".

Expected behavior:
Return a dictionary mapping request_id to latency = response_ts - request_ts.
Only include request_ids that have both request and response.
If duplicate requests or responses exist, use earliest request and earliest response after that request.

Buggy code:
'''

def request_latencies(logs):
    requests = {}
    responses = {}

    for log in logs:
        if log["type"] == "request":
            requests[log["request_id"]] = log["ts"]
        else:
            responses[log["request_id"]] = log["ts"]

    result = {}
    for request_id in requests:
        result[request_id] = responses[request_id] - requests[request_id]

    return result


'''
Q17. Reconstruct subscription state

Context:
Events have account_id, event, and ts.
event can be "start_trial", "subscribe", "cancel".
Return final state per account:
- "trial" if latest relevant event is start_trial
- "paid" if latest relevant event is subscribe
- "canceled" if latest relevant event is cancel

Expected behavior:
Use latest event by timestamp. Events may be unsorted.

Buggy code:
'''

def final_subscription_state(events):
    state = {}

    for e in events:
        account_id = e["account_id"]
        event = e["event"]

        if event == "start_trial":
            state[account_id] = "trial"
        elif event == "subscribe":
            state[account_id] = "paid"
        elif event == "cancel":
            state[account_id] = "canceled"

    return state


'''
Q18. Validate experiment weights

Context:
weights maps variant names to integer weights.

Expected behavior:
Return True only if:
- weights is a non-empty dict
- variant names are non-empty strings
- weights are non-negative integers
- bool values are rejected
- total weight is exactly 100

Buggy code:
'''

def validate_experiment_weights(weights):
    if not weights:
        return True

    total = 0
    for name, weight in weights.items():
        if not name:
            return False
        if not isinstance(weight, int):
            return False
        if weight < 0:
            return False
        total += weight

    return total <= 100


'''
Q19. Deterministic variant assignment

Context:
Assign user to variant using deterministic bucket:
bucket = sum(ord(c) for c in seed + "|" + str(user_id)) % 100

Expected behavior:
Return variant based on cumulative weights.
Use validate_experiment_weights.
Do not use random or built-in hash.

Buggy code:
'''

def assign_variant(user_id, seed, variants):
    if not validate_experiment_weights(variants):
        return None

    bucket = hash(str(user_id) + seed) % 100

    cumulative = 0
    for variant, weight in variants.items():
        cumulative += weight
        if bucket <= cumulative:
            return variant

    return None


'''
Q20. Compute conversion rate by variant

Context:
assignments contains user_id and variant.
events contains user_id and event.
Compute conversion rate by variant:
number of users with purchase / number of assigned users in variant.

Expected behavior:
- Denominator is assigned users by variant.
- Numerator is assigned users in that variant with at least one purchase.
- Deduplicate users.
- Ignore events from unassigned users.
- Return None for variants with zero assigned users.

Buggy code:
'''

def conversion_rate_by_variant(assignments, events):
    user_variant = {}
    for a in assignments:
        user_variant[a["user_id"]] = a["variant"]

    purchases = {}
    for e in events:
        if e["event"] == "purchase":
            variant = user_variant[e["user_id"]]
            purchases[variant] = purchases.get(variant, 0) + 1

    totals = {}
    for a in assignments:
        variant = a["variant"]
        totals[variant] = totals.get(variant, 0) + 1

    result = {}
    for variant in totals:
        result[variant] = purchases.get(variant, 0) / totals[variant]

    return result
    
'''
Q1 Answer

Bugs:
1. Uses list instead of set, so duplicate users are counted multiple times.
2. Directly accesses e["user_id"], causing KeyError for malformed records.
3. Counts None as a valid user.
4. Does not explicitly handle empty input, though it happens to return 0.
5. Does not distinguish valid from invalid records.

Correct logic:
Use a set, skip missing or None user_id.
'''

def count_active_users_fixed(events):
    users = set()
    for e in events:
        user_id = e.get("user_id")
        if user_id is not None:
            users.add(user_id)
    return len(users)


'''
Q2 Answer

Bugs:
1. First occurrence initializes count to 0 instead of 1.
2. Else branch increments only from second occurrence onward.
3. Directly accesses e["event"], causing KeyError.
4. Does not ignore missing event records.
5. Empty input is okay but malformed input is not.

Correct logic:
'''

def count_events_by_type_fixed(events):
    counts = {}
    for e in events:
        event = e.get("event")
        if event is None:
            continue
        counts[event] = counts.get(event, 0) + 1
    return counts


'''
Q3 Answer

Bugs:
1. Direct access to user_id can raise KeyError.
2. Direct access to ts can raise KeyError.
3. Uses <=, so later input record replaces earlier record on tied timestamp.
4. Does not skip malformed records.
5. Assumes result[user_id] always has ts.

Correct logic:
Use <, not <=, for timestamp comparison.
'''

def first_event_per_user_unsorted_fixed(events):
    result = {}
    for e in events:
        if "user_id" not in e or "ts" not in e:
            continue
        user_id = e["user_id"]
        if user_id not in result or e["ts"] < result[user_id]["ts"]:
            result[user_id] = e
    return result


'''
Q4 Answer

Bugs:
1. Sorts ascending by count, but should sort descending.
2. Does not break ties by smaller user_id correctly.
3. Does not handle k <= 0.
4. Directly accesses user_id, causing KeyError.
5. Missing user_id records are not ignored.

Correct logic:
Sort by (-count, user_id).
'''

def top_k_users_by_event_count_fixed(events, k):
    if k <= 0:
        return []

    counts = {}
    for e in events:
        if "user_id" not in e:
            continue
        user_id = e["user_id"]
        counts[user_id] = counts.get(user_id, 0) + 1

    ranked = sorted(counts.keys(), key=lambda u: (-counts[u], u))
    return ranked[:k]


'''
Q5 Answer

Bugs:
1. user_map indexing on missing event user causes KeyError.
2. Mutates original event dictionary by setting e["country"].
3. Does not ignore events missing user_id.
4. Assumes profile has country.
5. Inner join should skip unmatched users, not error.

Correct logic:
Create a new row and only include matched users.
'''

def inner_join_users_events_fixed(users, events):
    user_map = {}
    for u in users:
        if "user_id" in u:
            user_map[u["user_id"]] = u

    output = []
    for e in events:
        user_id = e.get("user_id")
        if user_id not in user_map:
            continue
        profile = user_map[user_id]
        row = dict(e)
        row["country"] = profile.get("country")
        output.append(row)

    return output


'''
Q6 Answer

Bugs:
1. profile may be None, so profile["country"] errors.
2. Direct e["user_id"] can fail if event is missing user_id.
3. row = e mutates original event dictionary.
4. Dict comprehension may fail if users missing user_id.
5. Missing profiles should produce country=None.

Correct logic:
'''

def left_join_users_events_fixed(users, events):
    user_map = {}
    for u in users:
        if "user_id" in u:
            user_map[u["user_id"]] = u

    output = []
    for e in events:
        user_id = e.get("user_id")
        profile = user_map.get(user_id)
        row = dict(e)
        row["country"] = profile.get("country") if profile else None
        output.append(row)

    return output


'''
Q7 Answer

Bugs:
1. Direct access to account_id can raise KeyError.
2. Direct access to ds can raise KeyError.
3. On tied ds, should keep later input record but code keeps earlier.
4. Does not skip malformed records.
5. Does not validate required fields.

Correct logic:
Use >= for tie replacement, because later input should win.
'''

def latest_record_per_account_fixed(records):
    latest = {}
    for r in records:
        if "account_id" not in r or "ds" not in r:
            continue
        account_id = r["account_id"]
        if account_id not in latest or r["ds"] >= latest[account_id]["ds"]:
            latest[account_id] = r
    return latest


'''
Q8 Answer

Bugs:
1. Denominator incorrectly uses len(events), not number of signup users.
2. Does not require purchase to happen after signup.
3. Does not use first signup timestamp.
4. Direct field access can raise KeyError.
5. Division by zero if no signups.
6. Duplicate purchases should count user once.

Correct logic:
Track first signup per user and whether user purchased after that.
'''

def signup_to_purchase_conversion_fixed(events):
    first_signup = {}

    for e in events:
        if "user_id" not in e or "event" not in e or "ts" not in e:
            continue
        if e["event"] == "signup":
            user_id = e["user_id"]
            if user_id not in first_signup or e["ts"] < first_signup[user_id]:
                first_signup[user_id] = e["ts"]

    if not first_signup:
        return None

    converted = set()
    for e in events:
        if "user_id" not in e or "event" not in e or "ts" not in e:
            continue
        user_id = e["user_id"]
        if e["event"] == "purchase" and user_id in first_signup and e["ts"] > first_signup[user_id]:
            converted.add(user_id)

    return len(converted) / len(first_signup)


'''
Q9 Answer

Bugs:
1. Duplicate signup uses latest signup, but requirement says earliest.
2. Uses activity_date >= signup_date + 7 days, but requirement is exactly day 7.
3. Direct field access can raise KeyError.
4. Division by zero if no valid signups.
5. Does not skip malformed dates.
6. Activity missing fields can crash.

Correct logic:
'''

from datetime import datetime, timedelta

def day_7_retention_fixed(signups, activity):
    signup_map = {}

    for s in signups:
        if "user_id" not in s or "signup_date" not in s:
            continue
        try:
            d = datetime.strptime(s["signup_date"], "%Y-%m-%d").date()
        except ValueError:
            continue

        user_id = s["user_id"]
        if user_id not in signup_map or d < signup_map[user_id]:
            signup_map[user_id] = d

    if not signup_map:
        return None

    retained = set()

    for a in activity:
        if "user_id" not in a or "date" not in a:
            continue
        user_id = a["user_id"]
        if user_id not in signup_map:
            continue
        try:
            activity_date = datetime.strptime(a["date"], "%Y-%m-%d").date()
        except ValueError:
            continue

        if activity_date == signup_map[user_id] + timedelta(days=7):
            retained.add(user_id)

    return len(retained) / len(signup_map)


'''
Q10 Answer

Bugs:
1. Events may be unsorted, but code processes input order.
2. If steps is empty, steps[0] errors.
3. Direct field access can raise KeyError.
4. After user completes funnel, later events can cause index out of range.
5. Does not ignore malformed records.
6. Multiple events at same ts are not explicitly handled.

Correct logic:
Sort valid events by user_id, ts, then input order.
'''

def users_completed_funnel_fixed(events, steps):
    if not steps:
        return set()

    valid = []
    for idx, e in enumerate(events):
        if "user_id" in e and "event" in e and "ts" in e:
            valid.append((e["user_id"], e["ts"], idx, e["event"]))

    valid.sort(key=lambda x: (x[0], x[1], x[2]))

    progress = {}
    completed = set()

    for user_id, ts, idx, event in valid:
        if user_id in completed:
            continue

        step_idx = progress.get(user_id, 0)
        if event == steps[step_idx]:
            step_idx += 1
            progress[user_id] = step_idx
            if step_idx == len(steps):
                completed.add(user_id)

    return completed


'''
Q11 Answer

Bugs:
1. Direct r["model"] can raise KeyError.
2. if latency incorrectly excludes latency_ms = 0.
3. Does not ignore latency_ms=None safely.
4. Missing latency should be skipped.
5. May include model with bad latency if not checked.

Correct logic:
Check latency is not None.
'''

def avg_latency_by_model_fixed(requests):
    sums = {}
    counts = {}

    for r in requests:
        if "model" not in r or "latency_ms" not in r:
            continue
        latency = r["latency_ms"]
        if latency is None:
            continue

        model = r["model"]
        sums[model] = sums.get(model, 0) + latency
        counts[model] = counts.get(model, 0) + 1

    return {m: sums[m] / counts[m] for m in sums}


'''
Q12 Answer

Bugs:
1. Direct access to model can raise KeyError.
2. Direct access to latency_ms can raise KeyError.
3. Does not skip None latency.
4. Even median formula is wrong due to operator precedence.
   nums[mid] + nums[mid - 1] / 2 should be (nums[mid] + nums[mid - 1]) / 2.
5. nums.sort() mutates the stored list. This does not mutate input records, but sorted(nums) is safer.
6. Empty groups should not happen after filtering, but malformed data can create issues.

Correct logic:
'''

def median_latency_by_model_fixed(requests):
    values = {}

    for r in requests:
        if "model" not in r or "latency_ms" not in r:
            continue
        latency = r["latency_ms"]
        if latency is None:
            continue
        values.setdefault(r["model"], []).append(latency)

    result = {}
    for model, nums in values.items():
        sorted_nums = sorted(nums)
        n = len(sorted_nums)
        mid = n // 2
        if n % 2 == 1:
            result[model] = sorted_nums[mid]
        else:
            result[model] = (sorted_nums[mid - 1] + sorted_nums[mid]) / 2

    return result


'''
Q13 Answer

Bugs:
1. Returns adopted spend, not adoption rate.
2. Does not track total spend denominator.
3. Crashes if spend row account_id not in advertisers.
4. Direct field access can raise KeyError.
5. Does not handle country with zero spend.
6. Does not handle missing product_adopted/spend.

Correct logic:
Track adopted_spend and total_spend by country.
'''

def weighted_adoption_by_country_fixed(advertisers, spend_rows):
    advertiser_map = {}
    for a in advertisers:
        if "account_id" in a:
            advertiser_map[a["account_id"]] = a

    adopted_spend = {}
    total_spend = {}

    for s in spend_rows:
        if "account_id" not in s or "spend" not in s:
            continue
        account_id = s["account_id"]
        if account_id not in advertiser_map:
            continue

        advertiser = advertiser_map[account_id]
        country = advertiser.get("country")
        if country is None:
            continue

        spend = s["spend"]
        if spend is None:
            continue

        total_spend[country] = total_spend.get(country, 0) + spend
        if advertiser.get("product_adopted") == 1:
            adopted_spend[country] = adopted_spend.get(country, 0) + spend

    result = {}
    for country, total in total_spend.items():
        result[country] = None if total == 0 else adopted_spend.get(country, 0) / total

    return result


'''
Q14 Answer

Bugs:
1. Events may be unsorted, so gap logic is wrong.
2. New session condition should be gap > 30, not >= 30.
3. Direct access can raise KeyError.
4. Does not skip malformed records.
5. Negative gaps can happen if unsorted input is not sorted.
6. First event should create one session.

Correct logic:
Sort valid events by user_id and ts.
'''

def sessions_per_user_fixed(events):
    valid = []
    for e in events:
        if "user_id" in e and "ts" in e:
            valid.append((e["user_id"], e["ts"]))

    valid.sort(key=lambda x: (x[0], x[1]))

    sessions = {}
    last_ts = {}

    for user_id, ts in valid:
        if user_id not in sessions:
            sessions[user_id] = 1
        elif ts - last_ts[user_id] > 30:
            sessions[user_id] += 1

        last_ts[user_id] = ts

    return sessions


'''
Q15 Answer

Bugs:
1. Error condition should be >= 500, not > 500.
2. Direct field access can raise KeyError.
3. Events may be unsorted, but times are not sorted.
4. Loop accesses times[i + 2] without checking bounds.
5. Window is inclusive 10 minutes, but code uses < 10 instead of <= 10.
6. Does not skip malformed records.

Correct logic:
Sort error times per user and use sliding window or indexed check.
'''

def users_with_3_errors_in_10_min_fixed(events):
    errors_by_user = {}

    for e in events:
        if "user_id" not in e or "ts" not in e or "status_code" not in e:
            continue
        if e["status_code"] >= 500:
            errors_by_user.setdefault(e["user_id"], []).append(e["ts"])

    result = set()

    for user_id, times in errors_by_user.items():
        times = sorted(times)
        for i in range(len(times) - 2):
            if times[i + 2] - times[i] <= 10:
                result.add(user_id)
                break

    return result


'''
Q16 Answer

Bugs:
1. Duplicate requests overwrite earlier requests; should use earliest request.
2. Duplicate responses overwrite earlier responses; need earliest response after request.
3. Crashes if response missing for a request.
4. Could produce negative latency if response before request.
5. Direct field access can raise KeyError.
6. Does not skip unknown log types.

Correct logic:
Group request and response times by request_id.
'''

def request_latencies_fixed(logs):
    req_times = {}
    resp_times = {}

    for log in logs:
        if "request_id" not in log or "type" not in log or "ts" not in log:
            continue
        request_id = log["request_id"]
        if log["type"] == "request":
            req_times.setdefault(request_id, []).append(log["ts"])
        elif log["type"] == "response":
            resp_times.setdefault(request_id, []).append(log["ts"])

    result = {}

    for request_id, requests in req_times.items():
        if request_id not in resp_times:
            continue

        requests = sorted(requests)
        responses = sorted(resp_times[request_id])

        request_ts = requests[0]
        response_ts = None

        for rts in responses:
            if rts >= request_ts:
                response_ts = rts
                break

        if response_ts is not None:
            result[request_id] = response_ts - request_ts

    return result


'''
Q17 Answer

Bugs:
1. Events may be unsorted, but code uses input order.
2. Does not compare timestamps.
3. Direct field access can raise KeyError.
4. Unknown events should be ignored.
5. Tied timestamp behavior is unspecified; reasonable choice is later input wins.
6. Does not store latest timestamp.

Correct logic:
Track latest timestamp and state per account.
'''

def final_subscription_state_fixed(events):
    latest = {}
    mapping = {
        "start_trial": "trial",
        "subscribe": "paid",
        "cancel": "canceled",
    }

    for idx, e in enumerate(events):
        if "account_id" not in e or "event" not in e or "ts" not in e:
            continue
        event = e["event"]
        if event not in mapping:
            continue

        account_id = e["account_id"]
        key = (e["ts"], idx)

        if account_id not in latest or key >= latest[account_id][0]:
            latest[account_id] = (key, mapping[event])

    return {account_id: state for account_id, (key, state) in latest.items()}


'''
Q18 Answer

Bugs:
1. Empty weights should return False, not True.
2. Does not verify weights is a dict.
3. Does not verify variant name is a string.
4. Empty string check works, but non-string truthy name could pass.
5. bool is subclass of int, so True passes incorrectly.
6. Allows total < 100 because it uses <= 100, but requirement is exactly 100.

Correct logic:
'''

def validate_experiment_weights_fixed(weights):
    if not isinstance(weights, dict) or not weights:
        return False

    total = 0

    for name, weight in weights.items():
        if not isinstance(name, str) or name == "":
            return False
        if isinstance(weight, bool) or not isinstance(weight, int):
            return False
        if weight < 0:
            return False
        total += weight

    return total == 100


'''
Q19 Answer

Bugs:
1. Uses built-in hash(), which is not stable across processes by default.
2. Bucket formula does not match requirement.
3. Boundary condition wrong: if cumulative is 50, bucket 50 should go to next variant.
   Condition should be bucket < cumulative.
4. Does not validate user_id is not None.
5. Does not validate seed is a non-empty string.
6. Calls validate_experiment_weights, but depending on implementation may be buggy.

Correct logic:
'''

def assign_variant_fixed(user_id, seed, variants):
    if user_id is None:
        return None
    if not isinstance(seed, str) or seed == "":
        return None
    if not validate_experiment_weights_fixed(variants):
        return None

    bucket = sum(ord(c) for c in seed + "|" + str(user_id)) % 100

    cumulative = 0
    for variant, weight in variants.items():
        cumulative += weight
        if bucket < cumulative:
            return variant

    return None


'''
Q20 Answer

Bugs:
1. Duplicate assignments can double count denominators.
2. Duplicate purchase events can double count numerators.
3. Events from unassigned users cause KeyError.
4. Direct field access can raise KeyError.
5. If user appears in assignments multiple times with conflicting variants, behavior is undefined.
6. Does not return variants with zero assigned users unless present in totals.
7. Does not dedupe assigned users by variant.

Correct logic:
One simple policy: use first assignment per user and dedupe users.
'''

def conversion_rate_by_variant_fixed(assignments, events):
    user_variant = {}
    variants = set()

    for a in assignments:
        if "user_id" not in a or "variant" not in a:
            continue
        user_id = a["user_id"]
        variant = a["variant"]
        variants.add(variant)

        if user_id not in user_variant:
            user_variant[user_id] = variant

    assigned_by_variant = {}
    for user_id, variant in user_variant.items():
        assigned_by_variant.setdefault(variant, set()).add(user_id)

    purchasers_by_variant = {}
    for e in events:
        if "user_id" not in e or "event" not in e:
            continue
        if e["event"] != "purchase":
            continue

        user_id = e["user_id"]
        if user_id not in user_variant:
            continue

        variant = user_variant[user_id]
        purchasers_by_variant.setdefault(variant, set()).add(user_id)

    result = {}
    for variant in variants:
        denom = len(assigned_by_variant.get(variant, set()))
        if denom == 0:
            result[variant] = None
        else:
            result[variant] = len(purchasers_by_variant.get(variant, set())) / denom

    return result