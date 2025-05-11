#Taleed Hamadneh 1220006
#Qasim Batrawi 1220204    
from socket import *
import os
serverPort = 9906
#TCP socket
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
# listen to the HTTP request on port 9906
serverSocket.listen(30) # up to 30 clients
print('Web Server is listening on port 9906 ...')

def send_response(response_code, response_type):
    status_line = ""
    if int(response_code) == 200:
        status_line = "HTTP/1.1 200 OK\r\n"
    elif int(response_code) == 404:
        status_line = "HTTP/1.1 404 Not Found\r\n"
    elif int(response_code) == 307:
        status_line = "HTTP/1.1 307 Temporary Redirect\r\n"
    else:
        status_line = f"HTTP/1.1 {response_code} Unknown\r\n"

    connectionSocket.send(status_line.encode())
    res = "Content-Type: " + response_type + "; charset=utf-8\r\n"
    connectionSocket.send(res.encode())
    connectionSocket.send("\r\n".encode())
    
    print(f"Response Sent: {status_line.strip()} | Client IP: {client_ip} | Client Port: {client_port} | Server Port: {serverPort}\n")

    
#when the requested file is unavailable
def Error(ip,port):
        send_response(404,'text/html')
        error = ('<!DOCTYPE html>'
                '<html lang="en">'
                '<style>'
                '*{text-align: center;padding:10px;}'
                'h1{font-size:50px;}'
                'p{font-size:20px;}'
                '</style>'
                '<head>'
                '<meta charset="UTF-8">'
                '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
                '<title>Error 404</title>'
                '</head>'
                '<body>'
                '<h1 style="color: red;">The file is not found!</h1>'
                '<p>IP Address: ' + str(ip) + ', Port Number: ' + str(port) + '</p>'
                '</body></html>'
        )
        connectionSocket.send(error.encode())


while True: #ALWAYS ON SERVER
    # Show all the files (that are available in the server) and separate them based on their types
    files = os.listdir('.')
    temp_files = []
    for f in files:
        if os.path.isfile(f):
            temp_files.append(f)
    files = temp_files

    html = os.listdir('./templates')
    temp_html = []
    for f in html:
        if os.path.isfile(os.path.join('./templates', f)):
            temp_html.append(f)
    html = temp_html

    css = os.listdir('./static/css')
    temp_css = []
    for f in css:
        if os.path.isfile(os.path.join('./static/css', f)):
            temp_css.append(f)
    css = temp_css

    images = os.listdir('./static/images')
    normal_images = []
    for f in images:
        if os.path.isfile(os.path.join('./static/images', f)):
            normal_images.append(f)
    images = normal_images

    videos = os.listdir('./static/videos')
    
    #connection is established
    connectionSocket, addr = serverSocket.accept()
    client_ip = addr[0]
    client_port = addr[1]
    print('Got connection from', "IP: " + client_ip + ", Port: " + str(client_port) + ", Server Port: 9906")
    
    sentence = connectionSocket.recv(4096).decode() #4096 is the maximum number of bytes to receive from the socket at once
    
    try:
        #get the request line from the request (This line has the requested object)
        sen = sentence.split('\n')[0]
        request = sen.split(' ')[1]
        print("The Request is : " + request) # print http request
        print(sentence)
    except :
        print("BAD REQUEST")
        continue

    # Main_English request
    if request == "/" or request == "/index.html" or request == "/main_en.html" or request == "/en":

        if 'main_en.html' in html: # check if the file exists
            with open('./templates/main_en.html','r', encoding='utf-8') as Main_English: # encoding is needed to show arabic words
                Main_English = Main_English.read()
            send_response(200,'text/html') # 200 -> OK , the content is html
            connectionSocket.send(Main_English.encode()) # send the file to the client through the socket (encoding from strings to byte)
        else:
            Error(client_ip, client_port) # 404 ERROR
            
    # Main_Arabic request
    elif request == "/ar" or request == "/main_ar.html":

        if 'main_ar.html' in html: # check if the file exists
            with open('./templates/main_ar.html','rb') as Main_Arabic:
                Main_Arabic = Main_Arabic.read()
            send_response(200,'text/html')
            connectionSocket.send(Main_Arabic)
        else:
            Error(client_ip, client_port)


    # if this statement (/request_handler?material) is in the url, then the user submited an image/video name in the html form
    # request: /html/request_handler?material=example&type=image
    elif request.startswith("/html/request_handler?material"):
        input = request.split('=')[1].split('&')[0] # to get the input from the user
        type = request.split('=')[2] # to get the type image/video

        if type == 'image':
            object1 = input + '.jpg' # to search for the image with jpg extension
            object2 = input + '.png' # to search for the image with png extension

            if object1 in images:
                path = './static/images/' + object1
                with open(path,'rb') as image:
                    image = image.read()
                send_response(200,'image/jpg')
                connectionSocket.send(image)
            elif object2 in images:
                path = './static/images/' + object2
                with open(path,'rb') as image:
                    image = image.read()
                send_response(200,'image/png')
                connectionSocket.send(image)
            else:
                connectionSocket.send("HTTP/1.1 307 Temporary Redirect\r\n".encode())
                connectionSocket.send('Content-Type: text/html; charset=utf-8\r\n'.encode())
                type = type.replace(" ", "+")
                location = "Location:http://www.google.com/search?q="+input+"&udm=2\r\n"
                connectionSocket.send(location.encode())
                connectionSocket.send('\r\n'.encode())
                print(f"Response Sent: HTTP/1.1 307 Temporary Redirect | Client IP: {client_ip} | Client Port: {client_port} | Server Port: {serverPort}\n")
                print("Redirect to Google\r\n")
        else:            
            object = input + '.mp4'
            if object in videos:
                path = './static/videos/' + object
                with open(path,'rb') as video:
                    video = video.read()
                send_response(200, 'video/mp4')
                connectionSocket.send(video)
            
            else:
                connectionSocket.send("HTTP/1.1 307 Temporary Redirect\r\n".encode())
                connectionSocket.send('Content-Type: text/html; charset=utf-8\r\n'.encode())
                location = "Location:https://www.youtube.com/results?search_query=" + input +"\r\n"
                connectionSocket.send(location.encode())
                connectionSocket.send('\r\n'.encode())
                print(f"Response Sent: HTTP/1.1 307 Temporary Redirect | Client IP: {client_ip} | Client Port: {client_port} | Server Port: {serverPort}")
                print("Redirect to Youtube\r\n")


    # other html file request
    # request: /html/mySite_1220006_ar.html
    elif request.startswith("/html/"):
        html_file_name = request.split('/')[2] # get the html file name (for example: mySite_1220006_ar.html)
        if html_file_name in html:
            path = "./templates/" + html_file_name
            with open(path,'rb') as Local_Webpage_Arabic:
                Local_Webpage_Arabic = Local_Webpage_Arabic.read()
            send_response(200,'text/html')
            connectionSocket.send(Local_Webpage_Arabic)
        else:
            Error(client_ip, client_port)
            
    # css file request
    # request: /static/css/example.css
    elif request.startswith("/static/css/"):
        css_file_name = request.split('/')[3] # get the image name (for example: main.css)
        if css_file_name in css: # check if the file exists
            path = './static/css/' + css_file_name # path of the css file 
            with open(path,'r') as cssFile:
                cssFile = cssFile.read()
            send_response(200,'text/css') # 200 -> OK , the content is css
            connectionSocket.send(cssFile.encode()) # send the file to the client through the socket (encoding from strings to byte)
        else:
            Error(client_ip, client_port)

    # images request
    # request: /static/images/example.png
    elif request.startswith("/static/images/"):
        image_file_name = request.split('/')[3] # get the image name (for example: background.png)
        if image_file_name in images:
            path = './static/images/' + image_file_name # path of the image
            response_type = 'image/' + path.split('.')[-1] # path.split('.')[-1] returns the the extension (for example: png)
            with open(path,'rb') as image:
                image = image.read()
            send_response(200, response_type)
            connectionSocket.send(image) # send the image to the client through the socket
        else:
            Error(client_ip, client_port)

    # videos requests (similar to image request)
    # request: request: /static/videos/example.mp4
    elif request.startswith("/static/videos/"):
        video_file_name = request.split('/')[3] # get the video file name
        if video_file_name in videos:
            type = 'video/' + video_file_name.split('.')[-1] # get the video extension
            path = './static/videos/' + video_file_name
            with open(path, 'rb') as video:
                video = video.read()
            send_response(200, type)
            connectionSocket.send(video)
        else:
            Error(client_ip, client_port)


    #if the client made any request that does not exist
    else:
        try:
            object = request.split('/')[1]
            if object in files or object in html or object in css or object in images or object in videos:
                type = object.split('.')[-1]
                if object in html:
                    object = './templates/' + object
                elif object in css:
                    object = './static/css/' + object
                elif object in images:
                    object = './static/images/' + object
                elif object in videos:
                    object = './static/videos/' + object

                if type == 'html':
                    send_response(200, 'text/html')
                    with open(object, 'r') as file:
                        file = file.read()
                    connectionSocket.send(file.encode())
                elif type == 'css':
                    send_response(200, 'text/css')
                    with open(object, 'rb') as file:
                        file = file.read()
                    connectionSocket.send(file)
                elif type == 'jpg':
                    send_response(200, 'image/jpg')
                    with open(object, 'rb') as file:
                        file = file.read()
                    connectionSocket.send(file)
                elif type == 'png':
                    send_response(200, 'image/png')
                    with open(object, 'rb') as file:
                        file = file.read()
                    connectionSocket.send(file)
                elif type == 'mp4':
                    send_response(200, 'video/mp4')
                    with open(object, 'rb') as file:
                        file = file.read()
                    connectionSocket.send(file)
                else:
                    send_response(200, 'text/html') # default
                    with open(object, 'rb') as file:
                        file = file.read()
                    connectionSocket.send(file)
            else:
                Error(client_ip,client_port)
        except IndexError:
            print('Bad Request')

    connectionSocket.close()