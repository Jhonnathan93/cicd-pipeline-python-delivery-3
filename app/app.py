"""Aplicación web Flask de la calculadora con protección CSRF."""

import os

from flask import Flask, render_template, request
from flask_wtf.csrf import CSRFProtect

from .calculadora import dividir, multiplicar, restar, sumar

app_port = int(os.environ.get("PORT", 5000))

app = Flask(__name__)
app.config.from_prefixed_env()
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


@app.get("/health")
def health():
    """Respuesta mínima para health checks (p. ej. ALB en /health)."""
    return "OK", 200


@app.get("/")
def index_get():
    """Muestra el formulario de la calculadora."""
    return render_template("index.html", resultado=None)


@app.post("/")
def index_post():
    """Procesa el envío del formulario y muestra el resultado."""
    return render_template("index.html", resultado=_resultado_from_post())


if __name__ == "__main__":  # pragma: no cover
    app.run(debug=False, port=app_port)
