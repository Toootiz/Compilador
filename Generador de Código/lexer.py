#Gabriel Muñoz Luna - A01028774
#Proyecto 1 Analizador Léxico
from globalTypes import *

#Definición de variables globales traidas desde el script del que usara el profe 
def globales(prog, pos, long):
    global programa, posicion, progLong, numLinea
    programa = prog
    posicion = pos
    progLong = long
    numLinea = 1

# Diccionario que representa la tabla de flujos del DFA
tabla_dict = {
    # Estado: [0:Otro, 1:Blanco, 2:Letra, 3:Num, 4:+, 5:-, 6:*, 7:=, 8:/, 9:<, 10:>, 11:!, 12:;, 13:,, 14:(, 15:), 16:[, 17:], 18:{, 19:}, 20:$]
    0:  [32, 0, 1, 3, 5, 6, 8, 21, 10, 13, 16, 19, 24, 25, 26, 27, 28, 29, 30, 31, 33],
    1:  [2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    3:  [4, 4, 32, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
    10: [11, 11, 11, 11, 11, 11, 12, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11],
    12: [12, 12, 12, 12, 12, 12, 7, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12],
    7: [12, 12, 12, 12, 12, 12, 12, 12, 9, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12],
    13: [14, 14, 14, 14, 14, 14, 14, 15, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14],
    16: [17, 17, 17, 17, 17, 17, 17, 18, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17],
    19: [32, 32, 32, 32, 32, 32, 32, 20, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32],
    21: [22, 22, 22, 22, 22, 22, 22, 23, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22],
    32: [34, 34, 32, 32, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34, 34]
}


# Funcion para detectar la columna y su respectivo caracter
def get_col(c):
    if c.isspace(): return 1
    if c.isalpha(): return 2
    if c.isdigit(): return 3
    if c == '+': return 4
    if c == '-': return 5
    if c == '*': return 6
    if c == '=': return 7
    if c == '/': return 8
    if c == '<': return 9
    if c == '>': return 10
    if c == '!': return 11
    if c == ';': return 12
    if c == ',': return 13
    if c == '(': return 14
    if c == ')': return 15
    if c == '[': return 16
    if c == ']': return 17
    if c == '{': return 18
    if c == '}': return 19
    if c == '$': return 20
    return 0

# Definición de la función getToken, que implementa la lógica del DFA para reconocer tokens
def getToken(imprime = True):
    # Declaramos las variables globales para poder modificarlas dentro de la función
    global posicion, programa, numLinea
    

    # while que implementa la lógica del DFA para reconocer tokens
    while True:
        estado = 0
        lexema = ""
        token = None
        estados_finales = {2, 4, 5, 6, 9, 8, 11, 14, 15, 17, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33, 34} # Estados que representan tokens válidos (incluyendo comentarios y EOF)
        estados_backtrack = {2, 4, 11, 14, 17, 22, 34} # Estados que requieren retroceder

        # Reset del estado, lexema y token para cada seccion del texto
        while estado not in estados_finales:
            c = programa[posicion] if posicion < len(programa) else '$' 
            col = get_col(c)
            
            # Transición de estados usando la tabla_dict
            if estado in tabla_dict:    
                nuevo_estado = tabla_dict[estado][col]
            else:
                nuevo_estado = 32 # Error
            
            # Si el nuevo estado es de backtrack, no se pasa la posición ni se agrega al lexema
            if nuevo_estado in estados_backtrack:
                estado = nuevo_estado
            # Evita agregar espacios al lexema
            else:
                if c == '\n': # Si encuentras un salto de línea
                    numLinea += 1

                if not (estado == 0 and c.isspace()): # No guardar espacios iniciales
                    lexema += c

                posicion += 1
                estado = nuevo_estado
                
                if estado == 0:
                    lexema = ""

        # Evitar bucle infinito al final     
        if estado == 0:
            if posicion >= len(programa):
                return TokenType.EndFile, "$"
            continue
        
        # Asignar el token correspondiente según el estado final alcanzado
        if estado == 2:
            token = RESERVED_WORDS.get(lexema, TokenType.ID)
        elif estado == 4:
            token = TokenType.NUM
        elif estado == 5:
            token = TokenType.PLUS
        elif estado == 6:
            token = TokenType.MINUS
        elif estado == 8:
            token = TokenType.TIMES
        elif estado == 11:
            token = TokenType.OVER
        elif estado == 24:
            token = TokenType.SEMI
        elif estado == 25:
            token = TokenType.COMMA
        elif estado == 26:
            token = TokenType.LPAREN
        elif estado == 27:
            token = TokenType.RPAREN
        elif estado == 14:
            token = TokenType.LT
        elif estado == 17:
            token = TokenType.GT
        elif estado == 22:
            token = TokenType.ASSIGN
        elif estado == 28:
            token = TokenType.LBRACKET
        elif estado == 29:
            token = TokenType.RBRACKET
        elif estado == 30:
            token = TokenType.LBRACE
        elif estado == 9:
            token = TokenType.COMMENT
            continue
        elif estado == 31:
            token = TokenType.RBRACE
        elif estado == 33:
            token = TokenType.ENDFILE
        elif estado ==18:
            token = TokenType.GTE
        elif estado == 23:
            token = TokenType.EQ
        elif estado == 34:
            token = TokenType.ERROR
            if lexema.strip() != "":
                print(f"Token: {token.name}, Lexema: {lexema}")
                imprimir_error(lexema, posicion, numLinea)
                return token, lexema
        
        else:
            token = TokenType.ERROR
        
        # Prevenir error de token vacio
        if token == TokenType.ERROR and lexema.strip() == "":
                continue
        
        # Imprimir el token y su lexema
        if imprime:
            print(f"Token: {token.name}, Lexema: {lexema}")
            
        return token, lexema


'''-------------------------------------------------------------------------------------------------
Función realizada con la ayuda de inteligencia artificial con la finalidad de imprimir el error de
manera más clara, mostrando la línea completa y un puntero al error
Se entiende y se comenta paso por paso lo que realiza
---------------------------------------------------------------------------------------------------'''

# Función para imprimir el error 
def imprimir_error(lexema, pos_actual, num_linea):
    # Se busca el inicio de la línea actual para imprimirla completa
    inicio_linea = programa.rfind('\n', 0, pos_actual) + 1
    fin_linea = programa.find('\n', pos_actual)
    if fin_linea == -1: fin_linea = len(programa)
    
    linea_texto = programa[inicio_linea:fin_linea].replace('$', '')
    
    # Calculamos la posición del puntero ^
    # Restamos el largo del lexema porque 'posicion' ya avanzó
    offset = pos_actual - inicio_linea - len(lexema)
    
    print(f"Línea {num_linea}: Error en la formación de un entero o identificador:")
    print(f"{linea_texto}")
    print(" " * offset + "^")