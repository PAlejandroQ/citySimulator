import psycopg2
import numpy as np
from sklearn.cluster import KMeans
from datetime import datetime
import matplotlib.pyplot as plt
def plotKmeans(kmeans):
    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_

    plt.scatter(coordinates[:, 0], coordinates[:, 1], c=labels, cmap='viridis', alpha=0.5, edgecolors='k')

    plt.scatter(centroids[:, 0], centroids[:, 1], c='red', marker='X', s=200, label='Centroids')

    # Agregar leyenda y etiquetas
    plt.legend()
    plt.title('K-Means Clustering')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')

    # Mostrar el gráfico
    plt.show()




# Conexión a la base de datos PostgreSQL
host = 'localhost'
databaseName = "project_db"
user = "user_watcher"
password = "password"
conn = psycopg2.connect(
    host=host,
    database=databaseName,
    user=user,
    password=password
)
cursor = conn.cursor()

try:
    # Extracción de la vista latest_et_checkpoints
    cursor.execute("""
        SELECT checkpoint_id, user_id, sector_id, point_gps, state, report_date, row_num
        FROM latest_et_checkpoints
    """)
    rows = cursor.fetchall()

    # Obtención de las coordenadas para el clustering
    coordinates = np.array([(float(row[3].split(',')[0][1:]), float(row[3].split(',')[1][:-1])) for row in rows])

    # Aplicación de k-means
    kmeans = KMeans(n_clusters=5, n_init=10)
    kmeans.fit(coordinates)
    centroids = kmeans.cluster_centers_
    plotKmeans(kmeans)
    print("OK Cluster Centers")

    # Formateo de los resultados
    results = []
    for i, centroid in enumerate(centroids):
        sector_id = i + 1  # Asignación de sector_id
        center_gps = f"({centroid[0]}, {centroid[1]})"  # Formato de punto para PostgreSQL
        report_date = int(datetime.now().timestamp() * 1000)  # Obtención de la hora actual en milisegundos
        results.append((sector_id, center_gps, report_date))

    # Actualización de la tabla existente en PostgreSQL
    for result in results:
        sector_id, center_gps, report_date = result
        cursor.execute("""
            INSERT INTO et_sectors (sector_id, center_gps, report_date)
            VALUES (%s, %s, %s)
            ON CONFLICT (sector_id) DO UPDATE
            SET center_gps = EXCLUDED.center_gps, report_date = EXCLUDED.report_date
        """, (sector_id, center_gps, report_date))

    # Confirmar los cambios en la base de datos
    conn.commit()

except Exception as e:
    # En caso de error, realizar un rollback para deshacer cambios
    conn.rollback()
    print("Error:", e)

finally:
    # Cerrar el cursor y la conexión
    cursor.close()
    conn.close()



