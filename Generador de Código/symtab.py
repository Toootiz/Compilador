# Gabriel Muñoz Luna - A01028774
# symtab.py: Estructura de la Tabla de Símbolos por Ámbitos para C-

class Simbolo:
    #Clase para almacenar la información semántica de un identificador.
    def __init__(self, name, kind, data_type, lineno):
        self.name = name          # Nombre del ID (ej. 'x', 'gcd')
        self.kind = kind          # 'Variable', 'Arreglo' o 'Funcion'
        self.data_type = data_type  # 'int' o 'void'
        self.lines = [lineno]     # Lista de líneas donde aparece (empezando por la declaración)
        self.location = None      # Ubicación de memoria (opcional para generación de código)

class Scope:
    #Clase que representa un ámbito (bloque o función) en el programa.
    def __init__(self, name, parent=None):
        self.name = name          # Nombre del ámbito (ej. 'Global', 'gcd', 'Bloque_L5')
        self.parent = parent      # Referencia al Scope superior (Lexical parent)
        self.symbols = {}         # Diccionario { nombre_id: Objeto Simbolo }

    def insert(self, name, kind, data_type, lineno):
        """
        Inserta un símbolo en el ámbito actual.
        Retorna True si se insertó con éxito, False si ya existe.
        """
        if name in self.symbols:
            return False  # Error semántico: Redeclaración en el mismo ámbito
        
        self.symbols[name] = Simbolo(name, kind, data_type, lineno)
        return True

    def lookup_local(self, name):
        #Busca un símbolo SOLO en el ámbito actual.
        return self.symbols.get(name)

    def lookup_global(self, name):
        #Busca un símbolo en el ámbito actual; si no está, sube recursivamente al padre.
        scope_actual = self
        while scope_actual is not None:
            if name in scope_actual.symbols:
                return scope_actual.symbols[name]
            scope_actual = scope_actual.parent
        return None  # No se encontró en ningún nivel


# --- LISTA GLOBAL DE ÁMBITOS PARA LA IMPRESIÓN ---
lista_todos_los_scopes = []

def crear_nuevo_scope(name, parent_scope):
    #Función auxiliar para instanciar un Scope y registrarlo para impresión.
    nuevo = Scope(name, parent_scope)
    lista_todos_los_scopes.append(nuevo)
    return nuevo

def printSymTab():
    print("\n=================================================================")
    print("                 REPORTE ESTRUCTURADO DE TABLAS DE SÍMBOLOS")
    print("=================================================================")
    
    for sc in lista_todos_los_scopes:
        print(f"\nBLOQUE: {sc.name}")
        print(f"{'Identificador':16} | {'Tipo':8} | {'Categoría':12} | {'Apariciones':15}")
        print("-" * 65)
        
        for name, sym in sc.symbols.items():
            # 1. Recuperar Identificador de manera segura
            s_name = getattr(sym, 'name', getattr(sym, 'nombre', str(name)))
            
            # 2. Recuperar y limpiar Tipo (int / void)
            s_type_obj = getattr(sym, 'type', getattr(sym, 'tipo', 'int'))
            s_type = s_type_obj.value if hasattr(s_type_obj, 'value') else str(s_type_obj)
            if "TokenType." in s_type:
                s_type = s_type.split(".")[-1]
            s_type = s_type.lower()
            
            # 3. Recuperar y limpiar Categoría (fun / var / param)
            s_cat_obj = getattr(sym, 'category', getattr(sym, 'categoria', getattr(sym, 'clase', 'var')))
            s_cat = s_cat_obj.value if hasattr(s_cat_obj, 'value') else str(s_cat_obj)
            if "TokenType." in s_cat:
                s_cat = s_cat.split(".")[-1]
            s_cat = s_cat.lower()
            
            # 4. Formatear la lista de líneas de aparición
            s_lines = getattr(sym, 'lines', getattr(sym, 'lineas', []))
            if isinstance(s_lines, list):
                lineas_str = " ".join(str(l) for l in sorted(list(set(s_lines))))
            else:
                lineas_str = str(s_lines)
            
            # Imprimir la fila con alineación uniforme compacta
            print(f"{s_name:16} | {s_type:8} | {s_cat:12} | {lineas_str}")
            
        print("=================================================================")