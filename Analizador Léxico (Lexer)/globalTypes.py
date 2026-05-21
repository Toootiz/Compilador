from enum import Enum

class TokenType(Enum):
    ENDFILE = 1
    ERROR = 2

    #Palabras reservadas
    IF = 'if'
    ELSE = 'else'
    INT = 'int'
    RETURN = 'return'
    VOID = 'void'
    WHILE = 'while'

    #tokens multicaracter
    ID = 3
    NUM = 4

    #simbolos especiales
    PLUS = '+'
    MINUS = '-'
    TIMES = '*'
    OVER = '/'
    LT = '<'
    LTE = '<='
    GT = '>'
    GTE = '>='
    EQ = '=='
    DIFF = '!='
    ASSIGN = '=' 
    SEMI = ';'
    COMMA = ','
    LPAREN = '('
    RPAREN = ')'
    LBRACKET = '['
    RBRACKET = ']'
    LBRACE = '{'
    RBRACE = '}'

    COMMENT = 5

RESERVED_WORDS = {
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "int": TokenType.INT,
    "return": TokenType.RETURN,
    "void": TokenType.VOID,
    "while": TokenType.WHILE
}