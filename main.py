import cv2
from pyzbar.pyzbar import decode, ZBarSymbol
import numpy as np
import flet as ft
import threading
import base64
import requests
import time

# Función para consultar la API con la matrícula escaneada
def consultar_api(matricula, page, show_dialog):
    url = "http://localhost:8000/api/v1/consulta"
    body = {
        "TokenApi": "",
        "Matricula": matricula,
        "Comando": "InfoAlumno",
        "idEspacio": 1
    }
    
    try:
        response = requests.post(url, json=body)
        if response.status_code == 200:
            data = response.json()
            nombre_completo = f"{data['name']} {data['ape_pat']}"
            carrera = data['Carrera']
            mensaje_bienvenida = f"Código QR: {matricula}\nBienvenido {nombre_completo} - {carrera}"
            show_dialog(mensaje_bienvenida)
        else:
            show_dialog(f"Código QR: {matricula}\nError al consultar la API")
    except Exception as e:
        show_dialog(f"Código QR: {matricula}\nError de conexión: {str(e)}")

# Función para escanear el QR y actualizar la pantalla en Flet
def scan_qr(update_image, show_dialog, page):
    for i in range(5):  # Intenta con los primeros 5 índices de cámara
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"Cámara encontrada en el índice {i}")
            break
    else:
        print("No se encontraron cámaras disponibles.")
    #cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Decodificamos solo los códigos QR (ZBarSymbol.QRCODE filtra únicamente QR)
        decoded_objects = decode(frame, symbols=[ZBarSymbol.QRCODE])

        for obj in decoded_objects:
            matricula = obj.data.decode("utf-8")
            consultar_api(matricula, page, show_dialog)

            points = obj.polygon
            if len(points) == 4:
                cv2.polylines(frame, [np.array(points, dtype=np.int32)], isClosed=True, color=(0, 255, 0), thickness=2)

        # Convertir el frame en imagen JPEG
        _, img_encoded = cv2.imencode('.jpg', frame)
        img_bytes = img_encoded.tobytes()

        # Convertimos la imagen en formato base64
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')

        # Actualizamos la imagen en la pantalla usando src_base64
        update_image(img_base64)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()

# Función para crear botones personalizados con título, subtítulo e ícono
def crear_boton_personalizado(titulo, subtitulo, icono, altura, on_click):
    return ft.Container(
        content=ft.Row(
            [
                # Columna izquierda: Icono
                ft.Container(
                    content=ft.Icon(icono, size=25, color="white"),
                    alignment=ft.alignment.center,
                    padding=5
                ),
                # Columna derecha: Título y subtítulo
                ft.Column(
                    [
                        ft.Text(titulo, size=16, weight=ft.FontWeight.BOLD, color="white"),
                        #ft.Text(subtitulo, size=12, color="white"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,  # Espacio entre el icono y el texto
            vertical_alignment  = ft.CrossAxisAlignment.CENTER
        ),
        width=570,
        height=altura,  # Ajusta el alto según el diseño deseado
        bgcolor='#29ABE2',  # Color de fondo
        border_radius=10,  # Bordes redondeados
        alignment=ft.alignment.center,
        ink=True,  # Efecto de pulsación al hacer clic
        on_click=on_click
    )

# Función para mostrar la pantalla de escaneo de QR
def mostrar_pantalla_qr(page):
    # Imagen para mostrar la vista de la cámara
    camera_image = ft.Image(src_base64="", fit=ft.ImageFit.FILL, expand=True)

    # Función para actualizar la imagen de la cámara
    def update_image(img_base64):
        camera_image.src_base64 = img_base64
        page.update()

    # Función para mostrar el mensaje de bienvenida en un AlertDialog
    def show_dialog(mensaje):
        dlg = ft.AlertDialog(
            title=ft.Text(mensaje),
            modal=True,
        )
        page.dialog = dlg
        page.update()
        page.dialog.open = True
        page.update()
        time.sleep(4)
        page.dialog.open = False
        page.update()

    # Pantalla de escaneo QR
    scan_qr_screen = ft.Column(
        [
            ft.Text("Escanea tu QR", size=24, weight="bold"),
            ft.Container(content=camera_image, width=800, height=400, border_radius=10, bgcolor="black"),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20
    )

    # Cambiar a la pantalla de escaneo QR
    page.clean()
    page.add(scan_qr_screen)
    page.update()

    # Iniciar el hilo de escaneo
    threading.Thread(target=scan_qr, args=(update_image, show_dialog, page), daemon=True).start()

# Función para iniciar la interfaz de Flet
def main(page: ft.Page):
    # Colores
    colorPrincipal = '#052147'
    colorSecundario = '#FFFFFF'
    colorTerciario = '#29ABE2'
    colorComplemento = '#0030A4'

    # Definir la fuente Montserrat
    page.fonts = {
        "Montserrat": "assets/fonts/Montserrat-VariableFont_wght.ttf",
        "Roboto-Bold" : "assets/fonts/Roboto-Bold.ttf",
        "Roboto-Regular" : "assets/fonts/Roboto-Regular.ttf",
    }

    # Configurar el tema con la fuente por defecto
    page.theme = ft.Theme(font_family="Roboto-Bold")

    # Colores y otras configuraciones de página
    page.title = "Escaneo de QR"
    page.window_full_screen = True
    page.window_width = 1024
    page.window_height = 600
    page.bgcolor = colorPrincipal

    # Texto para mostrar siempre "Esperando escaneo de QR"
    qr_text = ft.Text(value="Esperando escaneo de QR...", size=20, weight="bold",color =colorSecundario)
    title_text = ft.Text(value="Esperando escaneo de QR...", size=20, weight="bold",color =colorSecundario)
    services_text = ft.Text(value="Elige el motivo de tu visita", size=30, weight="bold", font_family="Montserrat")

    # Imagen para mostrar la vista de la cámara
    camera_image = ft.Image(src_base64="", fit=ft.ImageFit.FILL, expand=True)

    # Función para actualizar la imagen de la cámara
    def update_image(img_base64):
        camera_image.src_base64 = img_base64
        page.update()

    # Función para mostrar el mensaje de bienvenida en un AlertDialog
    def show_dialog(mensaje):
        dlg = ft.AlertDialog(
            title=ft.Text(mensaje),
            modal=True,
        )
        page.dialog = dlg
        page.update()
        page.dialog.open = True
        page.update()
        time.sleep(4)
        page.dialog.open = False
        page.update()

    
    # Lista con la información de los botones
    botones_info = [
        {"titulo": "Impresión 3D", "subtitulo": "Subtítulo 1", "icono": ft.icons.CATEGORY, "accion": lambda e: mostrar_pantalla_qr(page)},
        {"titulo": "Corte Láser", "subtitulo": "Subtítulo 2", "icono": ft.icons.SHAPE_LINE_OUTLINED, "accion": lambda e: mostrar_pantalla_qr(page)},
        {"titulo": "Consultoría", "subtitulo": "Subtítulo 3", "icono": ft.icons.PEOPLE, "accion": lambda e: mostrar_pantalla_qr(page)},
    ]

    # Calcular la altura dinámica de cada botón
    total_height = 300  # Altura total disponible para los botones (ajusta según el espacio)
    num_botones = len(botones_info)
    espaciado = 10  # Espacio entre botones
    altura_boton = (total_height - (espaciado * (num_botones - 1))) // num_botones  # Altura proporcional a la cantidad de botones


    # Crear la matriz de botones dinámicamente
    button_matrix = ft.Column(
        [
            ft.Row(
                [
                    crear_boton_personalizado(boton["titulo"], boton["subtitulo"], boton["icono"],altura_boton,boton["accion"])
                ], 
                alignment=ft.MainAxisAlignment.CENTER
            ) for boton in botones_info
        ],
        alignment=ft.MainAxisAlignment.CENTER,        
        spacing=espaciado,
        width=600,
        height=total_height  # Añadir medidas fijas
    )

    #ft.Container(content=camera_image, bgcolor=colorSecundario, width=330, height=280, border_radius=10),
    # Primera fila: Columna 1 (centrado) con los botones
    first_row = ft.Row(
        [
            ft.Container(
                content=ft.Column(
                    [
                        # Primera fila: services_text centrado
                        ft.Row(
                            [
                                ft.Container(content=services_text, alignment=ft.alignment.center, height=50),
                            ], 
                            alignment=ft.MainAxisAlignment.CENTER
                        ),

                        # Segunda fila: Dos columnas, un botón a la izquierda y button_matrix a la derecha
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Container(
                                            content=ft.Column(
                                                [
                                                    ft.Text("General", size=20, weight="bold", color=colorSecundario, text_align=ft.TextAlign.CENTER),
                                                    ft.Text("Espacio de trabajo", size=16, weight="bold", color=colorSecundario, text_align=ft.TextAlign.CENTER),
                                                    ft.Icon(ft.icons.WORK, size=30, color=colorSecundario),
                                                ],
                                                alignment=ft.MainAxisAlignment.CENTER,  # Centrar verticalmente los elementos
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Centrar horizontalmente los elementos
                                                spacing=5  # Añadir espacio entre los elementos
                                            ),
                                            width=260,
                                            height=300,
                                            bgcolor='#29ABE2',
                                            border_radius=10,
                                            alignment=ft.alignment.center,  # Centrar el contenedor dentro del padre
                                            ink=True,
                                            on_click=lambda e: print(f"Visita General Presionado")
                                        )
                                    ]
                                ),
                                ft.Column(
                                    [
                                        ft.Container(
                                            content=button_matrix,
                                            alignment=ft.alignment.center,
                                            width=600,  # Ajusta el tamaño si es necesario
                                            height=300
                                        )
                                    ]
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # Espacio entre las dos columnas
                        ),
                    ],
                    #spacing=10,  # Espacio entre las dos filas (services_text y las columnas)
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                bgcolor="white",
                alignment=ft.alignment.center,  # Centrar el contenido dentro del contenedor
                padding=30,
                width=900,  # Ajusta el ancho según sea necesario
                height=450,  
                border_radius=10
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,  # Centrar la fila dentro de la pantalla
        spacing=10,
        width=1024,
        height=450  # Medidas de la fila completa
    )


    # Segunda fila: Logo centrado
    second_row = ft.Row(
        [
            ft.Image(src="assets/logo_blanco_h.png", width=300, height=100)
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        width=1024,
        height=100  # Medidas de la segunda fila
    )

    # Agregar las dos filas a la página sin usar SafeArea
    page.add(
        ft.Column(
            [
                first_row,
                second_row
            ],
            width=1024,
            height=600,
            spacing=10
        )
    )

    # Hilo separado para escanear el QR mientras Flet se ejecuta
    threading.Thread(target=scan_qr, args=(update_image, show_dialog, page), daemon=True).start()

# Ejecuta la aplicación Flet
ft.app(target=main)
