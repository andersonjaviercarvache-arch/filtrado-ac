import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Ingeniería de Costos y Control Financiero", 
    layout="wide"
)

st.title("Sistema de Ingeniería de Costos y Control Financiero")
st.subheader("Búsqueda Inteligente de Comprobantes del SRI")

# Selector de archivos
uploaded_file = st.file_uploader(
    "Carga tu archivo de texto (.txt) descargado del SRI", 
    type=["txt", "csv"]
)

if uploaded_file is not None:
    try:
        # Lectura con tabulación y encoding para tildes/eñes
        df = pd.read_csv(uploaded_file, sep='\t', encoding='latin1')
        
        # Limpiar espacios vacíos en los nombres de las columnas
        df.columns = df.columns.str.strip()
        
        st.success("Archivo cargado correctamente.")
        
        # Campo de búsqueda universal
        st.markdown("---")
        busqueda = st.text_input("🔍 Digita cualquier coincidencia (Nombre, RUC, Nº Factura, Fecha, etc.):")
        
        if busqueda:
            # EXPLICACIÓN DEL CAMBIO:
            # 1. df.astype(str) convierte temporalmente todos los datos a texto.
            # 2. .str.contains busca la palabra ignorando mayúsculas/minúsculas.
            # 3. .any(axis=1) verifica si la palabra está en AL MENOS una columna de la fila.
            mascara_global = df.astype(str).apply(
                lambda x: x.str.contains(busqueda, case=False, na=False)
            ).any(axis=1)
            
            df_filtrado = df[mascara_global].copy()
            
            st.write(f"### Facturas encontradas para: '{busqueda}' ({len(df_filtrado)} registros)")
            
            # Buscar columna de dinero para actualizar el totalizador dinámicamente
            col_monto = None
            for col in ['VALOR TOTAL', 'TOTAL', 'MONTO', 'IMPORTE TOTAL']:
                if col in df_filtrado.columns:
                    col_monto = col
                    break
            
            if col_monto:
                # Conversión segura a decimales
                df_filtrado[col_monto] = df_filtrado[col_monto].astype(str).str.replace(',', '.')
                df_filtrado[col_monto] = pd.to_numeric(df_filtrado[col_monto], errors='coerce')
                
                total_monto = df_filtrado[col_monto].sum()
                st.metric(label="Suma Total de Coincidencias", value=f"${total_monto:,.2f}")
            
            # Desplegar la tabla con las filas que coincidieron
            st.dataframe(df_filtrado, use_container_width=True)
            
        else:
            # Vista general por defecto si el buscador está vacío
            st.write(f"### Vista general del documento ({len(df)} registros en total)")
            st.dataframe(df, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
