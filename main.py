from fastapi import FastAPI

from rekom.engine import rate_item, get_probability, suggest
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
    return {"message": _("User %d rated item %d with score %d") % user % item % score}


@app.get("/get-probability")
async def get_probability_route(user: int, item: int):
    probability = get_probability(user, item)
    return {"message": _("User %d has the probability %d to buy item %d.") % user % probability % item}


@app.get("/recommend")
async def recommend_route(user: int, limit: int = 100):
    suggestions = suggest(user, limit)
    return {
        "message": _("Got the suggestions for user %d.") % user,
        "data": suggestions
    }
