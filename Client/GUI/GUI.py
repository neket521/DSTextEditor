from Client.client_protocol import Client
import Tkinter
from Tkinter import *
from ScrolledText import *
import tkFileDialog
import tkMessageBox
import time, threading
root = Tkinter.Tk(className=" Awesome distributed text editor")
textPadWidth = 80
textPad = ScrolledText(root, width = textPadWidth, height=20)
length = 0
linecount = 0
old_length = -1
counter = True

#Timer
def timer():
    global old_length, length, counter
    if(old_length == length and length !=0 and counter):
        update()
        counter = False
        #print(old_length)
        #print(length)
    old_length = length
    threading.Timer(5, timer).start()
timer()




def getLength():
    return len(textPad.get('1.0', END + '-1c'))

def getLines():
    text = textPad.get('1.0', END + '-1c').split('\n')
    return [[j[i:i + 80] for i in range(0, len(j), textPadWidth)] for j in text]

def update(*args):
    tosend = getLines()[-1]
   ## call sending method from client
    print tosend

def newline_check(*args):
    global counter, length, linecount
    counter = True
    length = getLength()
    if (length+1) % textPadWidth == 0 and length != 0:
        linecount += 1
        update()

    elif int(length / textPadWidth) != linecount:
        linecount = int(length / textPadWidth)
        update()

textPad.bind("<KeyRelease>", newline_check)
textPad.bind("<Return>", update)


def new_command():
    textPad.delete('1.0', END)


def open_command():
    file = tkFileDialog.askopenfile(parent=root, mode='rb', title='Select a file')
    if file != None:
        contents = file.read()
        textPad.insert('1.0', contents)
        file.close()



def save_command():
    file = tkFileDialog.asksaveasfile(mode='w')
    if file != None:
    # slice off the last character from get, as an extra return is added
        data = textPad.get('1.0', END+'-1c')
        file.write(data)
        file.close()

def exit_command():
    if tkMessageBox.askokcancel("Quit", "Do you really want to quit?"):
        root.destroy()

def about_command():
    label = tkMessageBox.showinfo("About", "Just Another TextPad \n Copyright \n No rights left to reserve")

def share_command():
    print "I'm not sharing, I'm just hanging out here.."

def open_shared_command():
    print "Opening file on the server side.."

#def dummy():
#    print "I am a Dummy Command, I will be removed in the next step"



menu = Menu(root)
root.config(menu=menu)
filemenu = Menu(menu)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="New", command=new_command)

filemenu.add_command(label="Save", command=save_command)
filemenu.add_command(label="Share", command=share_command)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=exit_command)

openmenu = Menu(menu)
menu.add_cascade(label="Open...", menu=openmenu)
openmenu.add_command(label="Open local file", command=open_command)
openmenu.add_command(label="Open shared file", command=open_shared_command)

helpmenu = Menu(menu)
menu.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="About...", command=about_command)
#
textPad.pack()

root.mainloop()