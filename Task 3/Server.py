# Qasim Batrawi 1220204
# Taleed Hamadneh 1220006

from socket import *
from threading import *
import time
import random

ServerName = '127.0.0.1'
ServerPort_TCP = 6000
ServerPort_UDP = 6001 
ServerSocket_TCP = socket(AF_INET, SOCK_STREAM) # TCP
ServerSocket_UDP = socket(AF_INET, SOCK_DGRAM)  # UDP

MinPlayers = 2
MaxPlayers = 4
TimeToGuess = 10
GameDuration = 60
MinRange = 1
MaxRange = 100
NumberToGuess = random.randint(MinRange, MaxRange)
GameStarted = 0 # flag to check if the game has started or not

list_of_clients = []

winner_name = None

# find the IP of my Server
hostname = gethostname() # qasimbatrawi
ServerIP = gethostbyname(hostname) # IP of my device (e.g. 192.168__)

# bind the port of my server
ServerSocket_TCP.bind((ServerName, ServerPort_TCP))
ServerSocket_UDP.bind((ServerName, ServerPort_UDP))


ServerSocket_TCP.listen(MaxPlayers) # the server is listening for new tcp connections
# cant listen to UDP since its connectionless


print(f"Server Started on <{ServerName}>: TCP {ServerPort_TCP}, UDP {ServerPort_UDP}")

def listen_tcp():
    while True:
        connectionSocket, address = ServerSocket_TCP.accept() # new client connection. address = (client_ip, client_tcp_port)
        thread = Thread(target=handle_client_tcp, args=(connectionSocket, address)) # apply new thread for the new client
        thread.start()
        
def handle_client_tcp(connectionSocket, address):
    global GameStarted
    try:
        client_name = connectionSocket.recv(2048).decode()
        while True:
            if any(client_name == client['name'] for client in list_of_clients):
                connectionSocket.send("Username already taken, try another.".encode())
                client_name = connectionSocket.recv(2048).decode()
            else:
                connectionSocket.send(f"Connected as {client_name}\nTCP connection established\n".encode())
                break
            
        list_of_clients.append({
            'name': client_name,
            'IP': address[0],
            'tcp_port': address[1],
            'udp_port': None,
            'tcp_socket': connectionSocket
        })
        
        print(f"New Connection from ({address[0]}, {address[1]}) as {client_name}")
        message = "Waiting Room:\n"
        for client in list_of_clients:
            message+=client['name']
            message+='\n'

        connectionSocket.send(message.encode())
        
        while len(list_of_clients) < MinPlayers:
            continue
        
        GameStarted = True
        message = "Game started with players: " + ", ".join(client['name'] for client in list_of_clients)
        message+=f'\nYou have {GameDuration} seconds to guess the number ({MinRange} - {MaxRange})!\n'

        connectionSocket.send(message.encode())    
    except:
        connectionSocket.send("\nConnection Failed!\n".encode())


def listen_udp():
    global winner_name, list_of_clients, GameStarted
    ServerSocket_UDP.settimeout(TimeToGuess) # the client has 10 seconds to send a response

    while True:
        if winner_name is not None: # the game has ended
            break
        if not GameStarted: # the game has not started yet
            continue
        try:
            message, address = ServerSocket_UDP.recvfrom(2048)
        except:
            continue

        client_IP, client_udp_port = address[0], address[1]
        message = message.decode()
        the_client = None 
        
        for client in list_of_clients:
            if client['IP'] == client_IP and client['udp_port'] == client_udp_port:
                the_client = client
                break
            elif client['IP'] == client_IP and client['udp_port'] is None:
                client['udp_port'] = client_udp_port
                the_client = client
                break

        if the_client is None:
            continue

        guess = int(message)
        if guess == NumberToGuess:
            if GameStarted and winner_name is None:
                winner_name = the_client['name']
                GameStarted = False
                response_to_one_client_udp(client_IP, client_udp_port, "Feedback: CORRECT.")
        else:
            if guess < MinRange or guess > MaxRange:
                feedback = 'Warning: Out of the range, miss your chance\n'
            elif guess < NumberToGuess:
                feedback = 'Feedback: Higher\n'
            else:
                feedback = 'Feedback: Lower\n'
            response_to_one_client_udp(client_IP, client_udp_port, feedback)


def response_to_one_client_udp(client_IP , client_udp_port , message): # UDP
   try: 
        ServerSocket_UDP.sendto(message.encode(), (client_IP , client_udp_port)) 
   except:
        pass

def wait_and_send_results():
    global winner_name, GameStarted
    start = time.time()

    while time.time() - start < GameDuration:
        if winner_name is not None:
            GameStarted = False
            break
        time.sleep(1)

    if winner_name is None:
        winner_name = "No one"
    
    game_result()


def game_result():
    global winner_name
    new_message = ""

    if winner_name == "No one":
        print("No One Wins\n")
        new_message = f"\n=== GAME OVER ===\nTarget number was: {NumberToGuess}\nNo one wins\n"
    else:
        print(f"Guess Completed. Winner: {winner_name}\n")
        new_message = f"\n=== GAME RESULTS ===\nTarget number was: {NumberToGuess}\nWinner: {winner_name}\n"

    for client in list_of_clients:
        client['tcp_socket'].send(new_message.encode())

  
def start_game():
    
    global GameStarted, list_of_clients

    while len(list_of_clients) < MinPlayers and not GameStarted:
        continue    

    print(f"Starting game with {len(list_of_clients)} players")
    Thread(target=wait_and_send_results).start() #thread to send the results


def check_disconnections():
    global list_of_clients, GameStarted, winner_name

    while True:
        if GameStarted:
            for client in list_of_clients:
                try:
                    client['tcp_socket'].send("".encode())
                except:
                    client_name = client['name']
                    print(f"{client_name} disconnected from the game")
                    list_of_clients.remove(client)

                    for other_client in list_of_clients:
                        
                        try:
                            new_message = f"\n{client_name} decided to leave you alone in this game, do you want to continue? "
                            
                            ServerSocket_UDP.settimeout(None)
                            ServerSocket_UDP.sendto(new_message.encode(), (other_client['IP'] , other_client['udp_port']))
                            response, address = ServerSocket_UDP.recvfrom(2048)
                            response = response.decode()
                            ServerSocket_UDP.settimeout(10)
                            
                            if response != "yes":
                                print(f"{other_client['name']} decided to end the game")
                                GameStarted = False
                                winner_name = "No one"
                                return
                        except:
                            continue
        time.sleep(1)

     
def main():
    Thread(target=listen_tcp).start()
    Thread(target=listen_udp).start()
    Thread(target=check_disconnections).start()
    start_game()


if __name__ == '__main__':
    main()