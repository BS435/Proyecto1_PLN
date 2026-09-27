import nltk
import random

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

try:
    nltk.data.find('corpora/omw-2.0')
except LookupError:
    nltk.download('omw-2.0')

from nltk.corpus import wordnet as wn

categories_en = [
    'dog', 'piano', 'car', 'computer', 'movie',
    'snake', 'bicycle', 'restaurant', 'elephant', 'guitar'
]

categories_es = [
    'perro', 'gato', 'piano', 'computadora', 'serpiente',
    'bicicleta', 'guitarra', 'barco', 'tiburón', 'elefante'
]


def clean(candidates, secret_word):
    """Discards any candidate that contains the secret word inside it."""
    secret_word = secret_word.lower()
    result = []
    for l in candidates:
        clean_l = l.replace('_', ' ')
        if secret_word not in clean_l.lower():
            result.append(clean_l)
    return result


def try_en(secret_word):
    secret_word_synset = wn.synsets(secret_word)[0]

    valid_hypernyms = clean(secret_word_synset.hypernyms()[0].lemma_names(), secret_word)
    hypernym = valid_hypernyms[0]

    hyponyms = []
    for h in secret_word_synset.hyponyms():
        valid = clean(h.lemma_names(), secret_word)
        if valid:
            hyponyms.append(valid[0])
        if len(hyponyms) == 2:
            break
    hyponym_1 = hyponyms[0]
    hyponym_2 = hyponyms[1]

    synonyms = clean(secret_word_synset.lemma_names(), secret_word)
    synonym_1 = synonyms[0]
    synonym_2 = synonyms[1]

    return {
        "hint_1": hypernym, "hint_2": hyponym_1, "hint_3": hyponym_2,
        "hint_4": synonym_1, "hint_5": synonym_2, "answer": secret_word
    }


def try_es(secret_word):
    secret_word_synset = wn.synsets(secret_word, lang='spa', pos=wn.NOUN)[0]

    valid_hypernyms = clean(secret_word_synset.hypernyms()[0].lemma_names(lang='spa'), secret_word)
    hypernym = valid_hypernyms[0]

    hyponyms = []
    for h in secret_word_synset.hyponyms():
        valid = clean(h.lemma_names(lang='spa'), secret_word)
        if valid:
            hyponyms.append(valid[0])
        if len(hyponyms) == 2:
            break
    hyponym_1 = hyponyms[0]
    hyponym_2 = hyponyms[1]

    synonyms = clean(secret_word_synset.lemma_names(lang='spa'), secret_word)
    synonym_1 = synonyms[0]
    synonym_2 = synonyms[1]

    return {
        "hint_1": hypernym, "hint_2": hyponym_1, "hint_3": hyponym_2,
        "hint_4": synonym_1, "hint_5": synonym_2, "answer": secret_word
    }


def get_words_en():
    while True:
        secret_word = random.choice(categories_en)
        try:
            return try_en(secret_word)
        except IndexError:
            continue  # this word didn't give enough clean hints, try another


def get_words_es():
    while True:
        secret_word = random.choice(categories_es)
        try:
            return try_es(secret_word)
        except IndexError:
            continue


def get_round(language='en'):
    if language == 'en':
        return get_words_en()
    elif language == 'es':
        return get_words_es()
    else:
        raise ValueError("language must be 'en' or 'es'")


round_data = get_round('es')
print(round_data)
round_data = get_round('en')
print(round_data)