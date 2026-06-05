#Gabriel Muñoz Luna - A01028774
#Proyecto 2 Analizador Sintáctico

# Imports de los otros scripts
from globalTypes import *
from lexer import *
from scanner import *

token = None
tokenString = ""
lineno = 1
Error = False

# Tokens para recuperación de errores (Botón de Pánico)
FOLLOW_SET = [
    TokenType.SEMI, 
    TokenType.RBRACE, 
    TokenType.INT,  
    TokenType.VOID, 
    TokenType.ENDFILE
]

programa = ""
posicion = 0
progLong = 0

def globales(prog, pos, long):
    global programa, posicion, progLong
    programa = prog
    posicion = pos
    progLong = long
    recibeScanner(prog, pos, long) 

def syntaxError(message):
    global Error
    Error = True
    print(f"\nLínea {lineno}: {message}")
    
    lineas_codigo = programa.split('\n')
    if 0 < lineno <= len(lineas_codigo):
        linea_actual = lineas_codigo[lineno-1]
        print(linea_actual)
        
        # BUSQUEDA DINÁMICA DEL TOKEN:
        try:
            columna = linea_actual.find(tokenString)
            if columna == -1:
                columna = posicion % (len(linea_actual) + 1)
        except:
            columna = 0
            
        print(" " * columna + "^")

def match(expected):
    global token, tokenString, lineno
    if token == expected:
        token, tokenString, lineno = getToken(False)
    else:
        syntaxError(f"Error de sintaxis: se esperaba {expected} pero se encontró '{tokenString}'")
        
        # MODO BOTÓN DE PÁNICO
        while token not in FOLLOW_SET and token != TokenType.ENDFILE:
            token, tokenString, lineno = getToken(False)
     
        if token == TokenType.SEMI:
            token, tokenString, lineno = getToken(False)
    

# FUNCIONES DEL PARSER 
def params():
    if token == TokenType.VOID:
        match(TokenType.VOID)
        if token == TokenType.RPAREN:
            return None
        t = newStmtNode(StmtKind.VarK)
        t.name = "void"
        t.type = TokenType.VOID
        if token == TokenType.ID:
            return param_list(t)
        return t
    else:
        return param_list()

def param_list(first_param=None):
    # param-list -> param { , param }
    if first_param:
        t = first_param
    else:
        t = param()
    p = t
    while token == TokenType.COMMA:
        match(TokenType.COMMA)
        q = param()
        if q:
            if t is None:
                t = p = q
            else:
                p.sibling = q
                p = q
    return t

def param():
    t = newStmtNode(StmtKind.VarK)
    t.type = token # INT o VOID
    match(token)
    
    t.name = tokenString
    match(TokenType.ID)
    
    if token == TokenType.LBRACKET: 
        match(TokenType.LBRACKET)
        match(TokenType.RBRACKET)
        t.is_array = True
    return t

def statement_list():
    # pueden empezar con IF, RETURN, WHILE, '{', ID o ';'
    t = None
    p = None
    sentencias_start = [
        TokenType.IF, TokenType.RETURN, TokenType.WHILE, 
        TokenType.LBRACE, TokenType.ID, TokenType.SEMI
    ]

    while token in sentencias_start:
        q = statement()
        if q is not None:
            if t is None:
                t = p = q
            else:
                p.sibling = q
                p = q
    return t

def statement():
    if token == TokenType.IF:
        return selection_stmt() 
    elif token == TokenType.WHILE:
        return iteration_stmt()
    elif token == TokenType.RETURN:
        return return_stmt()
    elif token == TokenType.LBRACE:
        return compound_stmt()
    else:
        return expression_stmt()

def return_stmt():
    t = newStmtNode(StmtKind.ReturnK)
    match(TokenType.RETURN)
    if token != TokenType.SEMI:
        t.child[0] = expression()
    match(TokenType.SEMI)
    return t

def selection_stmt():
    t = newStmtNode(StmtKind.IfK)
    match(TokenType.IF)
    match(TokenType.LPAREN)
    t.child[0] = expression()
    match(TokenType.RPAREN)
    t.child[1] = statement()
    if token == TokenType.ELSE:
        match(TokenType.ELSE)
        t.child[2] = statement()
    return t

def iteration_stmt():
    t = newStmtNode(StmtKind.WhileK)
    match(TokenType.WHILE)
    match(TokenType.LPAREN)
    t.child[0] = expression()
    match(TokenType.RPAREN)
    t.child[1] = statement()
    return t

def expression_stmt():
    t = None
    if token != TokenType.SEMI:
        t = expression()
    match(TokenType.SEMI)
    return t

def compound_stmt():
    t = newStmtNode(StmtKind.CompoundK)
    match(TokenType.LBRACE)
    t.child[0] = local_declarations()
    t.child[1] = statement_list()
    match(TokenType.RBRACE)
    return t

def local_declarations():
    t = None
    p = None
    while token in [TokenType.INT, TokenType.VOID]:
        q = var_declaration()
        if q:
            if t is None: t = p = q
            else:
                p.sibling = q
                p = q
    return t

def var_declaration():
    t = newStmtNode(StmtKind.VarK)
    t.type = token 
    match(token)
    t.name = tokenString
    match(TokenType.ID)
    if token == TokenType.LBRACKET:
        match(TokenType.LBRACKET)
        match(TokenType.NUM) 
        match(TokenType.RBRACKET)
    match(TokenType.SEMI)
    return t

def program():
    return declaration_list()

def declaration_list():
    global token, tokenString, lineno 
    
    t = declaration()
    p = t
    
    while token != TokenType.ENDFILE:
        if Error and token not in [TokenType.INT, TokenType.VOID]:
            token, tokenString, lineno = getToken(False)
            continue
            
        q = declaration()
        if q:
            if t is None:
                t = p = q
            else:
                p.sibling = q
                p = q
        elif token != TokenType.ENDFILE:
            token, tokenString, lineno = getToken(False)
            
    return t

def declaration():
    t = None
    tipo = token
    match(token)
    
    nombre = tokenString
    match(TokenType.ID)
    
    if token == TokenType.LPAREN: # Es función
        t = newStmtNode(StmtKind.FunK)
        t.name = nombre
        t.type = tipo
        match(TokenType.LPAREN)
        t.child[0] = params()
        match(TokenType.RPAREN)
        t.child[1] = compound_stmt()
    else: # Es variable
        t = newStmtNode(StmtKind.VarK)
        t.name = nombre
        t.type = tipo
        if token == TokenType.LBRACKET:
            match(TokenType.LBRACKET)
            t.child[0] = newExpNode(ExpKind.ConstK)
            t.child[0].val = int(tokenString)
            match(TokenType.NUM)
            match(TokenType.RBRACKET)
        match(TokenType.SEMI)
    return t

def expression():
    t = simple_expression()
    
    if token == TokenType.ASSIGN:
        p = newExpNode(ExpKind.OpK)
        p.op = TokenType.ASSIGN
        p.child[0] = t 
        match(TokenType.ASSIGN)
        p.child[1] = expression()
        t = p
    return t

def simple_expression():
    t = additive_expression()
    relops = [
        TokenType.LTE, TokenType.LT, TokenType.GT, 
        TokenType.GTE, TokenType.EQ, TokenType.DIFF
    ]
    
    if token in relops:
        p = newExpNode(ExpKind.OpK)
        p.child[0] = t
        p.op = token
        match(token)
        p.child[1] = additive_expression()
        t = p
    return t

def additive_expression():
    t = term()
    while token in [TokenType.PLUS, TokenType.MINUS]:
        p = newExpNode(ExpKind.OpK)
        p.child[0] = t
        p.op = token
        match(token)
        p.child[1] = term()
        t = p
    return t

def term():
    t = factor()
    while token in [TokenType.TIMES, TokenType.OVER]:
        p = newExpNode(ExpKind.OpK)
        p.child[0] = t
        p.op = token
        match(token)
        p.child[1] = factor()
        t = p
    return t

def factor():
    global token, tokenString, lineno
    t = None
    if token == TokenType.NUM:
        t = newExpNode(ExpKind.ConstK)
        t.val = int(tokenString)
        match(TokenType.NUM)
    elif token == TokenType.LPAREN:
        match(TokenType.LPAREN)
        t = expression()
        match(TokenType.RPAREN)
    elif token == TokenType.ID:
        nombre_id = tokenString
        linea_id = lineno 
        match(TokenType.ID)
        
        t = newExpNode(ExpKind.IdK)
        t.name = nombre_id
        t.lineno = linea_id
        
        if token == TokenType.LPAREN: 
            match(TokenType.LPAREN)
            t.child[0] = args() 
            match(TokenType.RPAREN)
        
        elif token == TokenType.LBRACKET:
            match(TokenType.LBRACKET)
            t.child[0] = expression()
            match(TokenType.RBRACKET)  
    return t

def args():
    if token == TokenType.RPAREN:
        return None
    return arg_list()

def arg_list():
    t = expression()
    p = t
    while token == TokenType.COMMA:
        match(TokenType.COMMA)
        q = expression()
        if q:
            p.sibling = q
            p = q
    return t

def parser(imprime=True): 
    global token, tokenString, lineno, Error
    
    token, tokenString, lineno = getToken(False)
    
    ast = declaration_list()
    
    if token != TokenType.ENDFILE:
        syntaxError("El código no se analizó por completo hasta el EOF")
    
    if imprime and ast:
        printTree(ast)
        
    return ast

#Arbol

def newStmtNode(kind):
    t = TreeNode()
    t.nodekind = NodeKind.StmtK
    t.kind = kind 
    t.lineno = lineno
    return t

def newExpNode(kind):
    t = TreeNode()
    t.nodekind = NodeKind.ExpK
    t.kind = kind
    t.lineno = lineno
    return t


indentno = 0

def printSpaces():
    print("  " * indentno, end="")

def printTree(tree):
    global indentno
    if tree is None:
        return

    indentno += 1 
    
    while tree is not None:
        printSpaces()
        if tree.nodekind == NodeKind.StmtK:
            if tree.kind in [StmtKind.FunK, StmtKind.VarK]:
                # Usamos una validación segura para el tipo
                tipo_str = tree.type.value if hasattr(tree.type, 'value') else str(tree.type)
                label = "Funcion" if tree.kind == StmtKind.FunK else "Declaracion Var"
                print(f"{tree.lineno} {label}: {tree.name}, Tipo: {tipo_str}")
            elif tree.kind == StmtKind.CompoundK:
                print(f"{tree.lineno} Bloque {{}}")
            elif tree.kind == StmtKind.IfK:
                print(f"{tree.lineno} If")
            elif tree.kind == StmtKind.ReturnK:
                print(f"{tree.lineno} Return")
            elif tree.kind == StmtKind.WhileK:
                print(f"{tree.lineno} While")
            else:
                print(f"{tree.lineno} Sentencia: {tree.kind.name}")

        elif tree.nodekind == NodeKind.ExpK:
            if tree.kind == ExpKind.OpK:
                # Validamos que op sea un objeto con .value (TokenType)
                op_str = tree.op.value if hasattr(tree.op, 'value') else str(tree.op)
                print(f"{tree.lineno} Op: {op_str}")
            elif tree.kind == ExpKind.ConstK:
                print(f"{tree.lineno} Const: {tree.val}")
            elif tree.kind == ExpKind.IdK:
                print(f"{tree.lineno} Id: {tree.name}")

        for child_node in tree.child:
            if child_node is not None:
                printTree(child_node)

        tree = tree.sibling

    indentno -= 1