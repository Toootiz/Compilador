# Gabriel Muñoz Luna - A01028774
# Analizador Léxico (Scanner) Optimizado para C-

from enum import Enum
from globalTypes import *

# Estados del autómata para C-
class StateType(Enum):
    START = 1
    INID = 2
    INNUM = 3
    INCOMMENT = 4
    INCOMMENT_END = 5
    INLESS = 6     # Para < o <=
    INGREATER = 7  # Para > o >=
    INEQUAL = 8    # Para = o ==
    INNOT = 9      # Para !=
    INDIV = 10     # Para / o inicio de comentario /*
    DONE = 11

# Variables globales compartidas
program = ""
position = 0
programLength = 0
lineno = 1

def recibeScanner(prog, pos, long):
    """Recibe los datos del archivo fuente desde el script principal."""
    global program, position, programLength, lineno
    program = prog
    position = pos
    programLength = long
    lineno = 1  # Reiniciar el contador de líneas en cada nueva ejecución

def reservedLookup(tokenString):
    """Busca si el identificador es una palabra reservada o un ID común."""
    return RESERVED_WORDS.get(tokenString, TokenType.ID)

def getToken(imprime=True):
    """Despacha el siguiente token válido del flujo del programa."""
    global position, lineno
    tokenString = ""
    currentToken = None
    state = StateType.START
    
    while state != StateType.DONE:
        # Verificar si llegamos al final del string del programa
        if position >= len(program):
            c = '\0' 
        else:
            c = program[position]
            
        save = True
        
        # --- ESTADO INICIAL ---
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
                if c == '\n': 
                    lineno += 1
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

        # --- ESTADO ASIGNACIÓN O IGUALDAD ---
        elif state == StateType.INEQUAL:
            state = StateType.DONE
            if c == '=':
                currentToken = TokenType.EQ # ==
            else:
                currentToken = TokenType.ASSIGN # =
                save = False
                position -= 1 # Retroceder un carácter para no perderlo

        # --- ESTADO MENOR O MENOR IGUAL ---
        elif state == StateType.INLESS:
            state = StateType.DONE
            if c == '=':
                currentToken = TokenType.LTE # <=
            else:
                currentToken = TokenType.LT # <
                save = False
                position -= 1

        # --- ESTADO MAYOR O MAYOR IGUAL ---
        elif state == StateType.INGREATER:
            state = StateType.DONE
            if c == '=':
                currentToken = TokenType.GTE # >=
            else:
                currentToken = TokenType.GT # >
                save = False
                position -= 1

        # --- ESTADO DIFERENTE (!=) ---
        elif state == StateType.INNOT:
            state = StateType.DONE
            if c == '=':
                currentToken = TokenType.DIFF # !=
            else:
                currentToken = TokenType.ERROR # Un '!' solo es un error en C-
                save = False
                position -= 1

        # --- ESTADO DIVISIÓN O COMENTARIO ---
        elif state == StateType.INDIV:
            if c == '*': # ¡Detectado inicio de bloque de comentario /*!
                save = False
                position += 1 # Consumir el '*' de manera inmediata
                
                # Bucle dedicado para devorar el comentario ignorando todo su contenido
                while position < len(program):
                    char_actual = program[position]
                    
                    if char_actual == '\n':
                        lineno += 1
                        
                    # Validar si encontramos la secuencia de cierre '*/'
                    if char_actual == '*' and (position + 1 < len(program)) and (program[position + 1] == '/'):
                        position += 2 # Consumir tanto el '*' como el '/'
                        break
                        
                    position += 1
                
                # REINICIO PURIFICADO: Volvemos al estado inicial y limpiamos el buffer
                state = StateType.START
                tokenString = ""
                continue # Saltamos directo al siguiente ciclo del while sin alterar punteros
            else: 
                state = StateType.DONE
                currentToken = TokenType.OVER # Es un operador de división común '/'
                save = False
                position -= 1

        # --- ESTADO NÚMEROS (NUM) ---
        elif state == StateType.INNUM:
            if not c.isdigit():
                save = False
                position -= 1
                state = StateType.DONE
                currentToken = TokenType.NUM

        # --- ESTADO IDENTIFICADORES (ID) ---
        elif state == StateType.INID:
            if not c.isalpha():
                save = False
                position -= 1
                state = StateType.DONE
                currentToken = TokenType.ID

        # --- ACTUALIZACIÓN DE BUFFER Y POSICIÓN ---
        if save:
            tokenString += c
        if state == StateType.DONE:
            if currentToken == TokenType.ID:
                currentToken = reservedLookup(tokenString)
        position += 1

    if imprime:
        print(f"{lineno}: {currentToken.name} = {tokenString}")
    return currentToken, tokenString, lineno