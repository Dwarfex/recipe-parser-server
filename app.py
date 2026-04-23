from flask import Flask
from urllib.request import urlopen
from recipe_scrapers import scrape_html
import requests
from recipe_scrapers import SCRAPERS
from flask import request
from flask import jsonify
from waitress import serve
import logging
from urllib.parse import urlparse

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


def is_valid_uri(uri):
    """Check if the provided string is a valid URI."""
    try:
        result = urlparse(uri)
        # Check that the URI has a scheme (http, https, etc.) and a netloc (domain)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


@app.route("/pull", methods=['GET'])
def pull():
    url = request.args.get('url')
    
    # Validate that URL is provided
    if not url:
        logger.warning("Pull request received without a URL")
        return {'error': 'Missing required parameter: url'}, 400
    
    # Validate that URL is a valid URI
    if not is_valid_uri(url):
        logger.warning(f"Pull request received with invalid URL: {url}")
        return {'error': 'Invalid URL format'}, 400
    
    logger.info(f"Pulling recipe from URL: {url}")
    
    try:
        # retrieve the recipe webpage HTML
        html = urlopen(url).read().decode("utf-8")
        myobj = {'url': url, 'contents': html}

        x = requests.post('http://localhost:5127/parse', json = myobj)
        data = x.text
        response = app.response_class(
            response=data,
            status=200,
            mimetype='application/json'
        )
        return response
    except Exception as exception:
        logger.exception(f"Error pulling recipe from {url}")
        return {'error': 'Failed to pull recipe due to an internal error.'}, 500

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
