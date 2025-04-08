class node:
    def __init__(self,data):
        self.data=data
        self.next=None
class port:
    def __init__(self):
        self.head=None
    def end(self, data):
        nn=node(data)
        temp=self.head
        while temp.next:
            temp=temp.next
        temp.next=nn
    def display(self):
        if self.head==None:
            print("Empty")
        temp=self.head
        while temp:
            print(temp.data,end="-->")
            temp=temp.next

c=port()
n1=node(10)
c.head=n1
n2=node(20)
n1.next=n2
n3=node(30)
n2.next=n3
c.end(40)
c.display()
       