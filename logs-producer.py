from server import channel
from tqdm import tqdm

logs_files = open("class-4/assets/web-server-nginx_dev.log", "r")

QUEUES = [
    {
        "name": "data-lake",
        "routing_key": "new_log"
    },
    {
        "name": "data-clean",
        "routing_key": "new_log"
    }
]

#boucle pour parcourir l'ensemble des logs
EXCHANGE_NAME = "topic-exchange-weblog"

# create the exchange of type topic
channel.exchange_declare(EXCHANGE_NAME, durable=True, exchange_type='topic')

# create 2 queues
for queue in QUEUES:
    channel.queue_declare(queue=queue['name'])
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue['name'], routing_key=queue['routing_key'])

# publish event while reading all the log rows
for log_row in logs_files:
    channel.basic_publish(exchange=EXCHANGE_NAME, routing_key="new_log", body=log_row)
    print(f"[x] New log `{log_row}` in topic `{queue['routing_key']}`")

#https://www.rabbitmq.com/tutorials/tutorial-one-python.html