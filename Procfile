worker-kafka: python worker_kafka.py 
web: cp newrelic.ini.template newrelic.ini; newrelic-admin generate-config $NEW_RELIC_LICENSE_KEY newrelic.ini; newrelic-admin run-program gunicorn run:app