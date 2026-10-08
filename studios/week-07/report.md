# Week 7 Studio — Blocklists Lose, Boundaries Win

**Curso:** CMP-5006E Computer Security (Fall 2026)
**Autor:** Alex J. — **Fecha:** 8 de octubre de 2026
**Entorno:** Python 3.13.12, Windows (PowerShell), ejecución local (`127.0.0.1`), sin Docker.

---

## 1. Resumen

Se evaluó un WAF basado en blocklist (4 reglas regex, estilo ModSecurity CRS) contra
ataques conocidos, mutaciones del mismo ataque y tráfico legítimo. Después se comparó
con parametrización de consultas, y se confirmó un bypass sobre la app real `vuln-web`
con un oráculo sólido (el *canary* del admin).

**Conclusión:** el WAF falla en las dos dimensiones a la vez. Es evadible (axis 4) y
bloquea usuarios legítimos (axis 5). La parametrización no enumera nada: la entrada es
un valor y nunca llega a un contexto de código. Eso da una garantía (axis 2) que el WAF
no puede dar.

| Medición | Resultado | Tarea |
|---|---|---|
| Cobertura sobre ataques conocidos | **4/4** | 1 |
| Bypasses que pasan el WAF | **3/4** | 2 |
| Falsos positivos sobre tráfico legítimo | **2/26 = 7.7 %** | 3 |
| Inyecciones exitosas con parametrización | **0/8** | 4 |
| Bypass confirmado en la app real (canary filtrado) | **True** | 5 |
| Requests marcados por `anomaly()` (bypassed pero anómalos) | **1** | 5 |
| Tests provistos | **6/6 pasan** | — |

---

## 2. Qué se implementó

Se completaron las cinco funciones de `starter.py`. Todo el motor (`waf_block`,
`parameterized_login`, los conjuntos de ataque, el corpus benigno y el puente a
`vuln-web`) viene dado en `waf.py`.

```python
def measure_coverage(payloads):                      # Task 1
    blocked = sum(1 for p in payloads if waf_block(p))
    return blocked, len(payloads)

def measure_bypasses(bypasses):                      # Task 2
    through = sum(1 for p, _why in bypasses if not waf_block(p))
    return through, len(bypasses)

def measure_false_positives(benign):                 # Task 3
    return [(inp, rule) for inp in benign if (rule := waf_block(inp))]

def count_injection_successes(payloads):             # Task 4
    succeeded = sum(1 for p in payloads if parameterized_login(p, "wrong"))
    return succeeded, len(payloads)

def bypass_leaks_canary(base_url):                   # Task 5
    canary = vulnweb_canary()
    for payload, _why in BYPASSES:
        if waf_block(payload):       # el WAF lo frenó: nunca se envía
            continue
        try:
            body = send_login(base_url, payload)
        except Exception:            # la app puede responder 4xx/5xx
            continue
        if canary in body:           # oráculo sólido: el canary, no el eco
            return True
    return False
```

---

## 3. Resultados por tarea

### Task 1 — Cobertura sobre ataques conocidos (4/4)

El WAF bloquea los cuatro ataques de la semana 6 (tautología numérica, `UNION SELECT`,
`<script>`, `DROP TABLE`). **Esto no es un claim de seguridad.** Solo mide los payloads
que ya conocíamos al escribir las reglas, y no dice nada sobre lo que no se enumeró.

### Task 2 — Bypass (axis 4): 3/4 pasan

| Payload | ¿Pasa el WAF? | Por qué |
|---|---|---|
| `admin' OR 'a'='a'--` | **Pasa** | La regla exige `\d=\d`; la tautología con comillas no es numérica. |
| `x' UnIoN SeLeCt u,p FROM users--` | **Bloqueado** | Ver nota abajo. |
| `<img src=x onerror=alert(1)>` | **Pasa** | XSS sin la cadena `<script`. |
| `'; DR\u200bOP TABLE users--` | **Pasa** | Un carácter de ancho cero parte la palabra `DROP`. |

> **Nota (hallazgo propio).** El README describe `UnIoN SeLeCt` como bypass por
> "case + spacing", pero la regla ya usa `(?i)` y un espacio simple coincide con
> `[\s/*]+`. Esa mutación **no evade** nada. Los 3 bypasses reales son la tautología
> con comillas, el `onerror` sin `<script` y el carácter de ancho cero. Esto confirma
> lo observado en la terminal (`BLOCKED` en esa línea).

Cada bypass es una mutación de minutos. El espacio de lo "malo" es abierto y el
blocklist nunca puede completarse.

### Task 3 — Falsos positivos (axis 5): 2/26 = 7.7 %

| Input legítimo bloqueado | Regla |
|---|---|
| `drop table tennis lessons for beginners` | SQLi DROP TABLE |
| `reserve the drop table at the makerspace friday` | SQLi DROP TABLE |

**Ejemplo concreto:** el WAF le niega el servicio a una persona que busca clases de
*drop table tennis* (tenis de mesa). Cada caso es un usuario real rechazado, un ticket
de soporte y tiempo de analista. Un WAF que bloquea usuarios se apaga, y entonces su
cobertura real es 0 %.

Otras entradas con lenguaje parecido a un ataque **sí pasaron** porque el orden de las
palabras no coincide con la regex:
`i want to select the union option on the benefits form` (la regla pide `union` antes
de `select`) y `my order number is 1=1-2024` (la regla de tautología exige `or`).
Esos resultados son suerte de redacción, no robustez.

> **Ambas hojas fallan a la vez.** Aflojar reglas para reducir falsos positivos
> multiplica los bypasses. Apretarlas bloquea a más usuarios. No existe una
> configuración que sea completa y silenciosa. Eso es lo que fija
> `test_blocklist_loses_on_both_blades`: 3 bypasses pasan **y** 2 usuarios legítimos
> son bloqueados, simultáneamente.

### Task 4 — La garantía de la parametrización (0/8)

Los 8 payloads (4 ataques + 4 bypasses) se enviaron como *username* a
`parameterized_login`. Resultado: **0/8 lograron entrar.**

**Garantía (axis 2):** *"La entrada del usuario no puede alterar la estructura de la
consulta, para ninguna entrada."*

No es "bloqueado por una regla": no hay regla que evadir, porque no existe un camino
de la entrada hacia la estructura del query. El WAF nunca podría enunciar esto.

**Condición de la que depende** (el axis 2 pide que la garantía sea condicional): la
garantía vale **si y solo si** todas las consultas pasan los datos como parámetros.
Una sola concatenación olvidada en otra parte del código la rompe para ese query.

### Task 5 — Bypass confirmado en la app real + detección

**Oráculo.** Para cada bypass que el WAF *deja pasar*, se envía a `/login` de la app
real y se busca el **canary del admin** en la respuesta. No se busca el payload
reflejado, porque eso solo probaría reflexión y no fuga. Resultado: **`True`**, al menos
un bypass que pasó el WAF filtró el canary. Los payloads que el WAF bloquea nunca
llegan a la app.

Esto sigue la disciplina de `seclab.attack`: un hallazgo es un efecto relevante para la
seguridad, confirmado por un oráculo y reproducible, no "se veía bien".

**Detección con `anomaly()`.** La regla dada marca un request cuando hay una
comilla/terminador seguido de una palabra clave SQL/HTML. Sobre los 3 bypasses que
pasaron el WAF, marcó **1** (por lectura de la regex, la tautología
`admin' OR 'a'='a'--`):

| Bypass | ¿`anomaly()` lo marca? | Razón |
|---|---|---|
| `admin' OR 'a'='a'--` | Sí | comilla seguida de `OR` |
| `<img src=x onerror=alert(1)>` | No | no hay `'`, `"` ni `;` antes de la palabra clave |
| `'; DR\u200bOP TABLE users--` | No | el carácter invisible rompe la palabra `drop` |

Recall sobre los bypasses: **1/3**. La detección también tiene huecos.

**Costo de carga analista (axis 5 de la detección).** Cada marca es tiempo humano. Por
lectura manual de la regex sobre el corpus benigno, no debería marcar ninguna de las 26
entradas legítimas (0/26). **Esto está por verificar**, ver el comando en la sección 7.
Además, la palabra `or` sin límite de palabra (`\b`) es una fuente latente de ruido:
cualquier texto con comilla seguida de `...or...` (como "order", "for", "word") podría
disparar la regla. Es el mismo problema de precisión/recall del WAF y la automation
paradox de la semana 13.

**Mejora propuesta (no ejecutada).** Para cubrir los dos bypasses que `anomaly()` no ve,
se podría añadir un patrón de manejadores de evento HTML y de caracteres invisibles:

```python
import re
EXT = re.compile(
    r"['\";].*(select|drop|or|union|onerror)"   # regla original
    r"|\bon\w+\s*="                              # onerror=, onload=, ...
    r"|[\u200b-\u200d\ufeff]",                   # caracteres de ancho cero
    re.I,
)
```

Predicción: marcaría los 3/3 bypasses. Costo esperado: más marcas sobre texto legítimo
que contenga `on...=`, o caracteres invisibles legítimos (por ejemplo, texto copiado de
documentos o idiomas con joiners). Hay que medirlo antes de afirmar nada.

---

## 4. Control Scorecard

### 4.1 WAF blocklist

| Axis | Before | After control | Evidence |
|---|---|---|---|
| 1 · Threat model | Atacante remoto no autenticado, sin credenciales, controla el campo `user` de `/login` | Sin cambios. Se asume que no conoce las reglas, pero sí puede mutar payloads libremente | `vuln-web /login` |
| 2 · Guarantee | Ninguna | Bloquea las firmas de las 4 regex **si** el payload coincide literalmente con alguna. No se hace ningún claim sobre cualquier otra entrada | `waf.py` (`WAF_RULES`) |
| 3 · Coverage | 0/4 bloqueados | 4/4 en ataques conocidos; 1/4 en las mutaciones (5/8 en total). **Muestra de 8 payloads, no el espacio de ataque** (el rubric pide ≥ 20) | salida de `starter.py` |
| **4 · Bypass** | — | **Encontrado, 3/4 pasan:** tautología con comillas, `onerror` sin `<script`, ancho cero en `DROP`. Al menos uno filtra el canary en la app real | `starter.py`, `test_bypass_leaks_canary_on_real_app` |
| 5 · FP cost | 0 % | **2/26 = 7.7 %** del corpus benigno bloqueado (ej.: "drop table tennis lessons for beginners") | `benign_traffic.json`, salida de `starter.py` |
| 6 · Op cost | — | No medido. 4 regex, latencia esperada despreciable. El costo real es el tuning continuo (cada bypass nuevo exige otra regla) | — |
| 7 · Observability | Sin logging | `waf_block` devuelve el nombre de la regla que disparó, pero este lab no persiste ningún log | `waf.py` |
| 8 · Failure mode | — | **Falla abierto:** todo lo que no coincide con una regla pasa, sin alerta | `starter.py` (3/4 pasan) |

### 4.2 Parametrización de consultas

| Axis | Before | After control | Evidence |
|---|---|---|---|
| 1 · Threat model | Atacante remoto no autenticado | Sin cambios | — |
| 2 · Guarantee | Ninguna | **La entrada del usuario no puede alterar la estructura de la consulta, para ninguna entrada**, **si** todo query pasa los datos como parámetros (sin concatenación ni identificadores dinámicos) | `parameterized_login` |
| 3 · Coverage | Los 8 payloads funcionaban contra el sink vulnerable | **0/8 inyecciones exitosas.** Ver advertencia abajo sobre los 2 payloads XSS | `count_injection_successes` |
| **4 · Bypass** | — | Ninguno encontrado. Argumento: no hay camino de la entrada a la estructura del query. Se rompería con una concatenación olvidada o con SQLi de segundo orden, que este lab no cubre | `test_parameterization_guarantee_holds` |
| 5 · FP cost | 0 % | 0 por construcción: `o'brien` es solo un string. **No se midió con credenciales reales** | — |
| 6 · Op cost | — | No medido. Cambio de código, sin tuning continuo | — |
| 7 · Observability | — | No registra nada por sí misma. Un intento de inyección simplemente falla sin dejar rastro | — |
| 8 · Failure mode | — | Falla **abierto por consulta:** una sola consulta sin parametrizar sigue siendo vulnerable y nada alerta | — |

> **Advertencia sobre el 0/8.** De los 8 payloads, 2 son XSS (`<script>`, `<img onerror>`).
> La parametrización protege contra SQLi, no contra XSS. Eso se defiende con
> codificación de salida y CSP. Que esos 2 payloads "fallen" en `parameterized_login`
> solo significa que no son usernames válidos, no que el XSS esté mitigado. La garantía
> real aplica a los **6 payloads SQLi**.

### 4.3 WAF como detección

| Axis | Resultado |
|---|---|
| Guarantee | Ninguna, pero aporta **visibilidad** (alguien está sondeando, con qué) |
| Coverage | 1/3 de los bypasses marcados por la regla dada |
| Bypass | `onerror` sin comilla y ancho cero evaden `anomaly()` |
| FP / carga de analista | Cada marca es tiempo de analista. 0/26 por lectura manual (por verificar) |

---

## 5. Pregunta extra: ¿una regla para `OR 'a'='a'` sin falsos positivos?

**Sí, para este caso concreto.** Una regla anclada en comillas:

```python
(?i)'\s*or\s*'[^']*'\s*=\s*'
```

Coincide con `admin' OR 'a'='a'--` y no toca "director of operations or equivalent
role", porque el texto legítimo no tiene comillas alrededor de `or`.

**Por qué el tradeoff no tiene un punto limpio:**

1. **Se evade con otra forma equivalente:** `OR "a"="a"`, `OR 'a' LIKE 'a'`, `OR true`,
   `OR 2>1`, `OR x=x`. Todas tienen la misma intención y ninguna coincide.
2. **Para cubrirlas hay que quitar el ancla de comillas**, y una regla genérica como
   `\bor\b\s+\S+\s*[=<>]` empieza a coincidir con frases normales que contienen la
   palabra `or` seguida de una comparación.
3. **La causa de fondo:** la gramática de SQL y el inglés cotidiano se solapan. Cualquier
   patrón que cubra el espacio de ataque también cubre texto legítimo, y cualquier
   patrón que evite el texto legítimo deja huecos. Estás enumerando maldad en un espacio
   abierto.

Esta regla no se ejecutó contra el corpus completo, así que no puedo afirmar que tenga
0 falsos positivos sobre las 26 entradas (por lectura, ninguna contiene `'`…`or`…`'`).

---

## 6. Honesty clause — *Where we may have been unfair, and what we did not test*

- **Un "bypass" no lo era.** `UnIoN SeLeCt` fue bloqueado. Reportar 4/4 bypasses
  habría sido incorrecto; el número real es 3/4.
- **Muestra pequeña.** Solo hay 4 + 4 payloads de ataque. El rubric pide ≥ 20 para el
  axis 3. Las cifras son una muestra, no el espacio de ataque.
- **Esfuerzo asimétrico.** El WAF no se afinó (4 reglas del notebook), mientras que los
  bypasses vienen pre-escritos y elegidos para evadirlo. Un WAF real con CRS completo y
  tuning se comportaría mejor, y un atacante con más tiempo, peor.
- **Los payloads vienen de la clase.** Fueron escritos en la misma semana que las
  reglas; no es una corpus independiente (riesgo de corpus copiado, como advierte el
  rubric).
- **El corpus benigno es pequeño y está diseñado para provocar.** 26 entradas con
  lenguaje "parecido a ataque" a propósito. El 7.7 % no es una tasa de falsos
  positivos de tráfico real, que probablemente sería mucho menor.
- **La parametrización es un modelo.** `parameterized_login` usa un diccionario de
  Python, no SQLite con placeholders reales. Demuestra el principio, no la
  implementación de un driver.
- **0/8 mezcla SQLi y XSS.** La garantía de la parametrización cubre solo los 6
  payloads SQLi (ver sección 4.2).
- **No se midió costo operacional** (latencia, tuning) ni para el WAF ni para la
  parametrización.
- **No se verificó qué bypass concreto filtra el canary.** El test confirma que al menos
  uno lo hace, pero no se registró cuál.
- **Detección no medida sobre benigno.** El 0/26 de `anomaly()` es por lectura manual.
- **No probado:** SQLi de segundo orden, identificadores dinámicos (`ORDER BY`),
  otros encodings (URL, doble URL, Unicode), ni mutaciones automáticas (fuzzing).

---

## 7. Cómo reproducir

Desde `studios/week-07/`:

```powershell
python3 waf.py          # motor dado: 3/4 pasan, 26 benignos cargados
python3 starter.py      # las 5 mediciones
python3 test_waf.py     # 6 tests: debe terminar con "all 6 tests pass"
```

> En PowerShell, `echo $?` imprime `True` si el último comando tuvo éxito (como en tus
> ejecuciones). El código de salida numérico se ve con `echo $LASTEXITCODE` (debe ser 0).

**Verificar los puntos marcados "por verificar"** (falsos positivos de `anomaly()` y de
la regla extendida):

```powershell
python3 -c "from waf import *; import re; print([b for b in load_benign() if anomaly(b)])"
```

Debe imprimir `[]`. Para probar la regla extendida `EXT` de la sección 3, pégala en un
script y evalúala sobre `load_benign()` y sobre `BYPASSES`.

**Qué archivo respalda cada cifra:** `starter.py` (mediciones), `test_waf.py`
(aserciones), `waf.py` (reglas y corpus), `projects/duel-2-web/benign_traffic.json`
(26 entradas benignas).
