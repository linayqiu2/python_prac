'''
Q1.
You are given the following simplified Python snippet used to assign users and trigger a 1‑month free trial:

""" import random, datetime, requests

def maybe_start_trial(user_id): 
    if random.random() < 0.5: 
        variant = 'trial' 
    else: 
        variant = 'control' 
    now = datetime.datetime.now() 
    exposed_at = now 
    log_exposure(user_id, exposed_at, variant) 
    if variant == 'trial': 
        r = requests.post('https://billing/start_trial', json={'user_id': user_id}) if r.status_code == 200: log_trial(user_id, now) """

Identify at least 8 distinct correctness or reliability issues that could 
corrupt the experiment or data (think assignment stickiness, bias, timezones, 
idempotency, retries, race conditions, privacy, and observability). For each, 
explain the failure mode and its impact on metrics. Then propose concrete fixes 
(e.g., user‑hash bucketing with stable salts, UTC timestamps, exactly‑once exposure
 logging, outbox/queue, idempotency keys, transactional writes, circuit breakers, 
 exponential backoff, and eligibility checks). Finally, sketch a hardened version 
 (high‑level or pseudocode) that is production‑ready and experiment‑safe.
'''

'''
Q2 https://prachub.com/coding-questions/identify-bugs-in-python-script-for-user-assignment
'''

'''
Q3 https://prachub.com/interview-questions/debug-and-fix-a-pytorch-transformer-training-loop
'''

