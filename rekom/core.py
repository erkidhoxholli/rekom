import redis
import math

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)


### redis commands: https://redis.io/commands/zunionstore
def rate(item, user, score):
    redis_client.execute_command('ZADD', f'user:{user}:items', score, item)
    redis_client.execute_command('ZADD', f'item:{item}:scores', score, user)
    redis_client.execute_command('SADD', 'users', user)

def clear_db():
    redis_client.execute_command('FLUSHALL')

def get_user_suggestions(user, max):
    return redis_client.execute_command('ZREVRANGE', f'user:{user}:suggestions', 0, max, 'WITHSCORES')


def get_suggest_candidates(user, max):
    similar_users = redis_client.execute_command('ZRANGE', f'user:{user}:similars', 0, max)
    max = len(similar_users)
    args = []
    args.append('ztmp')
    args.append(max + 1)
    args.append(f'user:{user}:items')

    weights = []
    weights.append('WEIGHTS')
    weights.append(-1)
    # print(similar_users)
    for simuser in similar_users:
        args.append(f'user:{simuser}:items')
        weights.append(1)

    args = args + weights
    args.append('AGGREGATE')
    args.append('MIN')
    # print(*args)
    redis_client.execute_command('ZUNIONSTORE', *args)
    candidates = redis_client.execute_command("ZRANGEBYSCORE", "ztmp", 0, "inf")
    ##TODO: candidates are not returned properly when user=1
    ##  ZUNIONSTORE ztmp 3 user:1:items user:2:items user:3:items WEIGHTS -1 1 1 AGGREGATE MIN
    ##  ZRANGEBYSCORE ztmp  0 "inf"   ->> !!returns empty

    redis_client.execute_command('DEL', 'ztmp')
    return candidates


def batch_update_similar_items(max):
    users = redis_client.execute_command("SMEMBERS", "users")
    for user in users:
        candidates = get_similarity_candidates(user, max)
        # print(candidates)

        args = []
        args.append(f'user:{user}:similars')
        for candidate in candidates:
            if candidate != user:
                score = calculate_similarity(user, candidate)
                args.append(score)
                args.append(candidate)

        # print(*args)
        redis_client.execute_command('ZADD', *args)


def calculate_item_probability(user, item):
    redis_client.execute_command("ZINTERSTORE", "ztmp", 2, f'user:{user}:similars', f'item:{item}:scores', "WEIGHTS", 0,
                                 1)  ## https://redis.io/commands/zinterstore

    scores = redis_client.execute_command('ZRANGE', 'ztmp', 0, -1, 'WITHSCORES')
    # print(scores)
    redis_client.execute_command('DEL', 'ztmp')
    if len(scores) == 0: return 0

    score = 0
    for i in range(1, len(scores), 2):
        score += float(scores[i])  ## TODO: check this because scores are not proper...

    score /= float(len(scores) / 2.0)
    # print(score)
    return float(score)


def update_suggested_items(user, max):
    items = get_suggest_candidates(user, max)

    if len(items) == 0: return

    if max > len(items): max = len(items)

    args = []
    args.append(f'user:{user}:suggestions')
    for item in items:
        probability = calculate_item_probability(user, item)
        # print(f'probability for user {user} and item {item} is {probability}')
        args.append(probability)
        args.append(item)
    #print(*args)
    redis_client.execute_command('ZADD', *args)


def get_user_items(user, max):
    return redis_client.execute_command('ZREVRANGE', f'user:{user}:items', 0, max)


def get_item_scores(item, max):
    return redis_client.execute_command('ZREVRANGE', f'user:{item}:scores', 0, max)


## checked (is fine)
def get_similarity_candidates(user, max):
    items = get_user_items(user, max)
    if max > len(items): max = len(items)

    args = []
    args.append('ztmp')
    args.append(max)
    for i in range(0, max):
        args.append(f'item:{items[i]}:scores')
    redis_client.execute_command('ZUNIONSTORE', *args)
    users = redis_client.execute_command('ZRANGE', 'ztmp', 0, -1)
    redis_client.execute_command('DEL', 'ztmp')

    return users


## TODO: not working properly
## NOTE: the higher the similarity the better (0:1)
## http://www.cs.carleton.edu/cs_comps/0607/recommend/recommender/itembased.html
def calculate_similarity(user, simuser):
    if user == simuser:
        return 1.0

    redis_client.execute_command("ZINTERSTORE", "ztmp", 2, f'user:{user}:items', f'user:{simuser}:items', "WEIGHTS", 1,
                                 -1)  ## https://redis.io/commands/zinterstore
    user_diffs = redis_client.execute_command('ZRANGE', 'ztmp', 0, -1, 'WITHSCORES')
    redis_client.execute_command('DEL', 'ztmp')
    # print(user_diffs)
    if len(user_diffs) == 0:
        return 0

    score = 0.0
    # print(f'user_diffs: {user_diffs}')
    ## RMS Error
    ## https://statweb.stanford.edu/~susan/courses/s60/split/node60.html

    ## WITHSCORE returns the score every each second element including the element itself
    ## for ex if user_diffs = ['2', '0'] then 2 is the similar item between 2 users and the score is 0
    for i in range(1, len(user_diffs), 2):
        #         print('inside')
        #         print(user_diffs[i])
        diff_val = float(user_diffs[i])
        # print(f'diff_val: {diff_val}')
        score += math.pow(diff_val, 2)
    score /= float(len(user_diffs) / 2)
    score = math.sqrt(score)
    return score
