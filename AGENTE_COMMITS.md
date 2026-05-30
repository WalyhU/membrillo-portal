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
| `feature/tarea-1`, `feature/tarea-2`, `feature/tarea-3` | Trabajo de cada quien. **Aquí SÍ trabajás.** |

Si necesitás una rama nueva, se crea **siempre desde `develop`**.

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

> Trabajá en el repo El Membrillo Portal. Hacé commits pequeños: 1 cambio = 1 commit.
> Nunca toques `main` ni `develop` directo; trabajá en una rama `feature/...`.
> Mensajes de commit en formato `tipo: descripción corta` (feat, fix, docs, style,
> refactor, test, chore), en minúsculas y sin punto final. Después de cada cambio:
> `git add -A`, `git commit -m "..."`, y `git push -u origin <mi-rama-feature>`.
> Si vas a hacer varias cosas, separalas en varios commits. No uses `push --force`.
