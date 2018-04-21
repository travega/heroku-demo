from flask import Flask, request, redirect, url_for, render_template
import os, logging, psycopg2 
from datetime import datetime 
import ujson
import uuid
from flask_bootstrap import Bootstrap
from libs import postgres , utils , logs, rediscache
from appsrc import app, logger



RENDER_INDEX_BOOTSTRAP="index_bootstrap.html"
RENDER_ROOT="index_root.html"


@app.route('/', methods=['GET'])
def root():
    try:
        if (postgres.__checkHerokuLogsTable()):
            postgres.__saveLogEntry(request)
        logger.debug(utils.get_debug_all(request))

        key = {'url' : request.url}
        tmp_dict = None
        #data_dict = None
        tmp_dict = rediscache.__getCache(key)
        if ((tmp_dict == None) or (tmp_dict == '')):
            logger.info("Data not found in cache")


            data = render_template(RENDER_ROOT)

            rediscache.__setCache(key, data, 60)
        else:
            logger.info("Data found in redis, using it directly")
            data = tmp_dict
            

        return data, 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return "An error occured, check logDNA for more information", 200


@app.route('/error', methods=['GET'])
def error():
    if (postgres.__checkHerokuLogsTable()):
        postgres.__saveLogEntry(request)


    logger.debug(utils.get_debug_all(request))
    logger.error("Generating Error")
    error_code = 500
    if ('error_code' in request.args):
        error_code = int(request.args['error_code'])
    return "Error !!!!!!",error_code

