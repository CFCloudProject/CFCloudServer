# define operation
class Operation(object):

    def __init__(self, type, index = None, data = None):
        if index is None and data is None:
            i = re.compile('\d+').search(type).group()
            self.index = int(i)
            self.type = type[len(i)]
            d = type[len(i)+1:len(type)]
            if self.type == 'd':
                self.data = int(d)
            else:
                self.data = d
        else:
            self.type = type
            self.index = index
            self.data = data

    def __str__(self):
        return '{}{}{}'.format(self.index, self.type, self.data)