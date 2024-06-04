import pika
import json


class WriteToRabbit():
    def __init__(self, queue) -> None:
        self.conn = {
            "url":"localhost",
            "exchange":"Grabbers",
            "queue":"Grabbers",
            "routing_key":"RAW",
        }
        self.rabbitConnection = None
        self.rabbitchannel=None

        self.queue = queue
        self.start()

    @property 
    def channel(self):
        if self.rabbitConnection is None:
            return self.reconnect()
        if not self.rabbitConnection.is_open:
            return self.reconnect()
        return self.rabbitChannel

    def reconnect(self):
        self.rabbitConnection=pika.BlockingConnection(pika.ConnectionParameters(self.conn['url']))
        self.rabbitChannel=self.rabbitConnection.channel()
        return self.rabbitchannel
    
    def start(self):
        while True:
            try:
                self.channel
                if self.queue.empty():
                    continue
                message = self.queue.get()
                self.POST(message)
            except:
                pass


    def POST(self, message):
        self.channel.queue_declare(queue=self.conn['queue'], durable=True)

        self.channel.basic_publish(exchange=self.conn['exchange'],
                      routing_key=self.conn["routing_key"],
                      body=json.dumps(message, ensure_ascii=False, default=str),
                      properties=pika.BasicProperties(
                          delivery_mode = 2,
                      ))

