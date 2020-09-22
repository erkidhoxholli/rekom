from .core import *

def suggest(user, max):
    update_suggested_items(user, max)

    suggestions_with_scores = get_user_suggestions(user, max)
    # print(f'####### suggestions_with_scores for user {user}: {suggestions_with_scores}')
    clean_suggestions = []
    for i in range(0, len(suggestions_with_scores), 2):
        # print(f'clean_suggestions: {suggestions_with_scores[i]}')
        clean_suggestions.append({
            'item': suggestions_with_scores[i],
            'score': suggestions_with_scores[i + 1]
        })

    return clean_suggestions
    #print(f'####### suggestions for user {user}: {clean_suggestions}')


def update(max):
    batch_update_similar_items(max)


def get_probability(user, item):
    score = calculate_item_probability(user, item)
    return score


def rate_item(user, item, score):
    rate(item, user, score)