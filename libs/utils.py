import datetime
from flask import request

def __resultToDict(result):
    arrayData =  []
    column_names = [desc[0] for desc in result.cursor.description]

    for entry in result:
        #logger.debug(entry)
        resDic = {}
        for column in column_names:
            #if (isinstance(entry[column], datetime.date)):
            #    print('Date found : ' + entry[column].__str__())
            resDic[column] = entry[column]

            
        arrayData.append(resDic)
    return {'data' : arrayData, 'columns': column_names}


def get_debug_all(request):
    str_debug = '* url: {}\n* method:{}\n'.format(request.url, request.method)
    str_debug += '* Args:\n'
    for entry in request.args:
        str_debug = str_debug + '\t* {} = {}\n'.format(entry, request.args[entry])
    str_debug += '* Headers:\n'
    for entry in request.headers:
        str_debug = str_debug + '\t* {} = {}\n'.format(entry[0], entry[1])
    str_debug += '* Form:\n'
    for entry in request.form:
        str_debug = str_debug + '\t* {} = {}\n'.format(entry, request.form[entry])        
    return str_debug    