import secrets

from flask import Flask, jsonify, render_template, request, session

from normalizar import es_correcta, forma_normal
from pistas import nueva_ronda

TOTAL_PISTAS = 5

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

rondas = {}


def ronda_actual():
    return rondas.get(session.get('ronda'))


def pista_publica(ronda):
    pista = ronda['pistas'][ronda['pista_actual']]
    return {'numero': ronda['pista_actual'] + 1, 'texto': pista['texto'], 'relacion': pista['relacion']}


def terminar(ronda, puntos):
    ronda['terminada'] = True
    session['puntaje'] = session.get('puntaje', 0) + puntos
    session['partidas'] = session.get('partidas', 0) + 1
    return {'puntos': puntos, 'respuesta': ronda['respuesta'],
            'puntaje_total': session['puntaje'], 'partidas': session['partidas']}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/nueva-partida")
def nueva_partida():
    idioma = request.args.get("idioma", "es")
    try:
        ronda = nueva_ronda(idioma)
    except ValueError as error:
        return jsonify({'error': str(error)}), 400

    ronda.update(idioma=idioma, pista_actual=0, terminada=False)
    rondas.pop(session.get('ronda'), None)
    id_ronda = secrets.token_hex(8)
    rondas[id_ronda] = ronda
    session['ronda'] = id_ronda

    return jsonify({'idioma': idioma, 'total': TOTAL_PISTAS, 'pista': pista_publica(ronda),
                    'puntaje_total': session.get('puntaje', 0), 'partidas': session.get('partidas', 0)})


@app.route("/adivinar", methods=["POST"])
def adivinar():
    ronda = ronda_actual()
    if ronda is None or ronda['terminada']:
        return jsonify({'error': 'No hay una partida en curso.'}), 400

    respuesta = (request.get_json(silent=True) or {}).get('respuesta', '')
    if not forma_normal(respuesta, ronda['idioma']):
        return jsonify({'error': 'Escribe una respuesta.'}), 400

    if es_correcta(respuesta, ronda['aceptadas'], ronda['idioma']):
        puntos = TOTAL_PISTAS - ronda['pista_actual']
        return jsonify({'correcta': True, 'terminada': True, **terminar(ronda, puntos)})

    ronda['pista_actual'] += 1
    if ronda['pista_actual'] == TOTAL_PISTAS:
        return jsonify({'correcta': False, 'terminada': True, **terminar(ronda, 0)})

    return jsonify({'correcta': False, 'terminada': False, 'pista': pista_publica(ronda)})


if __name__ == "__main__":
    app.run(debug=True)
