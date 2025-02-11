from flask import Flask
from urllib.request import urlopen
from recipe_scrapers import scrape_html
import requests
from recipe_scrapers import SCRAPERS
from flask import request
from flask import jsonify
from waitress import serve
app = Flask(__name__)


@app.route("/", methods=['GET'])
def info():
    data =  list(SCRAPERS.keys())
    response = app.response_class(
        response=data,
        status=200,
        mimetype='application/json'
    )
    return data


@app.route("/parse", methods=['POST'])
def parse():
    json = request.get_json(force=True)
    html = json.get("contents")
    url = json.get("url")
    try:
        scraper = scrape_html(html, org_url=url)
        return scraper.to_json()
    except Exception as exception:
        return {'error': exception.message}


@app.route("/pull", methods=['GET'])
def pull():
    url = request.args.get('url')
    baseurl = request.base_url.removesuffix('/pull')

    # retrieve the recipe webpage HTML
    html = urlopen(url).read().decode("utf-8")
    myobj = {'url': url, 'contents': html}

    x = requests.post(baseurl + '/parse', json = myobj)
    data = x.text
    response = app.response_class(
        response=data,
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/example")
def example():
    baseurl = request.base_url.removesuffix('/example')

    url = "https://www.allrecipes.com/recipe/158968/spinach-and-feta-turkey-burgers/"
    # retrieve the recipe webpage HTML
    html = urlopen(url).read().decode("utf-8")
    myobj = {'url': url, 'contents': html}

    x = requests.post(baseurl + '/parse', json = myobj)
    data = x.text
    response = app.response_class(
        response=data,
        status=200,
        mimetype='application/json'
    )
    return response

if __name__ == "__main__":

    serve(app, host="0.0.0.0", port=5127)