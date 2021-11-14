from concurrent import futures

import grpc
import time

import components.components_pb2 as chat
import components.components_pb2_grpc as rpc


class ChatServer(rpc.ChatServerServicer):

    def __init__(self):
        self.chats = []

    def Connect(self, request, context):
        print("[{}] is now online".format(request.username))

        return chat.Empty()

    def ChatStream(self, request_iterator, context):
        lastindex = 0

        while True:
            while len(self.chats) > lastindex:
                n = self.chats[lastindex]
                lastindex += 1
                yield n

    def SendMessage(self, request: chat.Message, context):
        print("New message from: [{}] to: [{}]".format(request.sender, request.destinatary))

        self.chats.append(request)
        return chat.Empty()


if __name__ == '__main__':
    port = 11912

    # Create a server with 10 clients as a limit 
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  

    rpc.add_ChatServerServicer_to_server(ChatServer(), server)

    print('Starting server. Listening...')
    server.add_insecure_port('[::]:' + str(port))
    server.start()

    while True:
        time.sleep(64 * 64 * 100)