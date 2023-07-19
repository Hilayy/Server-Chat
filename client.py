from socket import *
from tkinter import *


def read_socket_details():
    with open('/Users/User/Desktop/socket details.txt', 'r') as f:
        lines = f.readlines()
        lines = [line.strip() for line in lines]
        return lines[0:2]


def close_window():
    root.destroy()


def message_wrap(_data, msg_type):
    if msg_type == 's':
        _data = _data.decode('utf-8')
        _data = 'Server: ' + _data
        fg_color = 'red'
    elif msg_type == 'c':
        _data = 'You: ' + _data
        fg_color = '#2f58d4'
    else:
        fg_color = 'purple'

    for i in range(0, len(_data), 58):
        chat_log.insert(END, _data[i:i + 58])
        chat_log.itemconfig(END, fg=fg_color)


def retrieve_text(event):
    text = text_box.get()
    if text != '':
        text_box.delete(0, END)
        message_wrap(text, 'c')
        try:
            sock.sendall(text.encode('utf-8'))
        except Exception as e:
            message_wrap("Server is Closed, Ending session.....".encode('utf-8'), 'i')
            root.after(3000, close_window)
            return

        data = sock.recv(BUFSIZ)
        message_wrap(data, 's')
        global quit_mode
        if quit_mode and data.decode('utf-8') == 'Password is correct, ending connection.':
            root.after(3000, close_window)
            return
        else:
            quit_mode = False
        if text == 'quit':
            quit_mode = True
        chat_log.yview_moveto(1)


HOST, PORT = read_socket_details()
BUFSIZ = 1024
ADDR = (HOST, int(PORT))

sock = socket(AF_INET, SOCK_STREAM)
sock.connect(ADDR)

root = Tk()
root.title('client side')
root.geometry('500x800')
root.minsize(500, 800)
root.maxsize(500, 800)
root.configure(bg='#395cdb')

chat_log = Listbox(root, height=30, width=50, font=('Helvetica', 14))
chat_log.configure(bg="#a3abff", fg="#2f58d4")
chat_log.pack(pady=2)

text_box = Entry(root, width=80, font=('Helvetica', 15), bg='#395cdb', fg='#1037c4')
text_box.pack(pady=0)
text_box.bind('<Return>', retrieve_text)
quit_mode = False

root.mainloop()
sock.close()
