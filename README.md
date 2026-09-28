# WordNet Guess — Pinpoint con WordNet

Proyecto 1 de Procesamiento de Lenguaje Natural. Juego de adivinanza estilo *Pinpoint*:
el sistema elige una categoría oculta y genera **automáticamente con WordNet** 5 pistas que
se revelan de la más general a la más reveladora. Gana quien adivine con menos pistas.

## Cómo ejecutarlo

Requiere Python 3.9 o superior (probado con 3.12).

```
pip install -r requirements.txt
python app.py
```

En Mac/Linux usar `pip3` y `python3` si `python` no apunta a Python 3.

Abrir <http://127.0.0.1:5000>. La primera vez se descargan los corpus `wordnet` y `omw-2.0`
de NLTK (requiere internet). El arranque tarda unos segundos porque se valida el banco de categorías.

Si en Mac la descarga falla con `CERTIFICATE_VERIFY_FAILED`, ejecutar una vez
`/Applications/Python 3.x/Install Certificates.command` (según la versión instalada).

## Mecánica

1. Se elige al azar una categoría del banco (`BANCO` en `pistas.py`).
2. Se muestra la pista 1. El jugador escribe su respuesta.
3. Si acierta, la partida termina y gana `6 − número de pista` puntos (5 en la pista 1, 1 en la pista 5).
4. Si falla, se revela la siguiente pista. Tras fallar la pista 5 se muestra la respuesta y gana 0 puntos.
5. El puntaje se acumula entre partidas; el botón **Nueva partida** inicia otra ronda.

## Uso de WordNet (`pistas.py`)

Cada pista indica en pantalla de qué relación proviene.

| Pista | Relación | Cómo se obtiene |
|---|---|---|
| 1 | Hiperónimo lejano | Segundo ancestro con lema en el idioma (`hypernyms()` recorrido hacia arriba) |
| 2 | Hiperónimo directo | Primer ancestro con lema en el idioma |
| 3 | Hipónimo | `hyponyms()` — se prefieren los más frecuentes (conteos de SemCor, `lemma.count()`) |
| 4 | Hipónimo | Otro hipónimo distinto |
| 5 | Sinónimo | Otro lema del **mismo synset** (`lemma_names()`); si el idioma no tiene, un tercer hipónimo |

Ejemplo (`dog.n.01`, inglés): *canid → domestic animal → cur → griffon → Canis familiaris*.

Detalles:
- El banco usa **ids de synset** (`'dog.n.01'`) en lugar de palabras sueltas para fijar el sentido correcto.
- Se descartan las pistas que "delatan" la respuesta: si comparten raíz con la palabra secreta
  (`perro de caza` para `perro`) o repiten una pista anterior.
- Al arrancar se prueban todas las categorías en ambos idiomas y sólo se juega con las que dan 5 pistas
  (hoy 34 de 40; las demás, como `piano` o `guitar`, no tienen suficientes hipónimos o sinónimos).

## Lematización y stemming (`normalizar.py`)

La respuesta del jugador y las respuestas aceptadas pasan por el mismo proceso antes de compararse:

1. **Funciones de cadenas:** minúsculas, eliminación de acentos (`unicodedata`), de puntuación y de
   `_`/`-`, colapso de espacios, separación en tokens y eliminación de artículos/preposiciones
   (`el`, `de`, `the`, `of`…).
2. **Normalización morfológica por token:**
   - Inglés: `WordNetLemmatizer` (sustantivos, resuelve plurales irregulares como *mice → mouse*) seguido de `PorterStemmer`.
   - Español: `SnowballStemmer('spanish')`, ya que NLTK no incluye lematizador para español.
3. Se compara la **secuencia de raíces**, lo que permite respuestas de varias palabras.

Se aceptan como correctas la palabra secreta y **cualquier sinónimo de su synset** que no se haya
mostrado como pista. Ejemplos aceptados para `perro`: `Perros`, `  PERRO!`, `el perro`,
`perro doméstico`, `can`; para `dog`: `Dogs`, `the domestic dogs`.

## Idiomas

Modalidad **inglés – español**, elegible con el selector de la página:

- **Español:** pistas en español y respuesta en español (Open Multilingual WordNet, `lang='spa'`).
- **English:** pistas en inglés y respuesta en inglés (WordNet de Princeton).

Ambos idiomas usan el mismo synset, así que la categoría es la misma en los dos. La página indica
siempre en qué idioma se muestran las pistas y en cuál se espera la respuesta. Limitación conocida:
OMW en español tiene huecos, y algunas pistas pueden salir con un término en inglés o latín
(`craniate`, `drawknife`) porque así están en el recurso.

## Estructura

```
app.py            Servidor Flask: /nueva-partida y /adivinar. La respuesta nunca se envía al navegador.
pistas.py         Banco de categorías y generación de pistas con WordNet.
normalizar.py     Funciones de cadenas + lematización/stemming.
templates/        index.html
static/           script.js, style.css
requirements.txt
```
