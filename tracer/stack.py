class Stack:
    
    def __init__(self):
        self.__stack = []
        return

    def push(self, value):
        self.__stack.append(value)
        return

    def pop(self):
        assert(len(self.__stack) > 0)
        return self.__stack.pop()

    def peek(self):
        assert(len(self.__stack) > 0)
        return self.__stack[len(self.__stack) - 1]

    def __contains__(self, item):
        return item in self.__stack

    def __len__(self):
        return len(self.__stack)

    def __getitem__(self, index):
        return self.__stack[index]

    def __iter__(self):
        return self.__stack.__iter__()

    def __repr__(self):
        return self.__stack.__repr__()

    def __str__(self):
        return self.__stack.__str__()

