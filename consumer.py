
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic
from pika.spec import BasicProperties
from functions.Myfunctions import process_raw_message,process_msg_data_clean
from functions.models import RawLog
from functions.orm_conn import CreateEngine
from server import channel

# # Create connection to MySQL DB
# con = CreateEngine()


# consume messages from queues
channel.basic_consume(queue="data-clean",on_message_callback=process_msg_data_clean, auto_ack=True) 


channel.basic_consume(queue="data-lake",on_message_callback=process_raw_message, auto_ack=True)


channel.start_consuming()
