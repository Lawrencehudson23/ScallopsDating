import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Message, User, Match, Profile
from channels.auth import login
from django.db.models import Q, Count, Max

class ChatConsumer(WebsocketConsumer):

    def get_matches(self, data):
        matches = Match.objects.filter(user1=data['from']).annotate(message = Max('messages')).order_by('-message').all()[:15]
        new_messages = []
        matches_with_no_msgs = []
        for match in matches:
            message = match.messages.order_by('-created_at').all()[:1]
            print(match.user1.profile)
            print("*******************************************")
            print(match.user2.profile)
            if match.id > Match.objects.get(user1=match.user2.id, user2=data['from']).id:
                matchId = Match.objects.get(user1=match.user2.id, user2=data['from']).id
            else:
                matchId = match.id
            if len(message)>0:
                new_messages.append({
                    "match_id" : matchId,
                    # MATCH ID NEEDS TO BE SMALLER ONE
                    "matched_user_first_name": match.user2.first_name,
                    "matched_user_last_name": match.user2.last_name,
                    'match_image':match.user2.profile.image.url,
                    'content':message[0].content,
                    'created_at':str(message[0].created_at),
                })
            else:
                matches_with_no_msgs.append({
                    "match_id" : matchId,
                    "matched_user_first_name": match.user2.first_name,
                    "matched_user_last_name": match.user2.last_name,
                    "match_image":match.user2.profile.image.url,
                })
        return {
            "new_messages":new_messages,
            'matches_with_no_msgs':matches_with_no_msgs,
        }


    def fetch_messages(self, data):
        # author_id = data['from']
        # author = User.objects.get(id= self.scope["session"]["user_id"])
        # messages = author.author_messages.order_by('-created_at').all()[:10]

        messages = Match.objects.get(id=self.scope['url_route']['kwargs']['match_id']).messages.order_by('-created_at').all()

        content = {
            'command':'messages',
            'messages' : self.messages_to_json(messages),
            'matches' : self.get_matches(data),
        }
        self.send_message(content)

    def new_message(self, data):
        author_user = User.objects.get(id= data["from"])
        recipient = User.objects.get(id=data['to'])
        message = Message.objects.create(content=data['message'],author=author_user, recipient = recipient)
        m1 = Match.objects.get(user1=author_user.id, user2=recipient.id).messages.add(message)
        m2 = Match.objects.get(user1=recipient.id, user2=author_user.id).messages.add(message)
        content = {
            'command' : 'new_message',
            'message' : self.message_to_json(message),
            'matches' : self.get_matches(data),
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
        print(self.scope['url_route']['kwargs'])
        self.room_name = self.scope['url_route']['kwargs']['match_id']
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