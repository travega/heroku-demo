from appsrc import app, WEBPORT


app.run(host='0.0.0.0', debug=True, port=int(WEBPORT))