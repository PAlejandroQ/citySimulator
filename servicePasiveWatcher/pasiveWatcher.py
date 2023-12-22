import psycopg2
import numpy as np
from sklearn.cluster import DBSCAN
from datetime import datetime
import matplotlib.pyplot as plt
# import os

def plotDBSCAN(unique_labels,coordinates):
    # Visualizar el resultado del clustering
    colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]
    for k, col in zip(unique_labels, colors):
        if k == -1:
            col = [0, 0, 0, 1]

        class_member_mask = labels == k

        xy = coordinates[class_member_mask]
        plt.plot(
            xy[:, 0],
            xy[:, 1],
            "o",
            markerfacecolor=tuple(col),
            markeredgecolor="k",
            markersize=8,
        )
    # current_directory = os.path.realpath(__file__)
    plt.title(f"Estimated number of clusters: {len(unique_labels)-1}")
    plt.savefig("servicePasiveWatcher/sectorsImage.png")
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

    # Aplicación de DBSCAN
    dbscan = DBSCAN(eps=70, min_samples=2).fit(coordinates)
    labels = dbscan.labels_

    # Obtener los centroides manualmente
    unique_labels = set(labels)
    centroids = []
    for label in unique_labels:
        if label != -1:  # No considerar puntos de ruido
            points_of_cluster = coordinates[labels == label, :]
            centroid_of_cluster = np.mean(points_of_cluster, axis=0)
            centroids.append(centroid_of_cluster)

    plotDBSCAN(unique_labels,coordinates)

    # Formateo de los resultados
    results = []
    et_sectors_of_users = []

    for i, centroid in enumerate(centroids):
        sector_id = i  # Asignación de sector_id
        center_gps = f"({centroid[0]}, {centroid[1]})"  # Formato de punto para PostgreSQL
        report_date = int(datetime.now().timestamp() * 1000)  # Obtención de la hora actual en milisegundos
        results.append((sector_id, center_gps, report_date))
        # print(labels == i)
        # Actualizar et_sectors_of_users
        sector_users = np.array(rows)[labels == i]
        for sector_user in sector_users:
            et_sectors_of_users.append((sector_user[1], sector_id))

    sector_users = np.array(rows)[labels == -1]
    for sector_user in sector_users:
        et_sectors_of_users.append((sector_user[1], None))
    # print("RESULTS\n", results)
    # print("ET SECTORS OF USERS\n", et_sectors_of_users)
    # Actualización de la tabla et_sectors en PostgreSQL
    for result in results:
        sector_id, center_gps, report_date = result
        cursor.execute("""
            INSERT INTO et_sectors (sector_id, center_gps, report_date)
            VALUES (%s, %s, %s)
            ON CONFLICT (sector_id) DO UPDATE
            SET center_gps = EXCLUDED.center_gps, report_date = EXCLUDED.report_date
        """, (sector_id, center_gps, report_date))

    # Actualización de la tabla et_sectors_of_users en PostgreSQL
    for et_sector_of_user in et_sectors_of_users:
        user_id, sector_id = et_sector_of_user
        cursor.execute("""
            INSERT INTO et_sectors_of_users (user_id, sector_id)
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id, sector_id))

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
