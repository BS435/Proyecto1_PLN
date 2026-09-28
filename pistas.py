import random

import nltk

for recurso in ('wordnet', 'omw-2.0'):
    try:
        nltk.data.find(f'corpora/{recurso}')
    except LookupError:
        nltk.download(recurso)

from nltk.corpus import wordnet as wn

from normalizar import forma_normal, limpiar

IDIOMAS_OMW = {'en': 'eng', 'es': 'spa'}

BANCO = {
    'dog.n.01': 'perro', 'cat.n.01': 'gato', 'horse.n.01': 'caballo',
    'elephant.n.01': 'elefante', 'shark.n.01': 'tiburón', 'snake.n.01': 'serpiente',
    'spider.n.01': 'araña', 'bee.n.01': 'abeja', 'bird.n.01': 'pájaro',
    'car.n.01': 'carro', 'truck.n.01': 'camión', 'bicycle.n.01': 'bicicleta',
    'airplane.n.01': 'avión', 'train.n.01': 'tren', 'boat.n.01': 'barco',
    'piano.n.01': 'piano', 'guitar.n.01': 'guitarra', 'drum.n.01': 'tambor',
    'computer.n.01': 'computadora', 'movie.n.01': 'película', 'book.n.01': 'libro',
    'knife.n.01': 'cuchillo', 'chair.n.01': 'silla', 'table.n.02': 'mesa',
    'hat.n.01': 'sombrero', 'shoe.n.01': 'zapato', 'tree.n.01': 'árbol',
    'flower.n.01': 'flor', 'apple.n.01': 'manzana', 'cheese.n.01': 'queso',
    'wine.n.01': 'vino', 'soup.n.01': 'sopa', 'cake.n.03': 'pastel',
    'restaurant.n.01': 'restaurante', 'hospital.n.01': 'hospital', 'church.n.02': 'iglesia',
    'doctor.n.01': 'médico', 'teacher.n.01': 'maestro', 'lawyer.n.01': 'abogado',
    'singer.n.01': 'cantante',
}

RELACION = {
    'hiperonimo': 'Hiperónimo',
    'hiponimo': 'Hipónimo',
    'sinonimo': 'Sinónimo',
}


class PistasInsuficientes(Exception):
    pass


def lemas(synset, idioma):
    return [l.replace('_', ' ') for l in synset.lemma_names(IDIOMAS_OMW[idioma])]


def palabra_secreta(id_synset, idioma):
    if idioma == 'es':
        return BANCO[id_synset]
    return lemas(wn.synset(id_synset), 'en')[0]


def _delata(candidato, raices_secretas, idioma):
    return bool(set(forma_normal(candidato, idioma)) & raices_secretas)


def _mejor_lema(candidatos):
    return min(candidatos, key=lambda l: (l[0].isupper(), len(l.split()), len(l)))


def _lemas_validos(synset, idioma, raices_secretas, usadas):
    return [l for l in lemas(synset, idioma)
            if not _delata(l, raices_secretas, idioma) and limpiar(l) not in usadas]


HIPONIMOS_CONOCIDOS = 8


def _popularidad(synset):
    return sum(l.count() for l in synset.lemmas()) - (0.5 if synset.lemma_names()[0][0].isupper() else 0)


def _ancestros(synset):
    visitados, cola = [], list(synset.hypernyms())
    while cola:
        actual = cola.pop(0)
        if actual not in visitados:
            visitados.append(actual)
            cola.extend(actual.hypernyms())
    return visitados


def generar_pistas(id_synset, idioma, aleatorio=random):
    synset = wn.synset(id_synset)
    secreta = palabra_secreta(id_synset, idioma)
    raices_secretas = set(forma_normal(secreta, idioma))
    usadas = {limpiar(secreta)}
    pistas = []

    def agregar(texto, relacion):
        pistas.append({'texto': texto, 'relacion': relacion})
        usadas.add(limpiar(texto))

    hiperonimos = []
    for ancestro in _ancestros(synset):
        validos = _lemas_validos(ancestro, idioma, raices_secretas, usadas)
        if validos:
            hiperonimos.append(_mejor_lema(validos))
            usadas.add(limpiar(hiperonimos[-1]))
        if len(hiperonimos) == 2:
            break
    if len(hiperonimos) < 2:
        raise PistasInsuficientes(f'{id_synset}/{idioma}: faltan hiperónimos')
    for h in reversed(hiperonimos):
        agregar(h, RELACION['hiperonimo'])

    hiponimos = sorted(synset.hyponyms(), key=_popularidad, reverse=True)
    conocidos, resto = hiponimos[:HIPONIMOS_CONOCIDOS], hiponimos[HIPONIMOS_CONOCIDOS:]
    aleatorio.shuffle(conocidos)
    hiponimos = conocidos + resto

    def siguiente_hiponimo():
        while hiponimos:
            validos = _lemas_validos(hiponimos.pop(0), idioma, raices_secretas, usadas)
            if validos:
                return _mejor_lema(validos)
        return None

    for _ in range(2):
        h = siguiente_hiponimo()
        if h is None:
            raise PistasInsuficientes(f'{id_synset}/{idioma}: faltan hipónimos')
        agregar(h, RELACION['hiponimo'])

    sinonimos = _lemas_validos(synset, idioma, raices_secretas, usadas)
    if sinonimos:
        agregar(_mejor_lema(sinonimos), RELACION['sinonimo'])
    else:
        h = siguiente_hiponimo()
        if h is None:
            raise PistasInsuficientes(f'{id_synset}/{idioma}: sin sinónimo ni tercer hipónimo')
        agregar(h, RELACION['hiponimo'])

    mostradas = {limpiar(p['texto']) for p in pistas}
    aceptadas = {forma_normal(l, idioma) for l in lemas(synset, idioma) + [secreta]
                 if limpiar(l) not in mostradas}
    return pistas, aceptadas


def _banco_valido():
    validos = []
    for id_synset in BANCO:
        try:
            for idioma in IDIOMAS_OMW:
                generar_pistas(id_synset, idioma)
            validos.append(id_synset)
        except PistasInsuficientes:
            pass
    return validos


BANCO_VALIDO = _banco_valido()


def nueva_ronda(idioma):
    if idioma not in IDIOMAS_OMW:
        raise ValueError("el idioma debe ser 'en' o 'es'")
    id_synset = random.choice(BANCO_VALIDO)
    pistas, aceptadas = generar_pistas(id_synset, idioma)
    return {
        'synset': id_synset,
        'respuesta': palabra_secreta(id_synset, idioma),
        'pistas': pistas,
        'aceptadas': aceptadas,
    }
