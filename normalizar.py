import re
import string
import unicodedata

from nltk.stem import PorterStemmer, SnowballStemmer, WordNetLemmatizer

_lematizador_en = WordNetLemmatizer()
_stemmer_en = PorterStemmer()
_stemmer_es = SnowballStemmer('spanish')

PALABRAS_VACIAS = {
    'en': {'a', 'an', 'the', 'of'},
    'es': {'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'del'},
}


def quitar_acentos(texto):
    descompuesto = unicodedata.normalize('NFD', texto)
    return ''.join(c for c in descompuesto if unicodedata.category(c) != 'Mn')


def limpiar(texto):
    texto = texto.replace('_', ' ').replace('-', ' ')
    texto = quitar_acentos(texto.lower())
    texto = texto.translate(str.maketrans('', '', string.punctuation + '¿¡'))
    return re.sub(r'\s+', ' ', texto).strip()


def tokens(texto, idioma):
    return [t for t in limpiar(texto).split() if t not in PALABRAS_VACIAS[idioma]]


def raiz(token, idioma):
    if idioma == 'en':
        return _stemmer_en.stem(_lematizador_en.lemmatize(token, pos='n'))
    return _stemmer_es.stem(token)


def forma_normal(texto, idioma):
    return tuple(raiz(t, idioma) for t in tokens(texto, idioma))


def es_correcta(respuesta, aceptadas, idioma):
    normal = forma_normal(respuesta, idioma)
    return bool(normal) and normal in aceptadas
