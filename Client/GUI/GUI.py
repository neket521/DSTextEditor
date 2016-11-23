from Tkinter import *
from ScrolledText import *
import tkFileDialog
import tkMessageBox
import threading
import Tkinter


class UI:

    def __init__(self, client):
        self.client = client


    def init(self):
        self.root = Tkinter.Tk(className=" Awesome distributed text editor")
        self.textPadWidth = 80
        self.textPad = ScrolledText(self.root, width=self.textPadWidth, height=20)
        self.length = 0
        self.linecount = 0
        self.old_length = -1
        self.counter = True
        self.init_menu()
        self.timer()
        self.textPad.bind("<KeyRelease>", self.newline_check)
        self.textPad.bind("<Return>", self.update)
        self.textPad.pack()
        self.root.mainloop()

    def init_menu(self):
        menu = Menu(self.root)
        self.root.config(menu=menu)
        filemenu = Menu(menu)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New", command=self.new_command)

        filemenu.add_command(label="Save", command=self.save_command)
        filemenu.add_command(label="Share", command=self.share_command)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.exit_command)

        openmenu = Menu(menu)
        menu.add_cascade(label="Open...", menu=openmenu)
        openmenu.add_command(label="Open local file", command=self.open_command)
        openmenu.add_command(label="Open shared file", command=self.open_shared_command)

        getmenu = Menu(menu)
        menu.add_cascade(label="Get", menu=getmenu)
        getmenu.add_command(label = "Files on the server", command=self.getFileList)

        helpmenu = Menu(menu)
        menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About...", command=self.about_command)


    #Timer
    def timer(self):
        l = self.getLength()
        if(self.old_length == l and l !=0 and self.counter and self.getLines()[-1] != []):
            self.update()
            self.counter = False
        self.old_length = l
        threading.Timer(5, self.timer).start()

    def getLength(self):
        return len(self.textPad.get('1.0', END + '-1c'))

    def getLines(self):
        text = self.textPad.get('1.0', END + '-1c').encode("utf-8").split('\n')
        return [[j[i:i + self.textPadWidth] for i in range(0, len(j), self.textPadWidth)] for j in text]

    def update(self, *args):
        tosend = "".join(self.getLines()[-1])
       ## call sending method from client
        #print(tosend)
        self.client.send_short_message(tosend)

    def newline_check(self, *args):
        self.counter = True
        length = self.getLength()
        if (length+1) % self.textPadWidth == 0 and length != 0:
            self.linecount += 1
            self.update()

        elif int(length / self.textPadWidth) != self.linecount:
            self.linecount = int(length / self.textPadWidth)
            self.update()

    def getFileList(self):
        self.client.get_filelist()

    def new_command(self):
        self.textPad.delete('1.0', END)

    def open_command(self):
        file = tkFileDialog.askopenfile(parent=self.root, mode='rb', title='Select a file')
        if file != None:
            contents = file.read()
            self.textPad.insert('1.0', contents)
            file.close()

    def getpwd(self):
        root = Tk()
        userbox = Entry(root)
        pwdbox = Entry(root, show='*')

        def onpwdentry(evt):
            self.username = userbox.get()
            self.password = pwdbox.get()
            root.destroy()

        def onokclick():
            self.username = userbox.get()
            self.password = pwdbox.get()
            root.destroy()

        Label(root, text='Username and password').pack(side='top')
        #Label(root, text='Password').pack(side='middle')
        userbox.pack(side='top')
        pwdbox.pack(side='top')
        pwdbox.bind('<Return>', onpwdentry)
        Button(root, command=onokclick, text='OK').pack(side='bottom')

        root.mainloop()
        return self.username+','+self.password

    def save_command(self):
        file = tkFileDialog.asksaveasfile(mode='w')
        if file != None:
        # slice off the last character from get, as an extra return is added
            data = self.textPad.get('1.0', END+'-1c')
            file.write(data)
            file.close()

    def exit_command(self):
        if tkMessageBox.askokcancel("Quit", "Do you really want to quit?"):
            self.root.destroy()
            self.client.stop()

    def about_command(self):
        label = tkMessageBox.showinfo('Copyright (c) Anton Prokopov,\n Nikita Kirienko,\n Elmar Abbasov')

    def share_command(self):
        data = self.textPad.get('1.0', END + '-1c')
        self.client.send_long_message(data)
        print("sdfgh")

    def open_shared_command(self):
        print "Opening file on the server side.."