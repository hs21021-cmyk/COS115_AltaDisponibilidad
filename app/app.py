

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
from pathlib import Path
from uuid import uuid4
import os
import subprocess

app = Flask(__name__)

# Identificación de la instancia del servidor
SERVIDOR = os.environ.get("SERVIDOR", "Servidor local")

# Directorio de almacenamiento
BASE_DIR = Path(__file__).resolve().parent.parent
VIDEOS_DIR = Path(
    os.environ.get("VIDEOS_DIR", str(BASE_DIR / "videos"))
)

ENTRADAS = VIDEOS_DIR / "entradas"
PROCESADOS = VIDEOS_DIR / "procesados"

ENTRADAS.mkdir(parents=True, exist_ok=True)
PROCESADOS.mkdir(parents=True, exist_ok=True)

# Tamaño máximo: 100 MB
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024


@app.route("/")
def inicio():
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>COS115 - Alta Disponibilidad</title>
    </head>
    <body>
        <h1>Proyecto COS115 - Alta Disponibilidad</h1>
        <h2>Servidor activo: {SERVIDOR}</h2>

        <p>Procesamiento de videos mediante FFmpeg.</p>

        <form action="/procesar" method="POST"
              enctype="multipart/form-data">

            <label>Selecciona un video MP4:</label>
            <input type="file" name="video"
                   accept=".mp4,video/mp4" required>

            <button type="submit">
                Procesar video
            </button>
        </form>
    </body>
    </html>
    """


@app.route("/health")
def estado():
    return jsonify({
        "estado": "activo",
        "servidor": SERVIDOR
    })


@app.route("/procesar", methods=["POST"])
def procesar_video():

    if "video" not in request.files:
        return jsonify({"error": "No se recibió un video"}), 400

    archivo = request.files["video"]

    if not archivo.filename:
        return jsonify({"error": "No se seleccionó un archivo"}), 400

    nombre_seguro = secure_filename(archivo.filename)

    if Path(nombre_seguro).suffix.lower() != ".mp4":
        return jsonify({"error": "Solo se permiten archivos MP4"}), 400

    # Identificador único para evitar nombres repetidos
    identificador = uuid4().hex

    nombre_entrada = f"{identificador}_original.mp4"
    nombre_salida = f"{identificador}_720p.mp4"

    ruta_entrada = ENTRADAS / nombre_entrada
    ruta_salida = PROCESADOS / nombre_salida

    archivo.save(ruta_entrada)

    comando = [
        "ffmpeg",
        "-y",
        "-i", str(ruta_entrada),
        "-vf",
        "scale=w=1280:h=720:force_original_aspect_ratio=decrease:force_divisible_by=2",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        str(ruta_salida)
    ]

    try:
        subprocess.run(
            comando,
            check=True,
            capture_output=True,
            text=True,
            timeout=300
        )

    except subprocess.TimeoutExpired:
        ruta_salida.unlink(missing_ok=True)
        return jsonify({
            "error": "El procesamiento superó el tiempo permitido"
        }), 504

    except (subprocess.CalledProcessError, OSError):
        ruta_salida.unlink(missing_ok=True)
        return jsonify({
            "error": "No se pudo procesar el video"
        }), 500

    return jsonify({
        "mensaje": "Video procesado correctamente",
        "servidor": SERVIDOR,
        "archivo": nombre_salida,
        "descarga": f"/descargar/{nombre_salida}"
    })


@app.route("/descargar/<nombre>")
def descargar_video(nombre):
    return send_from_directory(
        PROCESADOS,
        nombre,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
