import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Leer archivo Excel
file_path = 'Encuestapy.xlsx'  # Cambia el path si es necesario
df = pd.read_excel(file_path)

# Filtrar solo las columnas de los candidatos indicados y las columnas de filtros
candidatos = ['Milei', 'Villarruel', 'Macri', 'Bullrich', 'CFK', 'Massa', 'Moreno', 'Randazzo', 'Manes', 'Kicillof', 'Katopodis', 'Santilli', 'Espert', 'Osaba', 'Alak', 'Garro', 'Píparo', 'Allan']
df_candidatos = df[candidatos + ['Zona', 'Edad', 'Nivel Educativo', 'Sexo']]

# Crear una nueva columna para agrupar las edades en rangos
def clasificar_edad(edad):
    if 16 <= edad <= 29:
        return '16-29'
    elif 30 <= edad <= 42:
        return '30-42'
    elif 43 <= edad <= 55:
        return '43-55'
    elif edad > 55:
        return 'Mayores de 55'
    else:
        return 'Fuera de rango'

df_candidatos['Rango Edad'] = df_candidatos['Edad'].apply(clasificar_edad)

# Función para graficar la imagen de los candidatos con filtros
def graficar_imagen(zona, edad, nivel_educativo, sexo):
    # Aplicar filtros
    candidatos_df = df_candidatos.copy()
    if zona:
        candidatos_df = candidatos_df[candidatos_df['Zona'] == zona]
    if edad:
        candidatos_df = candidatos_df[candidatos_df['Rango Edad'] == edad]
    if nivel_educativo:
        candidatos_df = candidatos_df[candidatos_df['Nivel Educativo'] == nivel_educativo]
    if sexo:
        candidatos_df = candidatos_df[candidatos_df['Sexo'] == sexo]

    # Contar la cantidad de respuestas por valor para cada candidato en porcentaje
    distribucion = candidatos_df[candidatos].apply(lambda x: x.value_counts(normalize=True) * 100).T.fillna(0)

    # Calcular la suma de MB (1), B (2) y R+ (3) para cada candidato y crear la columna "Imagen Positiva"
    distribucion['Imagen Positiva'] = distribucion[1] + distribucion[2] + distribucion[3]

    # Ordenar por "Imagen Positiva" de mayor a menor
    distribucion = distribucion.sort_values(by='Imagen Positiva', ascending=False)

    # Crear gráfico de barras apiladas horizontales
    plt.figure(figsize=(16, 8))

    acumulado = pd.DataFrame()

    etiquetas = ['Muy Buena', 'Buena', 'Regular Positiva', 'Regular Negativa', 'Mala', 'Muy Mala']
    colores = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', '#9467bd', '#8c564b']

    for i, (etiqueta, color) in enumerate(zip(etiquetas, colores), start=1):
        valores = distribucion[i] if i in distribucion.columns else [0] * len(distribucion)

        # Crear las barras apiladas
        if acumulado.empty:
            acumulado = valores
        else:
            acumulado += valores

        bars = plt.barh(distribucion.index, valores, left=acumulado - valores, label=etiqueta, color=color)

        # Añadir etiquetas a las barras
        for bar, value in zip(bars, valores):
            if value >= 1:  # Mostrar solo si el valor es mayor o igual a 1%
                plt.text(bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() / 2,
                         f'{value:.0f}%', ha='center', va='center', color='black', fontsize=9)

    # Etiquetas y título
    plt.xlabel('Porcentaje (%)')
    plt.ylabel('Candidatos')
    plt.title('Distribución de Imagen por Candidato')

    # Mover la leyenda a la derecha sin superposición
    plt.legend(title='Valoración de Imagen', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Invertir el eje y para que el candidato con mayor imagen positiva esté arriba
    plt.gca().invert_yaxis()

    # Ajustar el gráfico para que no se superpongan los elementos
    plt.tight_layout(rect=[0, 0, 0.85, 1])  # Ajustar el margen derecho para la leyenda

    # Eliminar el borde del rectángulo
    for spine in plt.gca().spines.values():
        spine.set_visible(False)

    # Ocultar los valores de referencia del eje X
    plt.gca().xaxis.set_visible(False)

    # Mostrar el gráfico en Streamlit
    st.pyplot(plt)

# Controles interactivos en Streamlit
st.sidebar.title("Filtros")
zona = st.sidebar.selectbox('Zona:', ['', 'Casco', 'Norte', 'Sur', 'Oeste'])
edad = st.sidebar.selectbox('Rango de Edad:', ['', '16-29', '30-42', '43-55', 'Mayores de 55'])
nivel_educativo = st.sidebar.selectbox('Nivel Educativo:', ['', 'Primario', 'Secundario', 'Superior'])
sexo = st.sidebar.selectbox('Sexo:', ['', 'Masculino', 'Femenino'])

# Convertir los valores seleccionados a los valores numéricos para el filtrado
nivel_educativo_value = {'Primario': 1, 'Secundario': 2, 'Superior': 3}.get(nivel_educativo, None)
sexo_value = {'Masculino': 1, 'Femenino': 2}.get(sexo, None)

# Mostrar el gráfico basado en los filtros seleccionados
graficar_imagen(zona, edad, nivel_educativo_value, sexo_value)
