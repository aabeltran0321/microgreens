class Parser():
    def __init__(self,_header,_terminator,numterminator,_sizeofdata=10):
        self.size=_sizeofdata
        self._numterminator=numterminator
        self._numterminatorbuf=0
        self.terminator=_terminator
        self.st=_header
        self.currPointer=0
        self.state=False
        self.size_st=len(_header);
    def Poll(self,x):
        if(self.st[self.currPointer]==x):
            self.currPointer=self.currPointer+1
        else:
            self.currPointer=0;
        if(self.currPointer==self.size_st):
            self.currPointer=0
            return True
        return False
    def available(self,x):
        if(self.Poll(x)==True):
            self.state=True
            #self.index=0
            self.data=""
            return False
        if(self.state):
            if(x==self.terminator or self.terminator==''):
                self._numterminatorbuf=self._numterminatorbuf+1
                if(self._numterminator==self._numterminatorbuf):
                    self._numterminatorbuf=0
                    #*(data+(index%size))=0;
                    self.state=False;
                    return True
            self.data=self.data+x
                #self.index++
        return False