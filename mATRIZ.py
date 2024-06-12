import streamlit as st
import pandas as pd

class Matriz:
    def __init__(self, datos):
        self.__datos = pd.DataFrame(datos)

    def save_to_txt(self, data, filename):
        data.to_csv(f'{filename}.txt', index=False, sep='\t')

    def show_matriz(self):
        st.write("Matriz Original:")
        st.write(self.__datos)
        self.save_to_txt(self.__datos, 'matriz_original')

    def diagonal(self):
        diag = pd.DataFrame(0, index=range(len(self.__datos)), columns=self.__datos.columns)
        for i in range(len(self.__datos)):
            diag.iat[i, i] = self.__datos.iat[i, i]
        st.write("Matriz Diagonal:")
        st.write(diag)
        self.save_to_txt(diag, 'matriz_diagonal')

    def triangular_superior(self):
        tri_sup = pd.DataFrame(0, index=range(len(self.__datos)), columns=self.__datos.columns)
        for i in range(len(self.__datos)):
            for j in range(i, len(self.__datos.columns)):
                tri_sup.iat[i, j] = self.__datos.iat[i, j]
        st.write("Matriz Triangular Superior:")
        st.write(tri_sup)
        self.save_to_txt(tri_sup, 'matriz_triangular_superior')

    def triangular_inferior(self):
        tri_inf = pd.DataFrame(0, index=range(len(self.__datos)), columns=self.__datos.columns)
        for i in range(len(self.__datos)):
            for j in range(0, i+1):
                tri_inf.iat[i, j] = self.__datos.iat[i, j]
        st.write("Matriz Triangular Inferior:")
        st.write(tri_inf)
        self.save_to_txt(tri_inf, 'matriz_triangular_inferior')

    def transpuesta(self):
        transp = self.__datos.transpose()
        st.write("Matriz Transpuesta:")
        st.write(transp)
        self.save_to_txt(transp, 'matriz_transpuesta')

def main():
    st.title("Transformaciones de Matrices")
    
    uploaded_file = st.file_uploader("Cargar archivo CSV", type=["csv"])
    if uploaded_file is not None:
        # Intentar leer el archivo con varias codificaciones comunes
        for encoding in ['utf-8', 'latin-1', 'ISO-8859-1', 'cp1252']:
            try:
                data = pd.read_csv(uploaded_file, encoding=encoding)
                break
            except UnicodeDecodeError:
                uploaded_file.seek(0)
        else:
            st.error("No se pudo leer el archivo con las codificaciones comunes.")
            return

        m = Matriz(data)
        
        if st.button("Mostrar Matriz Original"):
            m.show_matriz()
        if st.button("Mostrar Diagonal"):
            m.diagonal()
        if st.button("Mostrar Triangular Superior"):
            m.triangular_superior()
        if st.button("Mostrar Triangular Inferior"):
            m.triangular_inferior()
        if st.button("Mostrar Transpuesta"):
            m.transpuesta()

if __name__ == "__main__":
    main()
