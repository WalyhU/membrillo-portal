# Guía de commits para agentes IA — El Membrillo Portal

> Pegale esto a tu agente (Claude, Copilot, Cursor, ChatGPT…) **al inicio**.
> Reglas simples para hacer **commits pequeños** y subirlos sin romper nada.
> Si seguís esto al pie de la letra, hasta un modelo chiquito lo logra.

---

## Regla de oro

**1 cambio = 1 commit = 1 idea.** Nada de commits gigantes.
Nunca trabajes ni subas directo a `main` ni a `develop`. Usá una rama `feature/...`.

---

## Ramas del repo

| Rama | Para qué |
|------|----------|
| `main` | Producción. **No tocar directo.** |
| `develop` | Integración. De aquí nacen las features. **No tocar directo.** |
| `pruebas` | Experimentos / probar cosas sin miedo. |
| `feature/tarea-1` … `feature/tarea-4` | Trabajo de cada persona (1 a 4). **Aquí SÍ trabajás.** |

Si necesitás una rama nueva, se crea **siempre desde `develop`**.

---

## ⚡ Lo primero: ¿qué persona sos?

El usuario te dirá algo como **"soy la persona 1"**. Con ese número:

1. Buscá tu fila en la tabla **"Asignación por persona"** de abajo.
2. Trabajá **solo** en tu rama `feature/tarea-N` (N = tu número).
3. Hacé **solo** lo que dice tu asignación. No toques el trabajo de las otras personas.

Si el usuario no dijo número, **preguntáselo** antes de empezar.

---

## Asignación por persona

> Cada persona trabaja en SU rama, hace commits pequeños y abre un PR hacia `develop`.
> El código del sistema ya está hecho: estas tareas son los **entregables del proyecto final**
> (documentación y evidencias), no reescribir la app.

### Persona 1 — Documentación del sistema (Fase 1)
- **Rama:** `feature/tarea-1`
- **Objetivo:** Documentar el análisis del sistema.
- **Crear archivo:** `docs/01-requerimientos.md` con:
  - Descripción del sistema (qué es el portal El Membrillo, 1 párrafo).
  - Requerimientos funcionales (mínimo 5).
  - Requerimientos no funcionales (mínimo 2).
  - Historias de usuario (mínimo 2, formato "Como… quiero… para…").
- **Hecho cuando:** el archivo existe, está completo y hay PR a `develop`.

### Persona 2 — Evidencias de CI/CD (Fase 3)
- **Rama:** `feature/tarea-2`
- **Objetivo:** Documentar el pipeline de GitHub Actions.
- **Crear archivo:** `docs/02-cicd.md` con:
  - Explicación de qué hace `.github/workflows/ci.yml` (jobs backend-check y docker-build).
  - Cómo se dispara (push / pull request).
  - Espacio para pegar capturas: pipeline en verde + logs de ejecución (guardar imágenes en `docs/img/`).
- **Hecho cuando:** el archivo explica el pipeline, tiene las capturas, y hay PR a `develop`.

### Persona 3 — Evidencias de Blue-Green (Fase 4)
- **Rama:** `feature/tarea-3`
- **Objetivo:** Documentar el deployment Blue-Green con sus capturas.
- **Crear archivo:** `docs/03-blue-green.md` con:
  - Explicación breve del proceso (blue = producción, green = nueva versión, swap del Service).
  - Las 4 evidencias en orden: captura ANTES del swap (footer BLUE), captura GREEN (validación), captura del swap (logs), captura DESPUÉS (footer GREEN). Imágenes en `docs/img/`.
  - Comandos usados (`./status.ps1`, `./swap.ps1`).
- **Hecho cuando:** el archivo tiene la explicación + las 4 capturas, y hay PR a `develop`.

### Persona 4 — Presentación final
- **Rama:** `feature/tarea-4`
- **Objetivo:** Generar la presentación `.pptx` y el guion de la demo.
- **Tareas:**
  - Usar el prompt de `PROMPT_PPTX_Deploy.md` para generar `Presentacion_ProyectoFinal_Deploy.pptx`.
  - Crear `docs/04-guion-presentacion.md`: quién dice qué en cada slide (15-20 min) y el orden de la demo en vivo.
- **Hecho cuando:** existe el `.pptx`, existe el guion, y hay PR a `develop`.

---

## Paso 0 — Una sola vez (preparar)

```bash
git clone https://github.com/WalyhU/membrillo-portal.git
cd membrillo-portal
git switch develop
git pull
```

---

## Paso 1 — Elegí (o creá) tu rama de trabajo

Usar una existente:

```bash
git switch feature/tarea-1
git pull
```

O crear una nueva desde develop:

```bash
git switch develop
git pull
git switch -c feature/mi-cambio
```

> Nombre de rama: `feature/` + algo corto en minúsculas con guiones.
> Ejemplos: `feature/login-fix`, `feature/boton-carrito`.

---

## Paso 2 — Hacé UN cambio pequeño

- Tocá lo mínimo para una sola cosa.
- Si vas a hacer 3 cosas → son 3 commits separados, uno por uno.

---

## Paso 3 — Revisá qué cambiaste

```bash
git status
git diff
```

---

## Paso 4 — Commit pequeño

```bash
git add -A
git commit -m "tipo: descripción corta en presente"
```

### Formato del mensaje (Conventional Commits, fácil)

```
tipo: qué hace el cambio
```

Tipos permitidos (elegí uno):

| tipo | cuándo usarlo |
|------|---------------|
| `feat` | nueva funcionalidad |
| `fix` | corrige un bug |
| `docs` | documentación / textos |
| `style` | formato, espacios, CSS (sin cambiar lógica) |
| `refactor` | reordenar código sin cambiar comportamiento |
| `test` | pruebas |
| `chore` | config, dependencias, cosas de mantenimiento |

**Ejemplos buenos:**

```
feat: agregar botón de compartir en producto
fix: corregir total del carrito cuando hay 0 items
docs: actualizar pasos de instalación en README
style: alinear footer en móvil
```

**Reglas del mensaje:**
- En minúsculas, sin punto final.
- Máximo ~60 caracteres en la primera línea.
- Que se entienda QUÉ hace, no "cambios" ni "update".

---

## Paso 5 — Subí a TU rama

```bash
git push -u origin <tu-rama>
```

Ejemplo:

```bash
git push -u origin feature/tarea-1
```

> ⚠️ Nunca `git push origin main` ni `develop`. Siempre tu rama `feature/...`.

---

## Paso 6 — Pull Request (en GitHub)

1. Entrá al repo en GitHub.
2. Botón **"Compare & pull request"**.
3. Base: `develop`  ←  Compare: `tu-rama`.
4. Título = resumen corto. Descripción = qué hiciste.
5. Crear PR y avisar al equipo.

---

## Si algo sale mal (no entres en pánico)

| Problema | Solución |
|----------|----------|
| Commiteé en la rama equivocada | Pedí ayuda antes de seguir. No hagas `push --force`. |
| Hay conflicto al hacer pull | `git pull` y resolvé el archivo marcado con `<<<<<<<`. Si dudás, preguntá. |
| Quiero deshacer cambios SIN commitear | `git restore <archivo>` |
| Me equivoqué de rama y aún no commiteé | `git stash` → `git switch rama-correcta` → `git stash pop` |

---

## Checklist antes de cada push

- [ ] Estoy en una rama `feature/...` (no main/develop).
- [ ] Hice `git pull` antes de empezar.
- [ ] El commit es de **una sola cosa**.
- [ ] El mensaje sigue el formato `tipo: descripción`.
- [ ] Probé que el cambio no rompe (la app abre / no hay error obvio).

---

## Prompt listo para pegarle al agente

> Soy la **persona N** (reemplazá N por tu número). Buscá la tarea de la persona N en
> la sección "Asignación por persona" y hacé SOLO eso, en la rama `feature/tarea-N`.
> Trabajá en el repo El Membrillo Portal. Hacé commits pequeños: 1 cambio = 1 commit.
> Nunca toques `main` ni `develop` directo; trabajá en tu rama `feature/tarea-N`.
> Mensajes de commit en formato `tipo: descripción corta` (feat, fix, docs, style,
> refactor, test, chore), en minúsculas y sin punto final. Después de cada cambio:
> `git add -A`, `git commit -m "..."`, y `git push -u origin <mi-rama-feature>`.
> Si vas a hacer varias cosas, separalas en varios commits. No uses `push --force`.
