from globalTypes import *
def recibeScanner(prog, pos, long):
    global program, position, programLength
    program = prog
    position = pos
    programLength = long
# Estados del autómata para C-
class StateType(Enum):
    START = 1
    INID = 2
    INNUM = 3
    INCOMMENT = 4
    INCOMMENT_END = 5 # Para detectar el */
    INLESS = 6    # Para < o <=
    INGREATER = 7 # Para > o >=
    INEQUAL = 8   # Para = o ==
    INNOT = 9     # Para !=
    INDIV = 10    # Para / o inicio de comentario /*
    DONE = 11

program = ""
position = 0
programLength = 0
lineno = 1

def recibeScanner(prog, pos, long):
    global program, position, programLength
    program = prog
    position = pos
    programLength = long

def reservedLookup(tokenString):
    return RESERVED_WORDS.get(tokenString, TokenType.ID)

def getToken(imprime=True):
    global position, lineno
    tokenString = ""
    currentToken = None
    state = StateType.START
    
    while state != StateType.DONE:
        if position >= len(program):
            c = '\0' 
        else:
            c = program[position]
            
        save = True
        
        if state == StateType.START:
            if c.isdigit():
                state = StateType.INNUM
            elif c.isalpha():
                state = StateType.INID
            elif c == '=':
                state = StateType.INEQUAL
            elif c == '<':
                state = StateType.INLESS
            elif c == '>':
                state = StateType.INGREATER
            elif c == '!':
                state = StateType.INNOT
            elif c == '/':
                state = StateType.INDIV
            elif c in [' ', '\t', '\r', '\n']:
                save = False
                if c == '\n': lineno += 1
            else:
                state = StateType.DONE
                if c == '\0' or c == '$': 
                    save = False
                    currentToken = TokenType.ENDFILE
                elif c == '+': currentToken = TokenType.PLUS
                elif c == '-': currentToken = TokenType.MINUS
                elif c == '*': currentToken = TokenType.TIMES
                elif c == '(': currentToken = TokenType.LPAREN
                elif c == ')': currentToken = TokenType.RPAREN
                elif c == '[': currentToken = TokenType.LBRACKET
                elif c == ']': currentToken = TokenType.RBRACKET
                elif c == '{': currentToken = TokenType.LBRACE
                elif c == '}': currentToken = TokenType.RBRACE
                elif c == ';': currentToken = TokenType.SEMI
                elif c == ',': currentToken = TokenType.COMMA
                else: currentToken = TokenType.ERROR

        elif state == StateType.INEQUAL:
            state = StateType.DONE
            if c == '=':
                currentToken = TokenType.EQ # ==
            else:
                currentToken = TokenType.ASSIGN # =
                save = False
                position -= 1 # Retroceder

        elif state == StateType.INDIV:
            if c == '*': # Es inicio de comentario /*
                save = False
                state = StateType.INCOMMENT
                tokenString = "" 
            else: #
                state = StateType.DONE
                currentToken = TokenType.OVER
                save = False
                position -= 1

        elif state == StateType.INCOMMENT:
            save = False
            if c == '*': state = StateType.INCOMMENT_END
            elif c == '\n': lineno += 1
            elif c == '\0': 
                state = StateType.DONE
                currentToken = TokenType.ENDFILE

        elif state == StateType.INCOMMENT_END:
            save = False
            if c == '/': state = StateType.START
            elif c == '*': state = StateType.INCOMMENT_END
            else: state = StateType.INCOMMENT

        elif state == StateType.INNUM:
            if not c.isdigit():
                save = False
                position -= 1
                state = StateType.DONE
                currentToken = TokenType.NUM

        elif state == StateType.INID:
            if not c.isalpha():
                save = False
                position -= 1
                state = StateType.DONE
                currentToken = TokenType.ID

        if save:
            tokenString += c
        if state == StateType.DONE:
            if currentToken == TokenType.ID:
                currentToken = reservedLookup(tokenString)
        position += 1

    if imprime:
        print(f"{lineno}: {currentToken.name} = {tokenString}")
    return currentToken, tokenString, lineno