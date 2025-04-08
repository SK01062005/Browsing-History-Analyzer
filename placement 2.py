class node:
    def __init__(self,data):
        self.data=data
        self.next=None

class code:
    def __init__(self):
        self.head=None
    def start(self,data):
        nn=node(data)
        nn.next=self.head
        self.head=nn
    def display(self):
        if self.head==None:
           print("Empty")
        temp=self.head
        while temp:
            print(temp.data,end="-->")
            temp=temp.next


c=code()
n1=node(20)
c.head=n1
n2=node(30)
n1.next=n2
c.start(10)
c.display()