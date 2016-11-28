from Tkinter import *
from ScrolledText import *
import tkFileDialog
import tkMessageBox
import Tkinter
import threading

class UI(threading.Thread):

    username = None
    password = None
    filename = None
    sharewith = None

    def __init__(self, client):
        self.client = client
        threading.Thread.__init__(self)

    def init(self, file_content):
        self.f_content = file_content
        self.start()

    def run(self):
        self.root = Tkinter.Tk(className=" Awesome distributed text editor")
        self.textPadWidth = 80
        self.textPad = ScrolledText(self.root, width=82, height=20)
        self.length = 0
        self.old_length = -1
        self.counter = True
        self.init_menu()
        self.textPad.bind("<Key>", self.newline_check)
        #self.textPad.bind("<KeyRelease>", self.put_message)
        self.textPad.pack()
        self.textPad.insert('1.0', self.f_content)
        self.line_number = 1
        self.old_line_number = -1
        self.old_message = ""
        self.sent_message = ""

        def send():
            l = self.get_cursor_pos().split('.')[1]
            if self.old_length == l and l != 0 and self.counter:
                self.send_message(0)
                self.counter = False
            self.old_length = l
            self.root.after(5000, send)

        self.root.after(5000, send)

        def get_line():
            self.line_number = self.get_cursor_pos().split('.')[0]
            if self.line_number != self.old_line_number:
                self.send_position()
                self.old_line_number = self.line_number
            self.root.after(20, get_line)

        self.root.after(20, get_line)


        def get_msges():
            self.put_message()
            self.root.after(10, get_msges)
        self.root.after(10, get_msges)
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

    def getLength(self):
        return len(self.textPad.get('1.0', END + '-1c'))

    def get_cursor_pos(self):
        return self.textPad.index(INSERT)

    def send_message(self, line,*args):
        if self.get_cursor_pos().split('.')[1] != '0':
            tosend = self.textPad.get(str(int(self.get_cursor_pos().split('.')[0])-line) + '.0', END + '-1c')
            self.sent_message = tosend
            self.client.send_short_message(tosend)

    def send_position(self, *args):
        self.client.send_position(self.get_cursor_pos().split(".")[0])

    def newline_check(self, event,*args):
        if event.keysym == "Return":
            self.send_message(0)
        self.counter = True
        if self.get_cursor_pos().split('.')[1] == str(self.textPadWidth+1):
            self.send_message(0)
            self.textPad.insert(END, '\n')

    def getFileList(self):
        self.client.get_filelist()

    def getpwd(self):
        root = Tk()
        userbox = Entry(root)
        pwdbox = Entry(root, show='*')

        def onpwdentry(evt):
            UI.username = userbox.get()
            UI.password = pwdbox.get()
            root.destroy()

        def onokclick():
            UI.username = userbox.get()
            UI.password = pwdbox.get()
            root.destroy()

        Label(root, text='Username and password').pack(side='top')
        userbox.pack(side='top')
        pwdbox.pack(side='top')
        pwdbox.bind('<Return>', onpwdentry)
        Button(root, command=onokclick, text='OK').pack(side='bottom')
        root.mainloop()
        return UI.username+','+UI.password

    def show_files(self, msg):
        root = Tk()
        w = Label(root, text=msg)
        w.pack()
        root.mainloop()

    def open_command(self):
        self.send_message(0)
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
        if self.client.message != None and self.client.message != self.old_message:
            while int(self.client.message.split(",")[0]) > int(self.textPad.index('end-1c').split('.')[0]):
                self.textPad.insert(END,'\n')
            self.textPad.insert(self.client.message.split(",")[0] + ".0", self.client.message.split(",")[1])
            self.old_message = self.client.message


    def put_coursor(self,*args):
        if self.textPad.index(INSERT).split('.')[1] != self.client.line:
            self.textPad.mark_set("insert", "%d.%d" % (0, self.client.line))

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
                UI.filename = filenamebox.get()
                root.destroy()

        def onclick(name):
            UI.filename = name
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
        self.client.get_file_by_filename(UI.filename)

    def share_command(self):
        root = Tk(className="Share")
        filenamebox = Entry(root)

        def onpwdentry(evt):
            if filenamebox.get() != '':
                UI.sharewith = filenamebox.get()
                root.destroy()

        def onclick():
            UI.sharewith = filenamebox.get()
            root.destroy()

        Label(root, text="Enter user name to share file with. \n To share with multiple users, list those users coma-separated (no spaces)").pack(side='top')
        button = Button(master=root, command=onclick, text="OK")
        button.pack(side='bottom')

        filenamebox.pack(side='top')
        filenamebox.bind('<Return>', onpwdentry)
        root.mainloop()
        self.client.share_file(UI.filename + ":" + UI.sharewith)
