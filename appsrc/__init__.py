from flask import Flask, request, redirect, url_for, render_template
import os, logging, psycopg2 
from datetime import datetime 
import ujson
import uuid
from flask_bootstrap import Bootstrap
from libs import postgres , utils , logs, rediscache


STATIC_URL_PATH = "../templates"
# environment variable
WEBPORT = os.getenv('PORT', '5000')



app = Flask(__name__, template_folder=STATIC_URL_PATH) 
Bootstrap(app)

logs.logger_init(loggername='app',
            filename="log.log",
            debugvalue="DEBUG",
            flaskapp=app)

logger = logs.logger 

from appsrc import root, votes, tables


"""
if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=int(WEBPORT))
"""



