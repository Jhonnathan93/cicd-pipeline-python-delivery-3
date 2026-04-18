"""Aplicación web Flask de la calculadora con protección CSRF."""

import os
import secrets
from pathlib import Path

from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFProtect

from .calculadora import dividir, multiplicar, restar, sumar


def _secret_key() -> str:
    """Clave sesión/CSRF desde env o desde archivo local compartido."""
    env_key = os.environ.get("SECRET_KEY")
    if env_key:
        return env_key

    default_key_path = (
        Path(__file__).resolve().parent.parent / ".cicd_pipeline_secret_key"
    )
    key_file = Path(os.environ.get("SECRET_KEY_FILE", str(default_key_path)))
    if key_file.exists():
        return key_file.read_text(encoding="utf-8").strip()

    key_file.parent.mkdir(parents=True, exist_ok=True)
    generated_key = secrets.token_hex(32)
    key_file.write_text(generated_key, encoding="utf-8")
    return generated_key


app = Flask(__name__)
app.secret_key = _secret_key()
csrf = CSRFProtect(app)


def _resultado_from_post() -> str | float | None:
    """Calcula el resultado a partir del formulario POST."""
    try:
        num1 = float(request.form["num1"])
        num2 = float(request.form["num2"])
        operacion = request.form["operacion"]
        operaciones = {
            "sumar": sumar,
            "restar": restar,
            "multiplicar": multiplicar,
            "dividir": dividir,
        }
        funcion = operaciones.get(operacion)
        if funcion is None:
            return "Operación no válida"
        return funcion(num1, num2)
    except ValueError:
        return "Error: Introduce números válidos"
    except ZeroDivisionError:
        return "Error: No se puede dividir por cero"


@app.get("/")
def index_get():
    """Muestra el formulario de la calculadora."""
    return render_template("index.html", resultado=None)


@app.post("/")
def index_post():
    """Procesa el envío del formulario y muestra el resultado."""
    return render_template("index.html", resultado=_resultado_from_post())


if __name__ == "__main__":  # pragma: no cover
    # Quita debug=True para producción
    app.run(debug=True, port=5000, host="127.0.0.1")
