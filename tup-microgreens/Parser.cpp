#include "Parser.h"
#include "stdlib.h"
Parser::Parser(char * header,char terminator,char numterminator,int sizeofdata)
{
	init(header,terminator,numterminator,sizeofdata);
}
Parser::Parser(char * header,char terminator)
{
    init(header,terminator,1,10);
}