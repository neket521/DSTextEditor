import os

class Queue: # also history

    def __init__(self):
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
        dir = os.path.dirname(__file__)
        rel_path = 'UserFiles/'+self.__msgs[0][3]
        path = os.path.join(dir, rel_path)
        f = open(path, 'rw')
        data = f.readlines()
        for msg in self.__msgs:
            data[msg[4]] = msg[5]
        f.writelines(data)
        f.close()