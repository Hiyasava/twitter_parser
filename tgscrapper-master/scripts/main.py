from pyrogram import Client, types, filters
from Telegramwork import Telegramwork
from RabbitThread import RabbitThread
from multiprocessing import Queue

client = Client('my_account')

class Main():
    
    def __init__(self) -> None:
        q = Queue()

        self.tgwork = Telegramwork(q)
        client.mainclass = self
        self.rabbit = RabbitThread()
        self.rabbit.start_process(q)

    @client.on_message(filters = filters.group & filters.forwarded)
    async def forwarded_messages_group(client: Client, Message: types.Message):
        client.mainclass.tgwork.get_forwarded_messages_from_group(Message=Message)


    @client.on_message(filters = filters.channel & filters.forwarded)
    async def forwarded_messages_channel(client: Client, Message: types.Message):
        client.mainclass.tgwork.get_forwarded_messages_from_channel(Message=Message)
    

    @client.on_message(filters=filters.group & filters.reply)
    async def replied_messages(client:Client, Message: types.Message):
        client.mainclass.tgwork.get_group_messages(Message)
        client.mainclass.tgwork.get_replied_messages_from_group(Message=Message)


    @client.on_message(filters = filters.channel & filters.reply)
    async def replied_messages_channel(client: Client, Message: types.Message):
        client.mainclass.tgwork.get_channel_messages(Message)
        client.mainclass.tgwork.get_replied_messages_from_channel(Message=Message)


    @client.on_message(filters=filters.channel)
    async def channel_messages(client: Client, Message: types.Message):
        client.mainclass.tgwork.get_channel_messages(Message=Message)


    @client.on_message(filters=filters.group)
    async def group_messages(client:Client, Message: types.Message):
        client.mainclass.tgwork.get_group_messages(Message=Message)


    @client.on_edited_message(filters=filters.group)
    async def group_edited_messages(client:Client, Message: types.Message):
        client.mainclass.tgwork.group_message(Message=Message)

    @client.on_edited_message(filters=filters.channel)
    async def group_edited_messages(client:Client, Message: types.Message):
        client.mainclass.tgwork.channel_message(Message=Message)

    @client.on_deleted_messages()
    async def group_deleted_messages(client:Client, Message: types.Message):
        client.mainclass.tgwork.deleted_message(Message=Message)

if __name__ == '__main__':
    Umain = Main()
    client.run()