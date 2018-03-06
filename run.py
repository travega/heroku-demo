from flask import Flask, request, redirect, url_for, render_template
import os, logging, psycopg2 
from datetime import datetime 
from sqlalchemy import create_engine
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import ujson
import redis 

RENDER_INDEX="index.html"
RENDER_TABLE_DATA="table_data.html"
STATIC_URL_PATH = "static/"

# log activation
def logger_init(loggername='app', filename='', debugvalue='debug', flaskapp=None):
    global logger

    from logging.handlers import TimedRotatingFileHandler

    logger = logging.getLogger(loggername)

    # création d'un formateur qui va ajouter le temps, le niveau
    # de chaque message quand on écrira un message dans le log
    format_string = "{'%(asctime)s','%(levelname)s',%(process)s,%(filename)s:%(lineno)s-%(funcName)s:-->%(message)s}"
    log_formatter = logging.Formatter(format_string, datefmt='%Y-%m-%d %H:%M:%S')

    numeric_level = getattr(logging, debugvalue.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: {}' % debugvalue)

    logger.setLevel(numeric_level)
    if (flaskapp != None):
        flaskapp.logger.setLevel(numeric_level)

    file_handler = TimedRotatingFileHandler(filename, when="midnight", backupCount=10)
    # on lui met le niveau sur DEBUG, on lui dit qu'il doit utiliser le formateur
    # créé précédement et on ajoute ce handler au logger
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    if (flaskapp != None):
        flaskapp.logger.addHandler(file_handler)
    # now stdout
    steam_handler = logging.StreamHandler()
    steam_handler.setLevel(logging.DEBUG)
    steam_handler.setFormatter(log_formatter)
    logger.addHandler(steam_handler)
    if (flaskapp != None):
        flaskapp.logger.addHandler(steam_handler)
        # and UDP

# environment variable
PORT = os.getenv('PORT', '5000')
REDIS_URL = os.getenv('REDIS_URL','')
REDIS_CONN = None 
DATABASE_URL = os.getenv('DATABASE_URL','')
MANUAL_ENGINE_POSTGRES = None


app = Flask(__name__) 

logger_init(loggername='app',
            filename="log.log",
            debugvalue="DEBUG",
            flaskapp=app)

if (DATABASE_URL != ''):
    Base = declarative_base()
    MANUAL_ENGINE_POSTGRES = create_engine(DATABASE_URL, pool_size=30, max_overflow=0)
    Base.metadata.bind = MANUAL_ENGINE_POSTGRES
    dbSession_postgres = sessionmaker(bind=MANUAL_ENGINE_POSTGRES)
    session_postgres = dbSession_postgres()
    logger.debug("{} - Initialization done Postgresql ".format(datetime.now()))
if (REDIS_URL != ''):
    REDIS_CONN = redis.from_url(REDIS_URL)
    REDIS_CONN.set('key','value')
    REDIS_CONN.expire('key', 300) # 5 minutes


def __resultToDict(result):
    from collections import namedtuple

    arrayData =  []
    column_names = [desc[0] for desc in result.cursor.description]

    for entry in result:
        logger.debug(entry)
        resDic = {}
        for column in column_names:
            resDic[column] = entry[column]
        arrayData.append(resDic)
    return {'data' : arrayData, 'columns': column_names}

def __getCache(key):
    if (REDIS_CONN != None):
        logger.debug('Reading in Redis')
        return REDIS_CONN.get(key)
    return None 

def __setCache(key, data, ttl):
    if (REDIS_CONN != None):
        logger.debug('Storing in Redis')
        REDIS_CONN.set(key, data)
        REDIS_CONN.expire(key, ttl)

def __getObjects(tableName):
    if (MANUAL_ENGINE_POSTGRES != None):
        concat = 'Salesforce.' + tableName
        result = MANUAL_ENGINE_POSTGRES.execute("select * from {}".format(concat))
        return __resultToDict(result)
        
    return {'data' : [], "columns": []}

def __getTables():
    if (MANUAL_ENGINE_POSTGRES != None):
        sqlRequest = "SELECT table_schema,table_name FROM information_schema.tables where table_schema like '%%alesforce' ORDER BY table_schema,table_name"
        result = MANUAL_ENGINE_POSTGRES.execute(sqlRequest)
        return __resultToDict(result)
        
    return {'data' : [], "columns": []}

def get_debug_all(request):
    str_debug = '* url: {}\n* method:{}\n'.format(request.url, request.method)
    str_debug += '* Args:\n'
    for entry in request.args:
        str_debug = str_debug + '\t* {} = {}\n'.format(entry, request.args[entry])
    str_debug += '* Headers:\n'
    for entry in request.headers:
        str_debug = str_debug + '\t* {} = {}\n'.format(entry[0], entry[1])
    return str_debug

@app.route('/', methods=['GET'])
def rooturlapp():
    try :
        logger.debug(get_debug_all(request))

        key = {'url' : request.url}
        tmp_dict = None
        data_dict = None
        tmp_dict = __getCache(key)
        if ((tmp_dict == None) or (tmp_dict == '')):
            logger.debug("Data not found in cache")
            data_dict  = __getTables()
            __setCache(key, ujson.dumps(data_dict), 300)
        else:
            logger.debug("Data found in redis, using it directly")
            data_dict = ujson.loads(tmp_dict)
        return render_template(RENDER_INDEX,
                            entries=data_dict['data'])

    except Exception as e:
        import traceback
        traceback.print_exc()
        return "An error occured, check logDNA for more information", 200





@app.route('/error', methods=['GET'])
def error():
    logger.debug(get_debug_all(request))
    logger.debug("Generating Error")
    error_code = 500
    if ('error_code' in request.args):
        error_code = int(request.args['error_code'])
    return "Error !!!!!!",error_code


@app.route('/getObjects', methods=['GET'])
def getObjects():
    try: 
        # logs all attributes received
        logger.debug(get_debug_all(request))
        # gets user agent
        user_agent = request.headers['user_agent']
        # gets object name
        object_name=''
        if ('name' in request.args):
            object_name = request.args['name']
        else:
            return "Error, must specify a object name with ?name=xxx", 404
            
        key = {'url' : request.url}
        tmp_dict = None
        data_dict = None
        tmp_dict = __getCache(key)
        if ((tmp_dict == None) or (tmp_dict == '')):
            logger.debug("Data not found in cache")
            data_dict  =__getObjects(object_name) 
            __setCache(key, ujson.dumps(data_dict), 300)
        else:
            logger.debug("Data found in redis, using it directly")
            data_dict = ujson.loads(tmp_dict)

        logger.info(data_dict)
        logger.info(data_dict['data'])
        if ('Mozilla' in user_agent):
            logger.info("Treating request as a web request, output to Web page")
            return render_template(RENDER_TABLE_DATA,
                            columns=data_dict['columns'],
                            object_name=object_name,
                            entries = data_dict['data'])
        else:
            logger.info("Treating request as an API request, output to Json only")
            return data_dict, 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return "An error occured, check logDNA for more information", 200



if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=int(PORT))




