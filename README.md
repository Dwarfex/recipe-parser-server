# Recipe Parser Server
A simple application that proxies the [recipe-scrapers](https://github.com/hhursev/recipe-scrapers) functionality and provides it as a simple API.


## GET Route "/"
Returns a list of Domains where the library works

## GET Route "/example"
Returns a JSON Response example

## POST Route "/parse"
Expects a JSON HTML Body and URL. It will return the parsed JSON like the /example route.
Example:

``{ url: "https://recipe-url.example", content:"<html><body>....."``

## GET Route "/pull?url=abc"
Pulls the given URL abc and returns an json if available
