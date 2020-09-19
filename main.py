from fastapi import FastAPI

from rekom.engine import rate_item, get_probability, suggest, update
from settings.config import setup_configuration
from settings.i18n import get_translations

config = setup_configuration('dev')  ## get this from os env variable
env_name = config['APP']['ENVIRONMENT']

print(f'Running on {env_name} environment!')

_ = get_translations('pl')

app = FastAPI(debug=config['APP']['DEBUG'],
              title=config['APP']['NAME'],
              version=config['APP']['VERSION'],
              docs_url=config['DOCS']['SWAGGER'],
              redoc_url=config['DOCS']['REDOC'])


@app.get("/")
async def home():
    return {"message": _("Welcome to home")}


@app.get("/rate")
async def rate_item_route(user: int, item: int, score: int):
    rate_item(user, item, score)

    message = _('User %(user)s rated  item %(item)s with score %(score)s.') % {'user': user, 'item': item,
                                                                               'score': score}

    return {"message": message}


@app.get("/get-probability")
async def get_probability_route(user: int, item: int):
    probability = get_probability(user, item)

    message = _('User %(user)s has the probability %(probability)s to buy item %(item)s.') % {'user': user,
                                                                                              'probability': probability,
                                                                                              'item': item}

    return {"message": message}


@app.get("/recommend")
async def recommend_route(user: int, limit: int = 100):
    suggestions = suggest(user, limit)

    message = _('Got the suggestions for user with id %(user)s ') % {'user': user}

    return {
        "message": message,
        "data": suggestions
    }


@app.get("/batch-update")
async def recommend_route(limit: int = 100):
    update(limit)

    return {"message": _('Updated the results!')}
