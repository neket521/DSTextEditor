from Tkinter import *
from ScrolledText import *
import tkFileDialog
import tkMessageBox
import threading
import Tkinter

class UI(threading.Thread):

    def __init__(self, client):
        self.client = client
        threading.Thread.__init__(self)


    def init(self, file_content):
        self.root = Tkinter.Tk(className=" Awesome distributed text editor")
        self.textPadWidth = 80
        self.textPad = ScrolledText(self.root, width=self.textPadWidth, height=20)
        self.length = 0
        self.linecount = 0
        self.old_length = -1
        self.counter = True
        self.username = None
        self.password = None
        self.sharewith = None
        self.filename = None
        self.init_menu()
        self.update()
        self.textPad.bind("<Key>", self.newline_check)
        self.textPad.bind("<KeyRelease>", self.put_message)
        self.textPad.bind("<Return>", self.send_position)
        self.textPad.pack()
        self.textPad.insert('1.0', file_content)

    def run(self):
        self.root.mainloop()

    def init_menu(self):
        menu = Menu(self.root)
        self.root.config(menu=menu)
        filemenu = Menu(menu)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Save", command=self.save_command)
        filemenu.add_command(label="Open", command=self.open_command)
        filemenu.add_command(label="Share", command=self.share_command)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.exit_command)
        helpmenu = Menu(menu)
        menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About...", command=self.about_command)

    def update(self, *args):
        print("update")
        l = self.getLength()
        if (self.old_length == l and l != 0 and self.counter and self.getLines()[-1] != []):
            #self.send_position()
            self.counter = False
        self.old_length = l
        self.root.after(5000, self.update)

    def getLength(self):
        return len(self.textPad.get('1.0', END + '-1c'))

    def get_cursor_pos(self):
        return self.textPad.index(INSERT)

    def getLines(self):
        text = self.textPad.get('1.0', END + '-1c').encode("utf-8").split('\n')
        return [text[i:i + self.textPadWidth] for i in range(0, len(text), self.textPadWidth)]


    def update(self, *args):
        tosend = "".join(self.getLines()[-1])
        self.client.send_short_message(tosend)

    def send_position(self, *args):
        self.client.send_position(self.get_cursor_pos().split(".")[0])
        self.update()

    def newline_check(self, *args):
        self.counter = True
        length = self.getLength()
        if length % self.textPadWidth == 0 and length != 0:
            self.textPad.insert(END, '\n')
            #self.linecount += 1
            self.send_position()

        #elif int(length / self.textPadWidth) != self.linecount:
        #    self.linecount = int(length / self.textPadWidth)
        #    self.update()

    def getFileList(self):
        self.client.get_filelist()

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
        userbox.pack(side='top')
        pwdbox.pack(side='top')
        pwdbox.bind('<Return>', onpwdentry)
        Button(root, command=onokclick, text='OK').pack(side='bottom')
        root.mainloop()
        return self.username+','+self.password

    def show_files(self, msg):
        root = Tk()
        w = Label(root, text=msg)
        w.pack()
        root.mainloop()

    def open_command(self):
        self.root.destroy()
        self.getFileList()

    def save_command(self):
        file = tkFileDialog.asksaveasfile(mode='w')
        if file != None:
        # slice off the last character from get, as an extra return is added
            data = self.textPad.get('1.0', END+'-1c')
            file.write(data)
            file.close()

    def put_message(self,*args):
        if self.client.message != None:
            print(self.client.message)
            self.textPad.insert(END, self.client.message)

    def put_coursor(self,*args):
        if self.textPad.index(INSERT).split('.')[1] != self.client.line:
            self.textpad.mark_set("insert", "%d.%d" % (0, self.client.line))

    def exit_command(self):
        if tkMessageBox.askokcancel("Quit", "Do you really want to quit?"):
            self.root.destroy()
            self.client.stop()

    def about_command(self):
        label = tkMessageBox.showinfo('Copyright (c) Anton Prokopov, Nikita Kirienko, Elmar Abbasov')


    def on_filelist_received(self, filelist):
        #filelist contains coma-separated file names to which current user has access
        root = Tk()
        filenamebox = Entry(root)
        def onpwdentry(evt):
            if filenamebox.get() != '':
                self.newfilename = filenamebox.get()
                root.destroy()

        def onclick(name):
            self.newfilename = name
            root.destroy()

        Label(root, text='Choose file to edit or enter new filename').pack(side='top')
        for filename in filelist.split(','):
            if filename != '':
                name = str(filename)
                button = Button(master=root, command=lambda i=name: onclick(i), text=name)
                button.pack(side='top')

        filenamebox.pack(side='bottom')
        filenamebox.bind('<Return>', onpwdentry)
        root.mainloop()
        #print self.newfilename
        self.client.send_filename(self.newfilename)

    def share_command(self):
        # filelist contains coma-separated file names to which current user has access
        root = Tk()
        filenamebox = Entry(root)

        def onpwdentry(evt):
            if filenamebox.get() != '':
                self.sharewith = filenamebox.get()
                root.destroy()

        def onclick():
            self.sharewith = filenamebox.get()
            root.destroy()

        Label(root, text='Enter user name to share file with').pack(side='top')
        button = Button(master=root, command=onclick, text="OK")
        button.pack(side='bottom')

        filenamebox.pack(side='top')
        filenamebox.bind('<Return>', onpwdentry)
        root.mainloop()
        # print self.newfilename
        self.client.share_file(self.newfilename + "," + self.sharewith)
