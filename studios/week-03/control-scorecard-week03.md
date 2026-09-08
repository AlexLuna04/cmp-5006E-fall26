# Control Scorecard — Week 3: Symmetric Crypto & Hashes

Rúbrica aplicada a las tres construcciones inseguras (ECB, CTR con nonce
reutilizado, `H(secret‖msg)`) y su corrección (CBC, CTR con nonce único, HMAC).

## Fila 1 — ECB vs CBC

| Axis | Before (ECB) | After control (CBC) | Evidence |
|------|--------|---------------|----------|
| Threat model | Atacante pasivo que observa el ciphertext, sin la clave | sin cambio | `data.py` (imagen con 2 regiones planas) |
| Guarantee | ECB promete confidencialidad **solo por bloque individual** | CBC promete confidencialidad del **mensaje completo**, encadenando cada bloque con el anterior | notebook, sección 1-2 |
| Coverage | 2/2 bloques distintos del plaintext se reflejan 1:1 en el ciphertext (100% de la estructura filtrada) | 96/96 bloques distintos — la estructura desaparece por completo | salida de `test_ecb_leaks_structure_cbc_hides_it` |
| **Bypass** | **Encontrado: no hace falta nada especial** — cualquier atacante que solo vea el ciphertext detecta las regiones repetidas (el "pingüino ECB") | CBC no tiene este bypass, pero introduce otros (padding oracle, IV predecible) fuera del alcance de esta semana | notebook, sección 2 |
| FP cost | n/a | n/a | — |
| Op cost | — | CBC añade una dependencia secuencial (no paralelizable), costo de cómputo similar | — |
| Observability | Ninguna alerta — el patrón es visible directamente en el ciphertext | igual, pero ya no hay patrón que observar | inspección visual / `distinct_blocks()` |
| Failure mode | **Falla silenciosamente**: el sistema "funciona" (cifra y descifra bien) mientras filtra estructura sin ningún error visible | mismo tipo de modo, pero sin el patrón — sigue siendo silencioso si se usa mal (ej. IV reutilizado) | — |

## Fila 2 — CTR con nonce reutilizado vs nonce único

| Axis | Before (nonce reusado) | After control (nonce único) | Evidence |
|------|--------|---------------|----------|
| Threat model | Atacante pasivo que observa dos ciphertexts cifrados bajo el mismo (key, nonce) | sin cambio | `data.py` (M1, M2) |
| Guarantee | CTR promete confidencialidad **si y solo si** el par (key, nonce) nunca se repite | Con nonce único por mensaje, la garantía se cumple | notebook, sección 3 / scorecard axis 2 |
| Coverage | 1/1 mensaje objetivo (`m2`) recuperado por completo conociendo `m1` | 0/1 — sin par repetido no hay cancelación de keystream posible | salida de `test_ctr_nonce_reuse_recovers_plaintext` |
| **Bypass** | **Encontrado**: `c1 ⊕ c2 = m1 ⊕ m2`, exactamente el two-time pad de la semana 2; con `crib-drag` se recupera sin conocer `m1` completo | Ningún bypass conocido si el nonce nunca se repite (garantía condicional, no absoluta) | `starter.py::recover_second_plaintext` |
| FP cost | n/a | n/a | — |
| Op cost | — | Ninguno — solo requiere disciplina operativa (contador, nonce aleatorio de suficiente tamaño) | — |
| Observability | Nada detecta la reutilización en tiempo real a menos que se audite explícitamente | se puede loggear/verificar unicidad de nonces por clave | — |
| Failure mode | **Falla silenciosamente y catastróficamente**: no hay error, solo texto plano recuperable | si se rompe la disciplina de nonce, vuelve a fallar silenciosamente — el control depende 100% de la condición | — |

## Fila 3 — `H(secret‖msg)` vs HMAC

| Axis | Before (`H(secret‖msg)`) | After control (HMAC) | Evidence |
|------|--------|---------------|----------|
| Threat model | Atacante que observa `(msg, tag)` válidos, conoce la longitud del secreto, pero no el secreto en sí | sin cambio | `data.py` (MAC_SECRET, MAC_MSG) |
| Guarantee | *Aparenta* autenticar ("solo quien tiene el secreto puede producir un tag válido") | Autentica genuinamente, sin extensión posible, mientras la clave se mantenga secreta | notebook, sección 4-5 |
| Coverage | 1/1 forja exitosa — tag válido para `msg‖pad‖extension` sin conocer el secreto | 0/1 — el intento ingenuo de "extender" no produce un tag válido | salida de `test_length_extension_breaks_bad_mac_guarantee` y `test_hmac_rejects_the_same_forgery` |
| **Bypass** | **Encontrado**: length-extension attack — el digest MD es el estado interno completo, se puede resumir el hashing desde el tag observado | Ningún bypass encontrado: HMAC anida el hashing, el estado interno intermedio nunca se expone | `starter.py::forge_extension` |
| FP cost | n/a | n/a | — |
| Op cost | — | Insignificante (una llamada extra a SHA-256 vs. la construcción ingenua) | — |
| Observability | El servidor acepta la forja como válida sin ningún indicio de anomalía | HMAC rechaza la forja, comportamiento correcto y verificable con `hmac.compare_digest` | — |
| Failure mode | **Falla abierta (fail-open)**: acepta datos no autorizados como legítimos, sin alertar a nadie | Falla cerrada: rechaza tags inválidos de forma consistente | `test_hmac_rejects_the_same_forgery` |

---

## Conclusión (para el debrief)

En los tres casos, **la primitiva (SHA-256, el cifrador de bloque) se mantuvo intacta**.
Lo que falló fue:

1. El **modo** (ECB no encadena bloques → filtra estructura).
2. La **disciplina operativa** (reutilizar un nonce en CTR → two-time pad).
3. La **construcción del MAC** (`H(secret‖msg)` expone el estado interno → length extension).

La corrección en los tres casos no fue "usar un hash/cifrador mejor", sino
**usar una construcción mejor** alrededor del mismo primitivo: CBC en vez de ECB,
disciplina de nonce único en vez de reutilización, y HMAC en vez de concatenación
ingenua.

## Honestidad — qué no se probó

- No se implementó el bonus de renderizar la imagen "pingüino" con matplotlib;
  la filtración de estructura se verificó solo por conteo de bloques distintos.
- El ataque de CTR asume que se conoce `m1` completo de antemano (crib conocido),
  no se hizo un crib-drag real partiendo de cero conocimiento del plaintext.
- No se midió el costo operacional real (latencia, CPU) de CBC/HMAC vs. las
  construcciones inseguras — se asume que es despreciable sin medición directa.
- No se evaluó qué pasa si además de reutilizar el nonce, se reutiliza también
  la clave en millones de mensajes (pregunta rápida del README) más allá de la
  discusión conceptual.