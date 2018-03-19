

def __resultToDict(result):
    arrayData =  []
    column_names = [desc[0] for desc in result.cursor.description]

    for entry in result:
        #logger.debug(entry)
        resDic = {}
        for column in column_names:
            resDic[column] = entry[column]
        arrayData.append(resDic)
    return {'data' : arrayData, 'columns': column_names}