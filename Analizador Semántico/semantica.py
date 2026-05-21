# Gabriel Muñoz Luna - A01028774
# semantica.py: Analizador Semántico e Inferencia de Tipos para C-

from globalTypes import *
from symtab import *

# revision de errores
Tiene_Errores = False

# amalcena las lines para los erores
lineas_codigo_fuente = []

#FUNCIONES UTILITARIAS 

def cargar_lineas_codigo(ruta_archivo):
    #Carga el archivo original en memoria para poder mostrar las líneas con errores.
    global lineas_codigo_fuente
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            lineas_codigo_fuente = f.readlines()
    except Exception:
        lineas_codigo_fuente = []

def normalizar_valor(obj):
    #Extrae de forma segura cadenas de texto limpias ignorando Enums, enteros o estructuras internas.
    if obj is None:
        return ""
    
    # Si ya es un entero (pánico del parser), lo hacemos string directo
    if isinstance(obj, int):
        return str(obj).lower()
        
    # Si es un Enum o tiene atributo value, extraemos el valor seguro
    if hasattr(obj, 'value'):
        val_str = str(obj.value)
    else:
        val_str = str(obj)
        
    val_str = str(val_str)
    
    if "TokenType." in val_str:
        val_str = val_str.split(".")[-1]
        
    return val_str.lower()

def forzar_atributos_simbolo(simbolo, categoria, tipo):
    #Fuerza atributos en el objeto símbolo para garantizar compatibilidad.
    if simbolo is None: return
    for attr in ['category', 'categoria', 'cat']:
        if hasattr(simbolo, attr) or attr in ['category', 'categoria']:
            setattr(simbolo, attr, categoria)
    for attr in ['type', 'tipo']:
        if hasattr(simbolo, attr) or attr in ['type', 'tipo']:
            setattr(simbolo, attr, tipo)

def errorSemantico(nodo, mensaje, token_error=None):
    global Tiene_Errores, lineas_codigo_fuente, scope_actual
    Tiene_Errores = True
    
    nombre_scope = scope_actual.name if scope_actual else "GLOBAL"
    
    print(f"\nLínea {nodo.lineno} [ÁMBITO: {nombre_scope}]: Error semántico: {mensaje}")
    
    idx_linea = nodo.lineno - 1
    if 0 <= idx_linea < len(lineas_codigo_fuente):
        linea_original = lineas_codigo_fuente[idx_linea].rstrip('\r\n')
        print(linea_original)
        
        target = token_error if token_error else getattr(nodo, 'name', getattr(nodo, 'op', ''))
        
        posicion = 0
        if target and str(target) in linea_original:
            posicion = linea_original.find(str(target))
            
        print(" " * posicion + "^")

# Variable global para rastrear el tipo de la función donde estamos parados
funcion_actual_tipo = "void"
scope_actual = None

def recorrer_tabla(nodo):
    global scope_actual
    if nodo is None: return

    abrio_scope = False

    if nodo.nodekind == NodeKind.StmtK:
        if nodo.kind == StmtKind.FunK:
            tipo_str = normalizar_valor(nodo.type)
            nombre_fun = str(nodo.name)
            exito = scope_actual.insert(nombre_fun, "fun", tipo_str, nodo.lineno)
            if not exito:
                errorSemantico(nodo, f"Redeclaración de la función '{nombre_fun}'", nombre_fun)
            
            simb = scope_actual.lookup_global(nombre_fun)
            forzar_atributos_simbolo(simb, "fun", tipo_str)
            
            scope_actual = crear_nuevo_scope(nombre_fun.upper(), scope_actual)
            abrio_scope = True

        elif nodo.kind == StmtKind.VarK:
            tipo_str = normalizar_valor(nodo.type)
            nombre_var = str(nodo.name)
            
            if tipo_str == "void":
                errorSemantico(nodo, f"La variable '{nombre_var}' no puede ser de tipo 'void'. Solo se permite 'int'.", nombre_var)
                tipo_str = "int"
                
            es_arreglo = (hasattr(nodo, 'is_array') and nodo.is_array) or (hasattr(nodo, 'child') and len(nodo.child) > 0 and nodo.child[0] is not None)
            cat_str = "var (arreglo)" if es_arreglo else "var"
            
            exito = scope_actual.insert(nombre_var, cat_str, tipo_str, nodo.lineno)
            if not exito:
                errorSemantico(nodo, f"Redeclaración del identificador '{nombre_var}' en este ámbito.", nombre_var)
                
            simb = scope_actual.lookup_global(nombre_var)
            forzar_atributos_simbolo(simb, cat_str, tipo_str)

        elif nodo.kind == StmtKind.CompoundK:
            if scope_actual.name == "GLOBAL" or (scope_actual.parent and scope_actual.parent.name == "GLOBAL" and len(scope_actual.symbols) > 0):
                scope_actual = crear_nuevo_scope(f"BLOQUE_L{nodo.lineno}", scope_actual)
                abrio_scope = True

    elif nodo.nodekind == NodeKind.ExpK:
        if nodo.kind == ExpKind.IdK:
            nombre_id = str(nodo.name)
            simbolo = scope_actual.lookup_global(nombre_id)
            if simbolo is None:
                errorSemantico(nodo, f"El identificador '{nombre_id}' no ha sido declarado en este ámbito.", nombre_id)
                scope_actual.insert(nombre_id, "var", "int", nodo.lineno)
            else:
                if not hasattr(simbolo, 'lines') or simbolo.lines is None:
                    simbolo.lines = []
                if nodo.lineno not in simbolo.lines:
                    simbolo.lines.append(nodo.lineno)

    if hasattr(nodo, 'child') and nodo.child:
        for hijo in nodo.child:
            if hijo is not None: recorrer_tabla(hijo)

    if abrio_scope and scope_actual.parent is not None:
        scope_actual = scope_actual.parent

    if hasattr(nodo, 'sibling') and nodo.sibling is not None:
        recorrer_tabla(nodo.sibling)

def recorrer_tipos(nodo):
    global funcion_actual_tipo, scope_actual
    if nodo is None: return

    cambio_funcion = False
    anterior_tipo = funcion_actual_tipo

    if nodo.nodekind == NodeKind.StmtK and nodo.kind == StmtKind.FunK:
        funcion_actual_tipo = normalizar_valor(nodo.type)
        cambio_funcion = True

    if hasattr(nodo, 'child') and nodo.child:
        for hijo in nodo.child:
            if hijo is not None: recorrer_tipos(hijo)

    if nodo.nodekind == NodeKind.ExpK:
        if nodo.kind == ExpKind.OpK:
            hijo1 = nodo.child[0] if len(nodo.child) > 0 else None
            hijo2 = nodo.child[1] if len(nodo.child) > 1 else None
            
            tipo_h1 = getattr(hijo1, 'exp_type', 'int') if hijo1 else 'int'
            tipo_h2 = getattr(hijo2, 'exp_type', 'int') if hijo2 else 'int'
            
            if tipo_h1 != 'int' or tipo_h2 != 'int':
                errorSemantico(nodo, f"Operador '{nodo.op}' requiere operandos de tipo entero ('int'). Recibió ('{tipo_h1}' y '{tipo_h2}')", nodo.op)
            
            nodo.exp_type = 'int'

        elif nodo.kind == ExpKind.ConstK:
            nodo.exp_type = 'int'

        elif nodo.kind == ExpKind.IdK:
            nombre_id = str(nodo.name)
            simbolo = scope_actual.lookup_global(nombre_id)
            if simbolo:
                s_type = getattr(simbolo, 'type', getattr(simbolo, 'tipo', 'int'))
                nodo.exp_type = normalizar_valor(s_type)
            else:
                nodo.exp_type = 'int'

    elif nodo.nodekind == NodeKind.StmtK:
        if nodo.kind == StmtKind.AssignK:
            if len(nodo.child) > 1 and nodo.child[1] is not None:
                tipo_derecha = getattr(nodo.child[1], 'exp_type', 'int')
                if tipo_derecha == 'void':
                    errorSemantico(nodo, "No se puede asignar un valor de tipo 'void' a una variable.", "=")

        elif nodo.kind == StmtKind.ReturnK:
            tiene_expresion = len(nodo.child) > 0 and nodo.child[0] is not None
            tipo_retornado = getattr(nodo.child[0], 'exp_type', 'int') if tiene_expresion else 'void'

            if funcion_actual_tipo == 'void' and tipo_retornado != 'void':
                errorSemantico(nodo, "Una función de tipo 'void' no debe retornar valores.", "return")
            elif funcion_actual_tipo == 'int' and tipo_retornado == 'void':
                errorSemantico(nodo, "Una función de tipo 'int' requiere retornar una expresión entera.", "return")

    if cambio_funcion:
        funcion_actual_tipo = anterior_tipo

    if hasattr(nodo, 'sibling') and nodo.sibling is not None:
        recorrer_tipos(nodo.sibling)


def inicializar_funciones_nativas():
    global scope_actual
    scope_actual.insert("input", "fun", "int", 0)
    scope_actual.insert("output", "fun", "void", 0)
    forzar_atributos_simbolo(scope_actual.lookup_global("input"), "fun", "int")
    forzar_atributos_simbolo(scope_actual.lookup_global("output"), "fun", "void")

def tabla(tree, imprime=True):
    global scope_actual, Tiene_Errores
    Tiene_Errores = False
    lista_todos_los_scopes.clear()
    
    scope_actual = crear_nuevo_scope("GLOBAL", None)
    inicializar_funciones_nativas()
    
    recorrer_tabla(tree)
    
    simbolos_globales = list(scope_actual.symbols.keys())
    if "main" not in simbolos_globales:
        class Dummy: lineno = 1
        errorSemantico(Dummy(), "Falta la declaración obligatoria de la función 'main'.")
    elif simbolos_globales[-1] != "main":
        simb_main = scope_actual.lookup_global("main")
        class DummyMain: lineno = getattr(simb_main, 'line', 1)
        errorSemantico(DummyMain(), "Restricción semántica: La función 'main' debe ser la última declaración en el archivo.")
    
    if imprime:
        printSymTab()

def semantica(tree, imprime=True, ruta_fuente=None):
    #Orquesta el análisis semántico y la validación de tipos.
    if ruta_fuente:
        cargar_lineas_codigo(ruta_fuente)
        
    tabla(tree, imprime)
    
    print("\nChecking Types...")
    recorrer_tipos(tree)
    print("Type Checking Finished")
    
    if not Tiene_Errores:
        print("\n>>> Análisis Semántico listo sin erroes.")
    else:
        print("\nSe detectaron errores semánticos durante la validación del programa.")