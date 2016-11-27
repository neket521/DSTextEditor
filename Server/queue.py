class Queue: # also history

    def __init__(self):
        self.__counter = 0
        self.__msgs = []

    def reinit(self):
        print 'reinit called'
        if len(self.__msgs) > 0:
            self.write_to_file()
            self.__counter = 0
            self.__msgs = []

    def add(self, tuple):
        if len(self.__msgs) == 25:
            self.__msgs.pop(0)
        if self.__counter == 25:
            self.__counter = 0
            self.write_to_file()
        self.__msgs.append(tuple)
        self.__counter += 1

    def get_messages(self):
        msgs = []
        if len(self.__msgs) > 0:
            msgs = [m for m in self.__msgs]
        return msgs

    def sort_queue(self):
        # sort by line number
        return sorted(self.__msgs, key=lambda x: x[4])

    def write_to_file(self):
        self.sort_queue()
        data = []
        with open('Server/UserFiles/' + self.__msgs[0][3], 'r') as f:
            for line in f:
                data.append(line)
        with open('Server/UserFiles/' + self.__msgs[0][3], 'w') as f:
            for msg in self.__msgs:
                if len(data) >= msg[4]:
                    data[msg[4]-1] = msg[5]
                else:
                    data.append(msg[5])
            f.writelines(data)