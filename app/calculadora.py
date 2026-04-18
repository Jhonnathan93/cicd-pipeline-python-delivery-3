"""Operaciones básicas para la calculadora web."""

AUTORES = (
    "jsocampod@eafit.edu.co, asrodriguo@eafit.edu.co, "
    "jdgutierrg@eafit.edu.co, mgutierrej@eafit.edu.co"
)


def sumar(a, b):
    """Devuelve la suma de a y b."""
    return a + b


def restar(a, b):
    """Devuelve la resta de a menos b."""
    return a - b


def multiplicar(a, b):
    """Devuelve el producto de a por b."""
    return a * b


def dividir(a, b):
    """Devuelve el cociente de a entre b; falla si b es cero."""
    if b == 0:
        raise ZeroDivisionError("No se puede dividir por cero")
    return a / b
