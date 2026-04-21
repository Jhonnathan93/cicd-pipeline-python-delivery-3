# Taller CI/CD

## URLs de despliegue (ALB)

Evidencia del despliegue según `terraform output` de cada entorno:

```
Staging ALB URL:    http://calculadora-staging-alb-1177439103.us-east-1.elb.amazonaws.com/
Production ALB URL: http://calculadora-production-alb-1885608817.us-east-1.elb.amazonaws.com/
```

- **Staging:** [http://calculadora-staging-alb-1177439103.us-east-1.elb.amazonaws.com/](http://calculadora-staging-alb-1177439103.us-east-1.elb.amazonaws.com/)
- **Producción:** [http://calculadora-production-alb-1885608817.us-east-1.elb.amazonaws.com/](http://calculadora-production-alb-1885608817.us-east-1.elb.amazonaws.com/)

---

## Respuestas al entregable (sección 9.1)

### 1. Flujo de trabajo completo con Terraform (commit a producción)

El flujo arranca con un **push** a `main` (o ejecución manual del workflow), que dispara `ci-cd.yml`.

1. **Commit / trigger:** el código queda disponible en el runner mediante checkout.

2. **Job `build-test-publish`:** instala dependencias, ejecuta linters, pruebas unitarias, SonarCloud, y si todo pasa en rama `main` construye y publica la imagen Docker en Docker Hub. El artefacto que se mueve hacia adelante es la imagen identificada por URI/tag.

3. **Job `deploy-tf-staging`:** con credenciales AWS y variables prepara backend S3 si aplica, hace `terraform init`/`apply` contra el estado staging y despliegue en ECS + ALB de staging. Valida que la infra y la definición de tarea existan.

4. **Job `update-service-staging`:** fuerza al servicio ECS de staging a usar la nueva task imagen recién construida.

5. **Job `test-staging`:** exporta `APP_BASE_URL` con la URL del ALB de staging y ejecuta pruebas de aceptación. Aquí se valida el comportamiento de usuario contra un entorno real expuesto por el balanceador.

6. **Job `deploy-tf-prod`:** solo si staging pasó; aplica Terraform al workspace/estado de producción (misma imagen validada).

7. **Job `update-service-prod`:** actualiza el servicio ECS de producción con la imagen aprobada.

8. **Job `smoke-test-prod`:** ejecuta pruebas de humo contra la URL de producción. Son comprobaciones para confirmar que el sitio responde tras el despliegue.

### 2. Terraform / IaC frente a despliegue manual y uso de HCL

**Ventajas:** repetibilidad, estado versionado en S3, menos errores por olvidar un security group o un puerto, y documentación viva de la infraestructura.

**Desventajas:** curva de aprendizaje y necesidad de cuidar secretos y formato de variables (por ejemplo listas de subnets en el pipeline).

**HCL:** Facilita expresar la infraestructura de manera estructurada, es muy intuitivo. Sin embargo, tiene ciertas limitaciones, como el manejo de lógica más compleja o el paso de variables, que puede volverse confuso en algunos casos.

### 3. Entorno Staging en el pipeline: ventajas, desventajas y velocidad vs. seguridad

**Ventajas:** se detectan fallos de integración, de infraestructura o de Selenium antes de tocar usuarios reales; permite validar la misma imagen que luego irá a producción.

**Desventajas:** más tiempo de pipeline y más coste de recursos (otro cluster/ALB); si staging y producción no son equivalentes, pueden aparecer fallos solo en un lado.

**Duda:** aunque se usa la misma imagen Docker, los tests de aceptación se repiten en staging. Esto parece redundante porque el artefacto no cambia, aunque entiendo que se busca validar el comportamiento en el entorno real. Aun así, podría optimizarse.

**Velocidad vs. seguridad:** Staging ralentiza el camino a producción, pero aumenta la seguridad del despliegue al ser un colchón de prueba automatizada. Es un intercambio razonable cuando el objetivo es CD con confianza.

### 4. Diferencia entre `test-staging` y `smoke-test-prod`

- **`test-staging`** ejecuta pruebas de aceptación completas con Selenium contra el ALB de staging: recorren flujos de la calculadora, operaciones, errores esperados, etc.

- **`smoke-test-prod`** ejecuta humo contra producción: verificaciones mínimas de que la aplicación carga y responde.

En producción se prioriza confirmar disponibilidad rápida tras el deploy; la validación funcional profunda ya ocurrió en staging con la misma imagen.

### 5. Qué podría faltar al pipeline desde una visión DevOps más amplia (2 ejemplos)

1. **Observabilidad (logs/métricas):** Un pipeline maduro suele enlazar métricas, alertas y dashboards (por ejemplo Amazon CloudWatch alarms). Mejoraría detectar latencia o errores 5xx antes de que el usuario los reporte.

2. **Estrategia de despliegue (no solo deploy directo):** ahora el flujo hace deploy directo. Faltaría implementar blue/green o rolling updates, rollback automático si falla, y health checks más estrictos. Esto reduce el riesgo en producción.

### 6. Experiencia con las dos funcionalidades nuevas (potencia y módulo) y utilidad del CI/CD

Implementar potencia y módulo fue directo a nivel de dominio (`calculadora.py`) y de formulario; el coste real estuvo en actualizar pruebas unitarias y de aceptación para que el pipeline siguiera garantizando regresión.

**Utilidad del CI/CD:** nos resultó útil porque cada cambio pasó por lint, tests y build de imagen de forma automática; al desplegar en AWS, la misma cadena validó que no se rompiera el contrato del formulario ni el health check.

**Menos útil o molesto:** los tiempos de espera del pipeline y los fallos por configuración de los secrets y de los comandos de terraform (debimos usar .tfvars para ambos entornos) no son culpa del código de la calculadora, pero sí frenan el feedback. Aun así, preferimos detectar eso en CI que en producción manual.
