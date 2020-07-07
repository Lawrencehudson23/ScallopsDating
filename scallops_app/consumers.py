import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Message, User
from channels.auth import login

class ChatConsumer(WebsocketConsumer):

    def fetch_messages(self, data):
        author_id = data['from']
        author = User.objects.get(id= self.scope["session"]["user_id"])
        messages = author.author_messages.order_by('-created_at').all()[:10]
        content = {
            'command':'messages',
            'messages' : self.messages_to_json(messages)
        }
        self.send_message(content)

    def new_message(self, data):
        author_user = User.objects.get(id= self.scope["session"]["user_id"])
        recipient = User.objects.get(id=data['to'])
        message = Message.objects.create(content=data['message'],author=author_user, recipient = recipient)
        content = {
            'command' : 'new_message',
            'message' : self.message_to_json(message)
        }
        return self.send_chat_message(content)


    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result
    
    def message_to_json(self, message):
        return {
            'author':message.author.id,
            'recipient':message.recipient.id,
            'content':message.content,
            'created_at':str(message.created_at)
        }

    commands= {
        'fetch_messages': fetch_messages,
        'new_message': new_message
    }

    def connect(self):
        session = self.scope['session']
        print("*********** USER " + str(session["user_id"]) + " CONNECTED *************")
        self.room_name = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = 'chat_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )
    
    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps(message))