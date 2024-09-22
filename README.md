
# Proyecto de Escaneo de Códigos QR con Flet y OpenCV

Este proyecto permite escanear códigos QR utilizando la cámara, consultar una API con la información del código y mostrar un mensaje de bienvenida en una ventana de diálogo. La interfaz está construida utilizando **Flet**, mientras que el escaneo de códigos QR se realiza con **OpenCV** y **pyzbar**.

## Características

- Escaneo de códigos QR en tiempo real utilizando la cámara.
- Consultas a una API externa para obtener información sobre el código QR escaneado.
- Interfaz gráfica con botones personalizados que incluyen título, subtítulo e ícono.
- Visualización de una imagen capturada por la cámara.
- Mensajes de alerta para mostrar información tras el escaneo.

## Requisitos

Asegúrate de tener instalados los siguientes paquetes:

- **Flet**: Para la interfaz gráfica.
- **OpenCV**: Para la captura de video y procesamiento de imagen.
- **pyzbar**: Para la decodificación de los códigos QR.
- **requests**: Para realizar consultas HTTP a la API.

Instala los paquetes con:

```bash
pip install flet opencv-python pyzbar requests
```

## Estructura del Proyecto

```
📂 assets
 ┣ 📂 fonts
 ┃ ┗ 📄 Montserrat-VariableFont_wght.ttf
 ┗ 📄 logo_blanco_h.png
📄 main.py
📄 README.md
```

- **assets/fonts/**: Carpeta donde se almacenan las fuentes utilizadas en el proyecto.
- **assets/logo_blanco_h.png**: Logo que aparece en la interfaz.
- **main.py**: Archivo principal que contiene la lógica del escaneo y la interfaz gráfica.
- **README.md**: Archivo de documentación del proyecto.

## Configuración

1. Coloca la fuente `Montserrat-VariableFont_wght.ttf` en la carpeta `assets/fonts`.
2. Asegúrate de que el logo esté en la carpeta `assets/` con el nombre `logo_blanco_h.png`.
3. Modifica el archivo `main.py` según tus necesidades si es necesario.

## Ejecución

Para ejecutar el proyecto, simplemente corre el siguiente comando en tu terminal:

```bash
python main.py
```

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.
