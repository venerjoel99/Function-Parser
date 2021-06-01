#Parser for 2-D polynomial functions

#Function tree
#  root node
#  members for x and y

#Tree node
#  left and right children
#  value (x, y, op, or number)

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
    def __init__(self):
        Type.__init__(self, 'Operator', ['+', '-', '*', '/', '^'])

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

#SQL SELECT command parser class
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
    def __checkAndPrintToken(self, level, tokenType, keyword = ""):
        if (self.__matches(tokenType, keyword)):
            print(('\t' * level) + str(self.__token))
            self.__getNextToken()
        else:
            self.__printError(tokenType)
            
    def __expression(self, level):
        self.__printXML(level, "Expression", True)
        self.__term(level + 1)
        while self.__matchesVals(OPERATOR, ['+', '-']):
            self.__checkAndPrintToken(level + 1, OPERATOR)
            self.__term(level + 1)
        self.__printXML(level, "Expression", False)
            
    def __term(self, level):
        self.__printXML(level, "Term", True)
        self.__factor(level + 1)
        while not (self.__matchesVals(OPERATOR, ['+','-']) 
            or self.__matches(PARENTHESIS) or self.__matches(EOI)):
            if (self.__matches(OPERATOR)):
                self.__checkAndPrintToken(level + 1, OPERATOR)
            self.__factor(level + 1)
        self.__printXML(level, "Term", False)
            
    def __factor(self, level):
        self.__printXML(level, "Factor", True)
        self.__pow(level + 1)
        if self.__matches(OPERATOR, "^"):
            self.__checkAndPrintToken(level + 1, OPERATOR)
            self.__factor(level + 1)
        self.__printXML(level, "Factor", False)
        
    def __pow(self, level):
        self.__printXML(level, "Power", True)
        if self.__matches(PARENTHESIS, '('):
            self.__checkAndPrintToken(level + 1, PARENTHESIS)
            self.__expression(level + 1)
            self.__checkAndPrintToken(level + 1, PARENTHESIS)
        else:
            self.__value(level + 1)
        self.__printXML(level, "Power", False)
        
    def __value(self, level):
        self.__printXML(level, "Value", True)
        if self.__matchesVals(ID, ['x', 'y']):            
            self.__checkAndPrintToken(level + 1, ID)
        elif self.__matches(FLOAT):
            self.__checkAndPrintToken(level + 1, FLOAT)
        else:
            self.__checkAndPrintToken(level + 1, INT)
        self.__printXML(level, "Value", False)
            
    
    #Print out SQL command line into an abstract syntax tree
    #in XML format
    def run(self):
        print("<Function>")
        self.__checkAndPrintToken(1, ID, 'z')
        self.__checkAndPrintToken(1, ASSIGNMENT) 
        self.__expression(1)
        if (self.__matches(EOI)):
            print("</Function>")
        else:
            self.__printError(EOI)
            
a = Lexer("z=x^2+2y" + "$")
b = a.nextToken()
while not isinstance(b.getType(), EOI):
    print(b)
    b = a.nextToken()
    
c = Parser("z=3x^y^4-2y^3+3.2/(xy^7)")
c.run()
        