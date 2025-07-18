#include <stdlib.h>
#include <string.h>
#include "arduino.h"
class Parser
{
private: 
    int size_st; 
    char currPointer;
    bool state;
    int index;
    char terminator;
    int size;
public:
    char * data;
    char * st;
    char _numterminator,_numterminatorbuf;
    void init(char * header,char terminator,char numterminator,int sizeofdata=10)
    {
		//malloc data
        size=sizeofdata;
        data=(char*)malloc(size);
        _numterminator=numterminator;
        _numterminatorbuf=0;
        this->terminator=terminator;
		//malloc header
		size_st=strlen(header);
        st=(char*)malloc(size_st);
        strcpy(st,header);//strcpy_s(st,size_st,header);
        currPointer=0;
        state=false;
	}
    Parser(char * header,char terminator,char numterminator,int sizeofdata=10);
    Parser(char * header,char terminator);
    
    bool Poll(char x)
    {
        if(st[currPointer]==x)
            currPointer++;
        else
            currPointer=0;
        if(currPointer==size_st)
        {
            currPointer=0;
            return 1;
        }
        return 0;
    }
    bool DataReceived(char x)
    {
        if(Poll(x))
        {
            state=true;
            index=0;
            return false;
        }
        if(state)
        {
            if(x==terminator)
            {
                _numterminatorbuf++;
                if(_numterminator==_numterminatorbuf)
                {
                    _numterminatorbuf=0;
                    *(data+(index%size))=0;
                    state=false;
                    return true;
                }
            }
            *(data+(index%size))=x;
            index++;
        }
        return false;
    }
};

class mich
{
public:
    Parser donna;
    int y;
    mich(void):donna("$GPRMC,",'\r',1),y(200)
    {}
    
};
