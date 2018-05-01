from flask import Flask, request, redirect, url_for, render_template
import os, logging, psycopg2 
from datetime import datetime 
import ujson
import uuid
from flask_bootstrap import Bootstrap
from libs import postgres , utils , logs, rediscache
from appsrc import app, logger


RENDER_ROOT_PHOTO="photo_main.html"
PATH_TO_TEST_IMAGES_DIR = './images'

@app.route('/photos_post', methods=['POST'])
def image():
    try:
        logger.debug(utils.get_debug_all(request))

        import time 
        print(request.files)
        i = request.files['fileToUpload']  # get the image
        f = ('%s.jpeg' % time.strftime("%Y%m%d-%H%M%S"))
        i.save('%s/%s' % (PATH_TO_TEST_IMAGES_DIR, f))

        return "Ok" , 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return "An error occured, check logDNA for more information", 200



@app.route('/photos', methods=['GET'])
def root_photo():
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


            data = render_template(RENDER_ROOT_PHOTO, imageid =  uuid.uuid4().__str__())

            rediscache.__setCache(key, data, 60)
        else:
            logger.info("Data found in redis, using it directly")
            data = tmp_dict
            

        return data, 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return "An error occured, check logDNA for more information", 200

