import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# Deshabilitar la advertencia de PyplotGlobalUseWarning
st.set_option('deprecation.showPyplotGlobalUse', False)

# Función para cargar el archivo Excel
def cargar_datos(archivo):
    return pd.read_excel(archivo)

# Función para realizar la regresión lineal simple
def regresion_lineal(datos):
    X = datos[['horas de sueño']]  # Ajusta esto según el nombre de tu variable independiente
    y = datos['rendimiento academico']  # Ajusta esto según el nombre de tu variable dependiente
    
    # Dividir datos en conjunto de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Entrenar el modelo de regresión lineal
    modelo = LinearRegression()
    modelo.fit(X_train, y_train)
    
    return modelo, X_test, y_test

# Función para mostrar resultados
def mostrar_resultados(modelo, X_test, y_test):
    # Mostrar coeficientes de la regresión
    st.write("Coeficientes de la regresión:")
    st.write(modelo.coef_)
    st.write("Término independiente:")
    st.write(modelo.intercept_)
    
    # Mostrar métricas de rendimiento
    st.write("R2 Score del modelo en el conjunto de prueba:", modelo.score(X_test, y_test))
    
    # Mostrar gráfico de dispersión
    plt.scatter(X_test, y_test, color='blue')
    plt.plot(X_test, modelo.predict(X_test), color='red')
    plt.title('Gráfico de Dispersión y Regresión Lineal')
    plt.xlabel('Variable Independiente')
    plt.ylabel('Variable Dependiente')
    st.pyplot()

def main():
    st.title("Sistema de Regresión Lineal Simple creado por Alumnos de FINESI IV")
    
    # Cargar datos
    archivo = st.file_uploader("Cargar archivo Excel", type=['xlsx'])
    if archivo is not None:
        datos = cargar_datos(archivo)
        st.write("Datos cargados:")
        st.write(datos)
        
        # Realizar regresión lineal
        modelo, X_test, y_test = regresion_lineal(datos)
        
        # Mostrar resultados
        st.write("Resultados de la regresión lineal:")
        mostrar_resultados(modelo, X_test, y_test)

if __name__ == "__main__":
    main()