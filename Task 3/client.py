# Qasim Batrawi 1220204
# Taleed Hamadneh 1220006

from socket import *
import threading
import time

end_the_game = False # flag
continue_the_game = False # flag

serverName = '127.0.0.1' #'192.168.1.126' # mine  runing client and server on same machine : localhost
tcp_port = 6000
udp_port = 6001

# TCP setup
tcp_socket = socket(AF_INET, SOCK_STREAM)
tcp_socket.connect(('127.0.0.1', tcp_port))

# UDP setup
udp_socket = socket(AF_INET, SOCK_DGRAM)

#join with unique username
username = input("\nEnter your username: ") #from user
tcp_socket.send(username.encode())
response = tcp_socket.recv(1024).decode()
while response == "Username already taken, try another.":
    username = input("Username already taken, try another: ")
    tcp_socket.send(username.encode())
    response = tcp_socket.recv(1024).decode()


print(response) # Connected as player 1

message = tcp_socket.recv(1024).decode()
print(message, end="") # waiting room message


start_game = ' '
while not start_game.startswith('Game started'):
    print(start_game)
    start_game = tcp_socket.recv(1024).decode()
    
print(start_game)

game_over = threading.Event()

#receiving feedback
def receive_feedback():
    global end_the_game, continue_the_game

    # settimeout(2) makes the client wait only up to 2 seconds #Without settimeout(), if the server doesnt respond, 
    # the client would get stuck on that recvfrom() line forever
    udp_socket.settimeout(2) 
    while True:
        try:
            feedback, serverAddress = udp_socket.recvfrom(1024)
            print(feedback.decode(), end="")
            if feedback.decode() == "Feedback: CORRECT.":
                end_the_game = True
                break
            if feedback.decode().endswith("continue? "):
                time.sleep(5)
                if continue_the_game == False:
                    end_the_game = True
                    break
            print("Enter your guess: ", end="", flush=True)
        except:
            continue
       

# sending guesses       
def guess_loop():
    global end_the_game, continue_the_game
    print("Enter your guess: ", end="", flush = True)
    start = time.time()
    while time.time() - start < 60 and not end_the_game:
        time.sleep(0.1)
        if end_the_game:
            break
        guess = input()
        udp_socket.sendto(guess.encode(), (serverName, udp_port))
        if guess == "yes":
            continue_the_game = True
            time.sleep(5)
        

#receive final results via TCP
def listen_for_result():
    global end_the_game
    final_result=' '
    while not final_result.startswith('\n=== GAME RESULTS ===') and not final_result.startswith('\n=== GAME OVER ==='):
            final_result = tcp_socket.recv(1024).decode()
            print("\n" + final_result)
            game_over.set()

    
receive_thread = threading.Thread(target=receive_feedback) # receive_thread: Handles receiving feedback from the server 
guess_thread = threading.Thread(target=guess_loop) # guess_thread: Handles sending guesses to the server 
result_thread = threading.Thread(target=listen_for_result)

# start the threads
receive_thread.start()
guess_thread.start()
result_thread.start()

# wait for threads to finish
receive_thread.join()
guess_thread.join()
result_thread.join()

tcp_socket.close()
udp_socket.close()

#Disconnected from the game
