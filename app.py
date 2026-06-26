import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Ingeniería de Costos y Control Financiero", 
    layout="wide"
)

st.title("Sistema de Ingeniería de Costos y Control Financiero")
st.subheader("Filtrado y Control de Facturas del SRI")

# 1. Selector de archivos
uploaded_file = st.file_uploader(
    "Carga tu archivo de texto (.txt) descargado del SRI", 
    type=["txt", "csv"]
)

if uploaded_file is not None:
    try:
        # Los reportes del SRI usan tabulaciones ('\t') como separador
        # Usamos encoding='latin1' para evitar errores con tildes y eñes
        df = pd.read_csv(uploaded_file, sep='\t', encoding='latin1')
        
        # Limpiar espacios en blanco invisibles en los nombres de las columnas
        df.columns = df.columns.str.strip()
        
        st.success("Archivo cargado y procesado con éxito.")
        
        # 2. Identificar columnas clave automáticamente
        # El SRI suele usar 'RAZÓN SOCIAL EMISOR' o 'RAZON SOCIAL EMISOR'
        col_emisor = None
        for col in ['RAZÓN SOCIAL EMISOR', 'RAZON SOCIAL EMISOR', 'EMISOR', 'NOMBRE EMISOR']:
            if col in df.columns:
                col_emisor = col
                break
        
        # Si las columnas cambian, permitimos que el usuario la seleccione manualmente
        if col_emisor is None:
            col_emisor = st.selectbox(
                "No se detectó la columna automática. Selecciona la columna del Emisor/Proveedor:", 
                df.columns
            )
            
        # 3. Campo de búsqueda/filtrado por nombre
        st.markdown("---")
        busqueda = st.text_input("🔍 Ingresa el nombre del proveedor o empresa para filtrar:")
        
        # 4. Aplicar el filtro si hay texto ingresado
        if busqueda:
            # Filtramos convirtiendo a texto, ignorando mayúsculas/minúsculas (.str.contains)
            df_filtrado = df[df[col_emisor].astype(str).str.contains(busqueda, case=False, na=False)].copy()
            
            st.write(f"### Resultados para: '{busqueda}' ({len(df_filtrado)} registros encontrados)")
            
            # Intentar buscar la columna de dinero para sumarizar de forma segura
            col_monto = None
            for col in ['VALOR TOTAL', 'TOTAL', 'MONTO', 'IMPORTE TOTAL']:
                if col in df_filtrado.columns:
                    col_monto = col
                    break
            
            if col_monto:
                # Limpieza de la columna Monto por seguridad (manejo de strings o comas decimales)
                df_filtrado[col_monto] = df_filtrado[col_monto].astype(str).str.replace(',', '.')
                df_filtrado[col_monto] = pd.to_numeric(df_filtrado[col_monto], errors='coerce')
                
                # Calcular el total acumulado de las facturas filtradas
                total_monto = df_filtrado[col_monto].sum()
                st.metric(label="Monto Total Filtrado", value=f"${total_monto:,.2f}")
            
            # Mostrar la tabla filtrada
            st.dataframe(df_filtrado, use_container_width=True)
            
        else:
            # Si no hay búsqueda, mostrar todo el documento original
            st.write(f"### Vista general del documento ({len(df)} registros en total)")
            st.dataframe(df, use_container_width=True)
            
    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
        st.info("Asegúrate de que el archivo sea el documento plano (.txt) obtenido directamente de las consultas del SRI.")
