from sqlalchemy import create_engine
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime 
import os 
import uuid
from libs import utils , logs , rediscache

DATABASE_URL = os.getenv('DATABASE_URL','')
MANUAL_ENGINE_POSTGRES = None
SALESFORCE_SCHEMA = os.getenv("POSTGRES_SCHEMA", "salesforce")
HEROKU_LOGS_TABLE = os.getenv("HEROKU_LOGS_TABLE", "heroku_logs__c") 

logger = logs.logger_init(loggername='app',
            filename="log.log",
            debugvalue="DEBUG",
            flaskapp=None)

if (DATABASE_URL != ''):
    Base = declarative_base()
    MANUAL_ENGINE_POSTGRES = create_engine(DATABASE_URL, pool_size=30, max_overflow=0)
    Base.metadata.bind = MANUAL_ENGINE_POSTGRES
    dbSession_postgres = sessionmaker(bind=MANUAL_ENGINE_POSTGRES)
    session_postgres = dbSession_postgres()
    logger.info("{} - Initialization done Postgresql ".format(datetime.now()))


def __getGameActivityById(gameactivity__c):
    sqlRequestActivityName = """
            select gameactivity__c.name ActivityName
            from 
                salesforce.gameactivity__c  
            where
                 gameactivity__c.sfid = %(gameactivity__c)s """

    resultActivityName = __execRequest(sqlRequestActivityName, {'gameactivity__c':gameactivity__c}) 
    return resultActivityName

def __getMatchsByGameActivityId(gameactivity__c):
    sqlRequest = """select match__c.sfid matchid ,
            match__c.date__c Date,
            participant__c_home.name as Participant_Home,
            participant__c_visitor.name Participant_Visitor
            
            from 
                    salesforce.match__c match__c, 
                    salesforce.participant__c participant__c_home , 
                    salesforce.participant__c participant__c_visitor
                    
            where match__c.gameactivity__c =  %(gameactivity__c)s
            and (participant__c_home.sfid = match__c.participant_home__c)
            and (participant__c_visitor.sfid = match__c.participant_visitor__c)
            
            order by 
            
            match__c.date__c DESC"""
    result = __execRequest(sqlRequest, {'gameactivity__c':gameactivity__c})
    return result

def __getMatchById(match_id):
    sqlRequest = """select date__c , 
       match__c.participant_home__c participant_home_id,
       match__c.participant_visitor__c participant_visitor_id,
       match__c.sfid match_id,
       match__c.gameactivity__c gameactivity__c,
       participant__home.name participant_home_name,
       participant__home.image__c participant_home_image,
       participant__home.description__c participant_home_description,
       participant__visitor.name participant_visitor_name,
       participant__visitor.image__c participant_visitor_image,
       participant__visitor.description__c participant_visitor_description
       
        from salesforce.match__c, 
            salesforce.participant__c participant__home,
            salesforce.participant__c participant__visitor

        where match__c.sfid= %(match_id)s 
        and (participant__home.sfid = match__c.participant_home__c)
        and (participant__visitor.sfid = match__c.participant_visitor__c)"""
    result = __execRequest(sqlRequest, {'match_id':match_id})
    return result



def __execRequest(strReq, Attributes):
    if (MANUAL_ENGINE_POSTGRES != None):
        result = MANUAL_ENGINE_POSTGRES.execute(strReq, Attributes)
        return utils.__resultToDict(result)
    return {'data' : [], "columns": []}



def __getObjects(tableName):
    if (MANUAL_ENGINE_POSTGRES != None):
        concat = SALESFORCE_SCHEMA + "." + tableName
        result = MANUAL_ENGINE_POSTGRES.execute("select * from {}".format(concat))
        return utils.__resultToDict(result)
        
    return {'data' : [], "columns": []}

def __getTables():
    if (MANUAL_ENGINE_POSTGRES != None):
        sqlRequest = "SELECT table_schema, table_name FROM information_schema.tables where table_schema like '%%alesforce' ORDER BY table_schema,table_name"
        result = MANUAL_ENGINE_POSTGRES.execute(sqlRequest)
        return utils.__resultToDict(result)
        
    return {'data' : [], "columns": []}


def __saveLogEntry(request):
    if (MANUAL_ENGINE_POSTGRES != None):
        url = request.url
        useragent = request.headers['user-agent']
        externalid = uuid.uuid4().__str__()
        creationdate  = datetime.now()

        sqlRequest = "insert into salesforce.heroku_logs__c (name, url__c, creationdate__c, externalid__c, useragent__c) values ( %(name)s, %(url)s, %(creationdate)s, %(externalid)s, %(useragent)s ) "

        MANUAL_ENGINE_POSTGRES.execute(sqlRequest,
                    {'tablename' : SALESFORCE_SCHEMA + '.' + HEROKU_LOGS_TABLE,
                    'url' : url,
                    'name' : externalid,
                    'creationdate':creationdate,
                    'externalid' : externalid,
                    'useragent':useragent} )    

def __checkHerokuLogsTable():
    key = {'checkHerokuLogTables' : "True"}
    tmp_dict = None
    tmp_dict = rediscache.__getCache(key)
    if ((tmp_dict == None) or (tmp_dict == '')):
        logger.info("Data not found in cache : heroku log data not known")
        hasDatabase = False
    
        if (MANUAL_ENGINE_POSTGRES != None):
            sqlRequest = 'SELECT EXISTS( SELECT * FROM information_schema.tables  WHERE table_schema = %(schema)s AND table_name = %(tablename)s ) '
            result = MANUAL_ENGINE_POSTGRES.execute(sqlRequest, {'schema' : SALESFORCE_SCHEMA, 'tablename' : HEROKU_LOGS_TABLE} )
            for entry in result:
                logger.info(entry['exists'])
                hasDatabase = entry['exists']
            if (hasDatabase == True):
                rediscache.__setCache(key, "True", 3600)
        return hasDatabase
    else:
        return True 
    
