
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
def procesar_imagen(nombre_archivo, umbral=244):
    # Abre la imagen y la convierte a escala de grises
    imagen = Image.open(nombre_archivo).convert("L")

    # Obtiene los datos de los píxeles
    datos = list(imagen.getdata())
    print(min(datos))
    # plt.imshow(datos, cmap="gray")
    # plt.axis('off')
    # plt.show()
    # Convierte los valores de píxeles a caracteres "#" o "_"
    caracteres = ["#" if pixel < umbral else "_" for pixel in datos]

    # Crea la matriz a partir de los caracteres
    matriz = [caracteres[i:i + imagen.width] for i in range(0, len(caracteres), imagen.width)]

    return np.array(matriz) 

def imprimir_matriz(matriz):
    for fila in matriz:
        print("".join(fila))

if __name__ == "__main__":
    # Cambia el nombre de la imagen según tu archivo
    nombre_archivo = "mapReady.png"
    
    # Ajusta el umbral según tu imagen
    # umbral = 244 umbral de cambio minimo
    # 255 umbral maximo
    umbral = 244

    matriz_resultante = procesar_imagen(nombre_archivo, umbral)
    print(len(matriz_resultante))
    # imprimir_matriz(matriz_resultante)
    print(np.array(matriz_resultante).shape)
    # plt.imshow(caracteres_data, cmap="gray")
    # plt.axis('off')
    # plt.show()
