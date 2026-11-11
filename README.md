# COS115 – Servidores de Alta Disponibilidad

## 1. Descripción del proyecto

Este proyecto presenta una infraestructura de servidores orientada a demostrar conceptos de alta disponibilidad, balanceo de carga, tolerancia a fallos y recuperación automática mediante contenedores Docker.

El sistema utiliza Nginx como balanceador de carga y tres servidores de aplicación desarrollados con Flask y ejecutados mediante Gunicorn. Cada servidor dispone de FFmpeg para procesar videos MP4.

La infraestructura permite distribuir solicitudes entre los servidores disponibles y continuar atendiendo peticiones cuando uno o dos servidores dejan de funcionar.

## 2. Objetivo general

Implementar una infraestructura de servidores que permita demostrar el balanceo de carga, la tolerancia a fallos y la recuperación automática de servicios mediante Docker, Nginx y Flask.

## 3. Tecnologías utilizadas

| Tecnología | Función |
|---|---|
| Docker | Ejecución de servicios mediante contenedores |
| Docker Compose | Definición y administración de la infraestructura |
| Nginx | Balanceo de carga y proxy inverso |
| Python y Flask | Desarrollo de la aplicación web |
| Gunicorn | Servidor de aplicaciones Python |
| FFmpeg | Procesamiento y conversión de videos |
| Git y GitHub | Control de versiones y almacenamiento del código |

## 4. Arquitectura del sistema

La infraestructura está compuesta por cuatro contenedores:

- **balanceador:** recibe las solicitudes HTTP mediante Nginx.
- **servidor1:** ejecuta Flask, Gunicorn y FFmpeg.
- **servidor2:** ejecuta Flask, Gunicorn y FFmpeg.
- **servidor3:** ejecuta Flask, Gunicorn y FFmpeg.

Los tres servidores utilizan un volumen compartido denominado `videos_compartidos`.

Flujo general:

Usuario → Nginx (puerto 8080) → Servidores Flask (puerto 5000) → FFmpeg y almacenamiento compartido.

## 5. Estructura del proyecto

```text
COS115-AltaDisponibilidad/
├── app/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 6. Requisitos

Para ejecutar el proyecto se necesita:

- Docker Desktop o Docker Engine con Docker Compose.
- Git, para clonar el repositorio.
- Un navegador web.
- Recursos suficientes para ejecutar cuatro contenedores.

## 7. Instalación y ejecución

Clonar el repositorio:

```bash
git clone https://github.com/hs21021-cmyk/COS115_AltaDisponibilidad.git
```

Ingresar a la carpeta:

```bash
cd COS115_AltaDisponibilidad
```

Construir e iniciar los contenedores:

```bash
docker compose up -d --build
```

Verificar el estado:

```bash
docker compose ps
```

Abrir la aplicación:

http://localhost:8080

Para detener los servicios:

```bash
docker compose down
```

## 8. Funcionalidades de la aplicación

### Página principal

`GET /`

Muestra el servidor que atendió la solicitud y un formulario para seleccionar un video MP4.

### Verificación de estado

`GET /health`

Ejemplo de respuesta:

```json
{
  "estado": "activo",
  "servidor": "Servidor 1"
}
```

### Procesamiento de videos

`POST /procesar`

Recibe un archivo MP4 mediante el campo `video` y utiliza FFmpeg para generar una versión ajustada a una resolución máxima de 1280 × 720 píxeles, conservando la proporción original.

El archivo procesado utiliza codificación de video H.264 y audio AAC.

### Descarga de videos

`GET /descargar/<nombre>`

Permite descargar los archivos procesados desde el almacenamiento compartido.

## 9. Pruebas de funcionamiento

### Balanceo de carga

Se realizan varias solicitudes a `/health` para comprobar que Nginx distribuye las peticiones entre los tres servidores.

### Tolerancia a fallos

Se detiene uno de los servidores:

```bash
docker compose stop servidor2
```

Se comprueba que los servidores restantes continúan atendiendo solicitudes.

Para restaurarlo:

```bash
docker compose start servidor2
```

### Procesamiento de videos

Se carga un video MP4 desde la página principal y se verifica que FFmpeg genere el archivo procesado.

### Almacenamiento compartido

Se comprueba que los archivos procesados están disponibles desde diferentes servidores gracias al volumen Docker compartido.

### Recuperación automática

Se utiliza la política `unless-stopped` para permitir que Docker reinicie un contenedor cuando termina su proceso principal, siempre que no haya sido detenido manualmente.

La prueba se realizó enviando una señal SIGTERM a Gunicorn desde el interior del contenedor. Se confirmó el incremento del contador de reinicios y la recuperación del endpoint `/health`.

## 10. Limitaciones

- Nginx constituye un punto único de fallo.
- La infraestructura depende de un único equipo anfitrión.
- El almacenamiento compartido no cuenta con replicación independiente.
- Si un servidor termina durante el procesamiento de un video, el trabajo no se reanuda automáticamente.
- No se implementa una cola de tareas distribuida.
- La solución demuestra mecanismos de disponibilidad, pero no constituye una infraestructura de alta disponibilidad completa a nivel de producción.

## 11. Conclusión

El proyecto permite demostrar de manera práctica cómo Docker y Nginx pueden utilizarse para distribuir solicitudes entre varios servidores, mantener la atención de peticiones ante fallos de instancias y recuperar automáticamente contenedores cuando termina su proceso principal.

La integración con FFmpeg proporciona una carga de trabajo real que permite observar el funcionamiento de los servicios y el almacenamiento compartido.