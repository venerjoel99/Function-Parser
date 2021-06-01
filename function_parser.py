#Parser for 2-D polynomial functions
import operator
import math
#Function tree
#  root node
#  members for x and y

#Tree node
#  left and right children
#  value (x, y, op, or number)
class Node:
    def __init__(self, value, left = None, right = None):
        self.__value = value
        self.__left = left
        self.__right = right
        
    def setVal(self, val):
        self.__value = val
        
    def setLeft(self, node):
        self.__left = node
        
    def setRight(self, node):
        self.__right = node
    
    def eval(self, x, y):
        val = self.__value
        valType = type(val)
        if valType == int or valType == float:
            return val
        elif val == 'x':
            return x
        elif val == 'y':
            return y
        else:
            leftResult = self.__left.eval(x,y)
            rightResult = self.__right.eval(x,y)
            operation = OPERATOR.getOperation(val)
            return operation(leftResult,rightResult)
            
class Function:
    def __init__(self, strVal):
        self.__strFunc = strVal
        tempParser = Parser(strVal)
        self.__root = tempParser.getRoot()
        
    def eval(self, x, y):
        return self.__root.eval(x,y)
            
class Type:    
    def __init__(self, type, valids = []):
        self.__type = type
        self.__valids = valids
    
    #Check if a char sequence would make a valid
    #token of this type
    def valid(self, charSeq):
        return charSeq in self.__valids
    
    def __str__(self):
        return self.__type
        
    def __repr__(self):
        return self.__str__()

#Derived class for integer type
class INT(Type):
    def __init__(self):
        Type.__init__(self, 'Int')

#Derived class for float type
class FLOAT(Type):
    def __init__(self):
        Type.__init__(self, 'Float')

#Derived class for id type             
class ID(Type):
    def __init__(self):
        Type.__init__(self, 'Id', ['x', 'y', 'z'])
        
class ASSIGNMENT(Type):
    def __init__(self):
        Type.__init__(self, 'Assignment', ['='])

#Derived class for operator type        
class OPERATOR(Type):
    def __realDiv(x,y):
        if y==0.0:
            if x < 0:
                return -math.inf
            else:
                return math.inf
        return x / y
		
	#Add special function calculator here for sin, cos, log
        
    __table = {
        '+' : operator.add,
        '-' : operator.sub,
        '*' : operator.mul,
        '/' : __realDiv,
        '^' : operator.pow
    }
    def __init__(self):
        Type.__init__(self, 'Operator', ['+', '-', '*', '/', '^'])
    def getOperation(opChar):
        return OPERATOR.__table[opChar]
        

class PARENTHESIS(Type):
    def __init__(self):
        Type.__init__(self, 'Parenthesis', ['(', ')'])
        
#Derived class for end-of-input type
class EOI(Type):
    def __init__(self):
        Type.__init__(self, 'EOI', ['$'])

#Derived class for invalid type        
class Invalid(Type):
    def __init__(self):
        Type.__init__(self, 'Invalid')

#Token class that stores a token type object
#and the value of the token        
class Token:
    def __init__(self, type, val):
        self.__type = type
        self.__val = val
        
    def getType(self):
        return self.__type
    
    def getVal(self):
        return self.__val
    
    def __str__(self):
        header = "<" + str(self.__type) + ">"
        footer = "</" + str(self.__type) + ">"
        return header + self.__val + footer
    
    def __repr__(self):
        return self.__str__()

#Class that performs lexical analysis
#by turning a character sequence to a token sequence        
class Lexer:
    def __init__(self, s):
        self.__s = s
        self.__len = len(s)
        self.__index = 0
        self.__eoi = False
        self.__singleCharTypes = [
            ASSIGNMENT(),
            OPERATOR(),
            PARENTHESIS(),
            EOI()
        ]
    
    #Get current char in stream    
    def __getCurrentChar(self):
        return self.__s[self.__index]
    
    #Is current character a letter?    
    def __isCharLetter(self):
        if self.__endStream():
            return False
        curChar = self.__getCurrentChar()
        return ('A' <= curChar <= 'Z') or ('a' <= curChar <= 'z')
    
    #Is current character a digit?
    def __isCharDigit(self):
        if self.__endStream():
            return False
        curChar = self.__getCurrentChar()
        return '0' <= curChar <= '9'
    
    #Is current character a space?    
    def __isCharSpace(self):
        return self.__getCurrentChar() == ' '
    
    #Did we reach the end of the character stream?
    def __endStream(self):
        return self.__index >= self.__len
    
    #Go to next character in the stream
    def __toNextChar(self):
        self.__index += 1
   
    #Get a sequence of digits
    def __getNumber(self):
        result = ''
        while (self.__isCharDigit()):
            result += self.__getCurrentChar()
            self.__toNextChar()
        return result
    
    #Get a sequence of letters and digits
    def __getAlphaNum(self):
        result = ''
        while (self.__isCharLetter() or self.__isCharDigit()):
            result += self.__getCurrentChar()
            self.__toNextChar()
        return result
        
    #Get next token from character stream
    def nextToken(self):
        while not self.__endStream():
            
            #Check if character is operator, comma, or EOI
            current = self.__getCurrentChar()
            for tokenType in self.__singleCharTypes:
                if tokenType.valid(current): 
                    if isinstance(tokenType, EOI):
                        self.__eoi = True
                    self.__toNextChar()
                    return Token(tokenType, current)
            
            #Get an integer or float if
            #character is a digit
            if self.__isCharDigit():
                leftDigits = self.__getNumber()
                current = self.__getCurrentChar()
                if (current == '.'):
                    leftDigits += current
                    self.__toNextChar()
                    if self.__isCharDigit():
                        rightDigits = self.__getNumber()
                        floatStr = leftDigits + rightDigits
                        return Token(FLOAT(), floatStr)
                    else:
                        return Token(Invalid(), leftDigits)
                else:
                    return Token(INT(), leftDigits)
            #Get an identifier or keyword
            #if character is a letter
            elif self.__isCharLetter():
                charSeq = self.__getCurrentChar()
                self.__toNextChar()
                return Token(ID(), charSeq)
            #Skip to next character if it is a space
            elif self.__isCharSpace():
                self.__toNextChar()
            #Mark the character as invalid if it doesn't match
            #any of the above
            else:
                current = self.__getCurrentChar()
                self.__toNextChar()
                return Token(Invalid(), current)
        #Make an invalid token if eoi is not reached by
        #the end of the character stream
        if not self.__eoi:
            return Token(Invalid(), '')
        else:
            return None

#Function parser for polynomials and exponentials
class Parser:
    #Take an inpuuted line and append $ for EOI
    def __init__(self, s):
        self.__lexer = Lexer(s + "$")
        self.__token = self.__lexer.nextToken()
        
    def __printXML(self, level, value, header):
        tail = ""
        if not header:
            tail += "/"
        print(('\t' * level) + "<" + tail + value + ">")
    
    #Store the next token outputted by the lexer into the private member
    def __getNextToken(self):
        self.__token = self.__lexer.nextToken()
        
    def __matchesVals(self, tokenType, values = []):
        if len(values) > 0:
            for val in values:
                if (self.__matches(tokenType, val)):
                    return True
            return False
        else:
            return self.__matches(tokenType)
            
    
    #Check if the current token matches the inputted token type
    #and if length of keyword > 0, then check if token is a keyword type
    #that matches the inputted keyword arg
    def __matches(self, tokenType, value = ""):
        validValue = True
        if (len(value) > 0):
            validValue = self.__token.getVal() == value
        return validValue and isinstance(self.__token.getType(), tokenType)
    
    #Print out the error by showing what type of token the parser was expecting
    #vs what it saw.  Then, exit so the parser doesn't keep parsing after syntax error.
    def __printError(self, tokenType):
        tokenTypeObj = tokenType()
        print("Syntax error: expecting " + str(tokenTypeObj) + "; saw " + str(self.__token.getType()) + '\n')
        exit()
    
    #Check if the token matches the type inputted and print it out if it does.
    #Otherwise, print the syntax error message and exit.  If keyword has length > 0
    #make sure the token matches the keyword inputted
    def __expectToken(self, level, tokenType, keyword = ""):
        if (self.__matches(tokenType, keyword)):
            self.__getNextToken()
        else:
            self.__printError(tokenType)
            
    def __getCurrentTokenVal(self, tokenType, keyword = ""):
        if (self.__matches(tokenType, keyword)):
            val = self.__token.getVal()
            self.__getNextToken()
            return val
        else:
            self.__printError(tokenType)
            return None
    
    #DONE
    def __expression(self):
        currentNode = self.__term()
        while self.__matchesVals(OPERATOR, ['+', '-']):
            newNode = Node(self.__getCurrentTokenVal(OPERATOR))
            newNode.setLeft(currentNode)
            newNode.setRight(self.__term())
            currentNode = newNode
        return currentNode
    
    def __term(self):
        currentNode = self.__factor()
        while not (self.__matchesVals(OPERATOR, ['+','-']) 
            or self.__matches(PARENTHESIS, ')') or self.__matches(EOI)):
            newNode = Node('*')
            if (self.__matches(OPERATOR)):
                newNode.setVal(self.__getCurrentTokenVal(OPERATOR))
            newNode.setLeft(currentNode)
            newNode.setRight(self.__factor())
            currentNode = newNode
        return currentNode
            
    def __factor(self):
        currentNode = self.__pow()
        if self.__matches(OPERATOR, "^"):
            newNode = Node(self.__getCurrentTokenVal(OPERATOR, '^'))
            newNode.setLeft(currentNode)
            newNode.setRight(self.__factor())
            currentNode = newNode
        return currentNode
        
    def __pow(self):
	
		#Add sin, cos, log function possibility here
	
        if self.__matches(PARENTHESIS, '('):
            self.__getCurrentTokenVal(PARENTHESIS, '(')
            node = self.__expression()
            self.__getCurrentTokenVal(PARENTHESIS, ')')
            return node
        else:
            return self.__value()
        
    def __value(self):
        if self.__matchesVals(ID, ['x', 'y']):            
            return Node(self.__getCurrentTokenVal(ID))
        elif self.__matches(FLOAT):
            floatVal = float(self.__getCurrentTokenVal(FLOAT))
            return Node(floatVal)
        else:
            intVal = int(self.__getCurrentTokenVal(INT))
            return Node(intVal)
            
    def getRoot(self):
        self.__getCurrentTokenVal(ID, 'z')
        self.__getCurrentTokenVal(ASSIGNMENT) 
        root = self.__expression()
        return root
            
a = Lexer("z=x^2+2y" + "$")
b = a.nextToken()
while not isinstance(b.getType(), EOI):
    print(b)
    b = a.nextToken()
    
c = Parser("z=3x^y^4-2y^3+3.2/(xy^7)")

#TODO:
  #Fix Lexer to parse sin, cos, log
  #Make new types for function strings sin, cos, log
  #Fix Parser to include new type of functions (in pow function)
  #Add evaluation option for functions
        