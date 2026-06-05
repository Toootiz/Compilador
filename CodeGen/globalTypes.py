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

# --- NUEVAS DEFINICIONES PARA EL ÁRBOL (AST) ---

class NodeKind(Enum):
    StmtK = 1  # Nodo de tipo Sentencia
    ExpK = 2   # Nodo de tipo Expresión

class StmtKind(Enum):
    IfK = 1
    WhileK = 2
    AssignK = 3
    ReturnK = 4
    VarK = 5   # Declaración de Variable
    FunK = 6   # Declaración de Función
    CompoundK = 7 # Bloque { ... }

class ExpKind(Enum):
    OpK = 1    # Operación (+, -, <, etc)
    ConstK = 2 # Números
    IdK = 3    # Identificadores (variables)

class ExpType(Enum):
    Void = 1
    Integer = 2
    Boolean = 3

MAXCHILDREN = 3

class TreeNode:
    def __init__(self):
        self.child = [None] * MAXCHILDREN
        self.sibling = None
        self.lineno = 0
        self.nodekind = None # StmtK o ExpK
        self.kind = None     # IfK, OpK, etc.
        self.op = None       # Para OpK
        self.val = None      # Para ConstK
        self.name = None     # Para IdK, VarK, FunK
        self.type = None     # Para declaraciones (int/void)