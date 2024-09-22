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
    cap = cv2.VideoCapture(0)

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
def crear_boton_personalizado(titulo, subtitulo, icono):
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(titulo, size=16),
                ft.Text(subtitulo, size=12),
                ft.Icon(icono, size=30),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5
        ),
        width=135,
        height=115,
        bgcolor= '#29ABE2',
        border_radius=10,
        alignment=ft.alignment.center,
        ink=True,
        on_click=lambda e: print(f"Botón {titulo} presionado")
    )

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

    # Crear una matriz de botones usando la función crear_boton_personalizado
    button_matrix = ft.Column(
        [
            ft.Row(
                [
                    ft.Container(content=services_text, alignment=ft.alignment.center, height=50),
                ], 
                alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.Row(
                [
                    crear_boton_personalizado("Corte Láser", "Ing. Francisco Roura", ft.icons.ADD),
                    crear_boton_personalizado("Impresión 3D", "Subtítulo 2", ft.icons.SEARCH),
                    crear_boton_personalizado("Botón 3", "Subtítulo 3", ft.icons.DELETE),
                ], 
                alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.Row(
                [
                    crear_boton_personalizado("Botón 4", "Subtítulo 4", ft.icons.CHECK),
                    crear_boton_personalizado("Botón 5", "Subtítulo 5", ft.icons.CLOSE),
                ], 
                alignment=ft.MainAxisAlignment.CENTER
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
        width=700,
        height=450  # Añadir medidas fijas
    )

    # Primera fila: Columna 1 (2/3 ancho) con los botones, Columna 2 (1/3 ancho) con cámara y texto
    first_row = ft.Row(
        [
            ft.Container(
                content=button_matrix, 
                bgcolor="white",
                alignment=ft.alignment.center,
                padding=10,
                width=650,
                height=450,  
                border_radius=10
            ),
            ft.Column(
                [
                    ft.Container(content=title_text, alignment=ft.alignment.center, width=300, height=50),
                    ft.Container(content=camera_image, bgcolor=colorSecundario, width=330, height=280, border_radius=10),
                    ft.Container(content=qr_text, alignment=ft.alignment.center, width=300, height=50),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER
            )
        ],
        alignment=ft.MainAxisAlignment.START,
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
