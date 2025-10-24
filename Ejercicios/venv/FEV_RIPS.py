import pandas as pd
import json
import numpy as np
import inspect

# 📥 Cargar archivo Excel
archivo_excel = "C:\\Users\\dwndz\\OneDrive\\Escritorio\\RIPS\\Dr_JairoCorrea\\drCorrea_092025.xlsx"
xls = pd.ExcelFile(archivo_excel)

# 🧩 Funciones auxiliares
def cargar_transaccion(df):
    return {
        "numDocumentoIdObligado": df.at[0, "numDocumentoIdObligado"],
        "numNota": df.at[0, "numNota"],
        "tipoNota": "RS",
        "numFactura": None,
        "codPrestador": df.at[0, "codPrestador"]
    }

def cargar_usuarios(df):
    usuarios = []
    for i, row in df.iterrows():
        usuarios.append({
            "tipoDocumentoIdentificacion": row["tipoDocumento"],
            "numDocumentoIdentificacion": str(row["numDocumento"]),
            "tipoUsuario": "12",
            "fechaNacimiento": pd.to_datetime(row["fechaNacimiento"]).strftime('%Y-%m-%d'),
            "codSexo": str(row["codSexo"]),
            "codPaisResidencia": str(row["PaisResidencia"]),
            "codMunicipioResidencia": str(row["MunicipioResidencia"]),
            "codZonaTerritorialResidencia": str(row["ZonaResidencia"]),
            "incapacidad": "NO",
            "codPaisOrigen": str(row["PaisOrigen"]),
            "consecutivo": i + 1,
            "servicios": {
                "consultas": [],  # Se llenarán después
                "procedimientos": []  # Se llenarán después
            }
        })
    return usuarios

def cargar_consultas_y_procedimientos(df_consultas, df_procedimientos, usuarios_map, num_documento_obligado, cod_prestador):
    # Asegurar que codPrestador sea string
    cod_prestador = str(cod_prestador)
    
    # Procesar consultas
    for i, row in df_consultas.iterrows():
        doc = str(row["IDPaciente"])
        if doc in usuarios_map:
            consulta = {
                "codPrestador": cod_prestador,  # Usar el código de prestador dinámico
                "fechaInicioAtencion": pd.to_datetime(row["fechaInicioAtencion"]).strftime('%Y-%m-%d %H:%M'),  # Corregido el nombre del campo
                "numAutorizacion": "",
                "codConsulta": str(row["CUPS"]),
                "viaIngresoServicioSalud": "01",
                "modalidadGrupoServicioTecSal": "01",
                "grupoServicios": "01",
                "codServicio": row["codServicio"],
                "finalidadTecnologiaSalud": str(row["finalidadTecnologiaSalud"]),
                "causaMotivoAtencion": str(row["causaMotivoAtencion"]),
                "codDiagnosticoPrincipal": str(row["CIE10_Principal"]),
                "codDiagnosticoRelacionado1": None if pd.isna(row["CIE10_relacionado1"]) else str(row["CIE10_relacionado1"]),
                "codDiagnosticoRelacionado2": None if pd.isna(row["CIE10_relacionado2"]) else str(row["CIE10_relacionado2"]),
                "codDiagnosticoRelacionado3": None if pd.isna(row["CIE10_relacionado3"]) else str(row["CIE10_relacionado3"]),
                "tipoDiagnosticoPrincipal": str(row["tipoDiagnosticoPrincipal"]),
                "tipoDocumentoIdentificacion": "CC",
                "numDocumentoIdentificacion": str(num_documento_obligado),  # Usar el documento del obligado
                "vrServicio": 0,
                "valorPagoModerador": 0,
                "conceptoRecaudo": "05",
                "numFEVPagoModerador": "",
                "consecutivo": i + 1
            }
            usuarios_map[doc]["servicios"]["consultas"].append(consulta)
        else:
            print(f"⚠️ Usuario no encontrado para consulta: {doc}")

    # Procesar procedimientos
    for i, row in df_procedimientos.iterrows():
        doc = str(row["IDPaciente"])
        if doc in usuarios_map:
            procedimiento = {
                "codPrestador": cod_prestador,  # Usar el código de prestador dinámico
                "fechaInicioAtencion": pd.to_datetime(row["fechaInicioAtencion"]).strftime('%Y-%m-%d %H:%M'),  # Corregido el nombre del campo
                "idMIPRES": "",
                "numAutorizacion": "",
                "codProcedimiento": str(row["CUPS"]),
                "viaIngresoServicioSalud": "01",
                "modalidadGrupoServicioTecSal": "01",
                "grupoServicios": "01",
                "codServicio": row["codServicio"],
                "finalidadTecnologiaSalud": "15",
                "tipoDocumentoIdentificacion": "CC",
                "numDocumentoIdentificacion": str(num_documento_obligado),  # Usar el documento del obligado
                "codDiagnosticoPrincipal": str(row["CIE10_Principal"]),
                "codDiagnosticoRelacionado": None if pd.isna(row["CIE10_relacionado"]) else str(row["CIE10_relacionado"]),
                "codComplicacion": None,
                "vrServicio": 0,
                "conceptoRecaudo": "05",
                "valorPagoModerador": 0,
                "numFEVPagoModerador": "",
                "consecutivo": i + 1
            }
            usuarios_map[doc]["servicios"]["procedimientos"].append(procedimiento)
        else:
            print(f"⚠️ Usuario no encontrado para procedimiento: {doc}")

def limpiar_servicios_vacios(usuarios):
    for usuario in usuarios:
        servicios = usuario["servicios"]
        # Si no hay consultas, eliminar la lista de consultas
        if not servicios["consultas"]:
            del servicios["consultas"]
        # Si no hay procedimientos, eliminar la lista de procedimientos
        if not servicios["procedimientos"]:
            del servicios["procedimientos"]
        # Si no hay servicios, eliminar el objeto servicios
        if not servicios:
            del usuario["servicios"]
    return usuarios

# 🧠 Cargar hojas


df_transaccion = xls.parse("TRANSACCION")
df_usuarios = xls.parse("USUARIOS")
df_consultas = xls.parse("CONSULTAS")
df_procedimientos = xls.parse("PROCEDIMIENTOS")

# Convertir los DataFrames a tipos nativos antes de procesarlos
df_transaccion = df_transaccion.astype(object)
df_usuarios = df_usuarios.astype(object)
df_consultas = df_consultas.astype(object)
df_procedimientos = df_procedimientos.astype(object)

# 🧠 Procesar datos
transaccion = cargar_transaccion(df_transaccion)
usuarios = cargar_usuarios(df_usuarios)
usuarios_map = {str(u["numDocumentoIdentificacion"]): u for u in usuarios}

# Pasar el codPrestador de la transacción
cargar_consultas_y_procedimientos(
    df_consultas, 
    df_procedimientos, 
    usuarios_map, 
    df_transaccion.at[0, "numDocumentoIdObligado"],
    df_transaccion.at[0, "codPrestador"]  # Añadir el código de prestador
)

# Primero hacer la verificación
print("\nVerificación de datos antes de limpiar:")
for usuario in usuarios:
    num_doc = usuario["numDocumentoIdentificacion"]
    print(f"Usuario {num_doc}:")
    print(f"  Consultas: {len(usuario['servicios']['consultas'])}")
    print(f"  Procedimientos: {len(usuario['servicios']['procedimientos'])}")
    print("------------------------")

# Después limpiar los servicios vacíos
usuarios = limpiar_servicios_vacios(usuarios)

# JSON final
rips_json = {
    "numDocumentoIdObligado": str(df_transaccion.at[0, "numDocumentoIdObligado"]),
    "numFactura": "",
    "tipoNota": "RS",
    "numNota": str(df_transaccion.at[0, "numNota"]),
    "usuarios": usuarios
}

# Modifica la función convert_numpy_types
def convert_numpy_types(obj):
    if isinstance(obj, np.integer):
        return str(obj) if "codPrestador" in str(inspect.stack()) else int(obj)
    elif isinstance(obj, np.floating):
        if np.isnan(obj):
            return None
        return float(obj)
    elif isinstance(obj, str):
        return None if obj.lower() == 'nan' else obj
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj):
        return None
    elif isinstance(obj, pd.Timestamp):
        if 'fechaNacimiento' in str(inspect.stack()):
            return obj.strftime('%Y-%m-%d')
        return obj.strftime('%Y-%m-%d %H:%M')
    return obj

# Modifica la parte de guardado para limpiar los datos antes de serializar
try:
    ruta_salida = "C:\\CURSOS DEV\\PHYTON\\rips_generado.json"
    
    # Reemplazar "nan" por null en todo el objeto antes de serializar
    def clean_nan_values(obj):
        if isinstance(obj, dict):
            return {k: clean_nan_values(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_nan_values(x) for x in obj]
        elif isinstance(obj, str) and obj.lower() == "nan":
            return None
        return obj
    
    # Limpiar los valores nan antes de guardar
    clean_json = clean_nan_values(rips_json)
    
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(clean_json, f, ensure_ascii=False, indent=2, default=convert_numpy_types)
    print(f"✅ JSON generado con éxito en: {ruta_salida}")
except Exception as e:
    print(f"❌ Error al generar el JSON: {str(e)}")
    # Imprimir más detalles del error
    print("Detalles del error:")
    for key in rips_json:
        try:
            # Intenta serializar cada sección por separado
            json.dumps(rips_json[key], default=convert_numpy_types)
        except Exception as section_error:
            print(f"Error en sección '{key}': {str(section_error)}")