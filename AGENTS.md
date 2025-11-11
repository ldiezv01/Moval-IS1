# AGENTS.md – Asistente de Desarrollo de Moval

## 1. Propósito del documento

Este archivo describe el **agente de inteligencia artificial utilizado durante el desarrollo del proyecto Moval**, indicando su rol, herramientas, responsabilidades y limitaciones.  
El objetivo es mantener transparencia sobre el uso de IA en el ciclo de vida del software, garantizando que toda la intervención asistida ha sido verificada por los integrantes del equipo humano.

---

## 2. Agente utilizado

- **Nombre del agente:** Codex  
- **Proveedor:** OpenAI  
- **Versión del modelo:** GPT-5-Codex  
- **Tipo de integración:** Asistente de desarrollo integrado mediante la API de OpenAI y GitHub Copilot (VS Code).  
- **Entorno de uso:** Local (entornos de desarrollo del equipo)  
- **Lenguajes principales del proyecto:** Python, SQL, JSON, Markdown  

---

## 3. Rol del agente

El agente Codex actúa como **asistente técnico y documental** dentro del flujo de trabajo de Moval.  
Su función es **ayudar al equipo humano** en tareas de generación, revisión y optimización del código, así como en la elaboración de documentación técnica coherente con el estándar IEEE 830-1998.

El agente **no ejecuta código ni modifica directamente el repositorio remoto**, sino que opera bajo la supervisión de los desarrolladores.

---

## 4. Responsabilidades del agente

| Categoría | Funciones principales |
|------------|----------------------|
| **Generación de código** | Sugerir implementaciones en Python y SQL basadas en los requisitos funcionales definidos en el SRS. |
| **Refactorización y optimización** | Proponer mejoras en legibilidad, eficiencia y mantenimiento del código. |
| **Documentación** | Ayudar en la redacción de archivos como `README.md`, `AGENTS.md`, `CONTRIBUTING.md` y comentarios internos del código. |
| **Pruebas** | Sugerir casos de prueba unitarios y ejemplos de uso. |
| **Revisión de estilo** | Verificar la consistencia con las guías de estilo PEP-8 y convenciones internas del proyecto. |
| **Trazabilidad** | Asistir en la vinculación de requisitos ↔ componentes ↔ pruebas, según las prácticas IEEE. |

---

## 5. Flujo de trabajo con el agente

1. **Consulta y sugerencia:**  
   Los desarrolladores formulan consultas o instrucciones a Codex desde el entorno VS Code o la API de OpenAI.

2. **Propuesta de código o texto:**  
   Codex genera sugerencias de implementación o documentación.

3. **Revisión humana obligatoria:**  
   Cada propuesta es revisada, corregida o descartada por los integrantes del equipo antes de su incorporación al repositorio.

4. **Commit con trazabilidad:**  
   En los commits del proyecto se indica, cuando corresponde, la participación del agente con mensajes del tipo:  
   `Refactor de módulo X (sugerido por Codex)` o `Generación inicial de script Y con ayuda de Codex`.

---

## 6. Limitaciones

- Codex **no accede a bases de datos reales** ni manipula información sensible.  
- No toma decisiones autónomas sobre el diseño o arquitectura del sistema.  
- Todas las acciones asistidas se realizan **bajo supervisión humana** y son verificadas antes del despliegue.  
- No se ha empleado el modelo para generar contenido evaluativo sin intervención del equipo.

---

## 7. Consideraciones éticas y de transparencia

El equipo reconoce que Codex es una herramienta de apoyo y **no un coautor del software**.  
Toda la responsabilidad intelectual y técnica del proyecto Moval recae sobre los miembros del equipo.  
El uso de inteligencia artificial se documenta con el propósito de fomentar la transparencia académica y la trazabilidad de las fuentes utilizadas.

---

## 8. Revisión y mantenimiento del agente

- **Periodicidad:** revisión de configuración y comportamiento del agente cada sprint.  
- **Responsable de verificación:** líder técnico del proyecto.  
- **Versión actual del documento:** 1.0 (noviembre 2025)

---

## 9. Bibliografía y referencias

- OpenAI (2025). *GPT-5 Codex Developer Documentation.*  
- IEEE Std 830-1998. *Recommended Practice for Software Requirements Specifications.*  
- GitHub Copilot Documentation. *Integrating AI assistants into the software development lifecycle.*

---

**Fin del documento**

