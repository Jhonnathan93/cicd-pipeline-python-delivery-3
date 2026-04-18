# Taller CI/CD - Respuestas

## 1) Ventajas de usar un pipeline de CI

Un pipeline de Integración Continua (CI) le da varias a un proyecto:

- **Detección temprana de errores:** cada push o pull request dispara validaciones automáticas (lint, tests, cobertura). Esto permite encontrar fallos rápido.
- **Calidad constante del código:** al exigir formateo, reglas de estilo y pruebas en cada cambio, el código mantiene un estándar.
- **Feedback rápido para el equipo:** en minutos se sabe si un cambio rompió algo.
- **Trazabilidad y confianza en despliegues:** cada ejecución deja evidencia (logs, artefactos, reportes).

## 2) Diferencia entre prueba unitaria y prueba de aceptación

- **Prueba unitaria:** valida una pieza pequeña y aislada de lógica, sin dependencias externas.
- **Prueba de aceptación:** valida el comportamiento completo desde la perspectiva del usuario.

Ahora tomemos como ejemplo una aplicación que al iniciar sesión diga "hola nombre de usuario" 

- Para una prueba unitaria probariamos la función  

```

Def generar_saludo(nombre): 

   Return "Hola {nombre}"

```

Para la cual creariamos un test unitario el cual pruebe si envio parámetro Mariana el resultado sería “Hola Mariana”
 
- Si quisiera realizar una prueba de aceptación  

Tomaríamos la siguiente historia de usuario: 

```

Como usuario, quiero iniciar sesión para ver un saludo personalizado.

```

Y creariomos la siguiente prueba de aceptación:

```

Escenario: Mostrar saludo después de iniciar sesión 

  Dado que el usuario está en la página de inicio de sesión 

  Y tiene una cuenta con nombre “Mariana” 

  Cuando ingresa sus credenciales correctas 

  Y hace clic en “Iniciar sesión” 

  Entonces debe ver el mensaje “Hola Mariana” 

```

## 3) Qué hace cada step principal del workflow

Desde checkout hasta push de Docker:

1. **Checkout (`actions/checkout`)**  
   Descarga el código del repositorio en el runner.  

2. **Setup Python (`actions/setup-python`)**  
   Instala/configura la versión de Python definida (3.12).  

3. **Install dependencies**  
   Actualiza pip e instala paquetes de `requirements.txt`.  

4. **Run Black**  
   Verifica formato del código (`--check`).  

5. **Run Pylint**  
   Ejecuta análisis estático de calidad.  

6. **Run Flake8**  
   Revisa reglas de estilo y errores simples de Python.  

7. **Run Unit Tests with pytest + coverage**  
   Ejecuta pruebas unitarias y genera reportes de cobertura.  

8. **Run Acceptance Tests**  
   Levanta la app con Gunicorn y corre pruebas (Selenium).  

9. **Upload Artifacts (`actions/upload-artifact`)**  
   Sube reportes (HTML/cobertura) como artefactos del pipeline.  

10. **SonarCloud Scan**  
    Ejecuta análisis de calidad/seguridad y quality gate en SonarCloud.  

11. **Set up QEMU**  
    Prepara emulación para builds multi-arquitectura (cuando aplica).  

12. **Set up Docker Buildx**  
    Habilita builder avanzado de Docker.  

13. **Login to Docker Hub**  
    Autentica con credenciales seguras del repositorio.  

14. **Build and push Docker image**  
    Construye imagen y la publica con tags (`sha` y `latest`).  

## 4) Problemas encontrados y cómo se solucionaron

Durante el taller aparecieron varios problemas reales:

- **Alertas de seguridad/accesibilidad en Sonar:** faltaba `lang` en HTML, binding inseguro a `0.0.0.0` para ejecución local y uso de métodos GET/POST sin endurecer CSRF.  
  **Solución:** añadir `lang="es"` en `index.html`, usar `127.0.0.1` para ejecución local y refactorizar rutas/CSRF con Flask-WTF.

- **Alertas por CORS y métodos HTTP:** Sonar marcó riesgo por mezcla de métodos seguros/no seguros en la misma ruta y configuración HTTP poco restrictiva.  
  **Solución:** separar handlers por método (`@app.get` y `@app.post`), dejar CSRF activo y mantener la app escuchando en localhost en desarrollo.

- **Alertas de calidad (Sonar/Pylint):** docstrings faltantes, línea larga, nombre de constantes y advertencia por posible secreto hardcodeado.  
  **Solución:** refactor de `app.py` y `calculadora.py`, docstrings en módulos/funciones, ajuste de estilo y mejora de gestión de secretos.


## 5) Ventajas de empaquetar en Docker al final del pipeline

- **Portabilidad real:** la misma imagen corre igual en cualquier entorno compatible con Docker.
- **Consistencia entre ambientes:** evita el clásico “en mi máquina sí funciona”.
- **Artefacto desplegable inmediato:** se produce un entregable listo para ejecutar.
- **Base para CD:** automatizar despliegue es mucho más directo.
