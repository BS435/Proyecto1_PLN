let game = null;
let currentHint = null;

const hint = document.getElementById("hint");
const relation = document.getElementById("relation");
const previousHints = document.getElementById("previous-hints");
const answer = document.getElementById("answer");
const message = document.getElementById("message");
const attempts = document.getElementById("attempts");
const score = document.getElementById("score");
const language = document.getElementById("language");
const languageNote = document.getElementById("language-note");
const guessButton = document.getElementById("guess-button");
const newGameButton = document.getElementById("new-game-button");

const NOMBRES_IDIOMA = { es: "español", en: "inglés" };

async function newGame() {
    try {
        const response = await fetch(`/nueva-partida?idioma=${language.value}`);

        if (!response.ok) {
            throw new Error("No se pudo obtener la partida.");
        }

        game = await response.json();

        currentHint = null;
        previousHints.innerHTML = "";
        answer.value = "";
        answer.disabled = false;
        guessButton.disabled = false;
        message.textContent = "";

        const nombre = NOMBRES_IDIOMA[game.idioma];
        languageNote.textContent =
            `Las pistas se muestran en ${nombre} y la respuesta se escribe en ${nombre}.`;

        actualizarPuntaje(game);
        showHint(game.pista);
        answer.focus();

    } catch (error) {
        console.error(error);
        message.textContent = "No se pudo iniciar la partida.";
    }
}

function showHint(pista) {
    if (currentHint) {
        const item = document.createElement("li");
        item.textContent = `${currentHint.texto} (${currentHint.relacion})`;
        previousHints.appendChild(item);
    }

    currentHint = pista;

    attempts.textContent = `Pista ${pista.numero} de ${game.total}`;
    hint.textContent = pista.texto;
    relation.textContent = pista.relacion;
}

function actualizarPuntaje(datos) {
    score.textContent = `Puntaje: ${datos.puntaje_total} (${datos.partidas} partidas)`;
}

function terminarPartida(resultado) {
    answer.disabled = true;
    guessButton.disabled = true;
    currentHint = null;
    actualizarPuntaje(resultado);
    newGameButton.focus();
}

async function checkAnswer() {

    if (!game) {
        message.textContent = "La partida todavía no ha iniciado.";
        return;
    }

    const userAnswer = answer.value.trim();

    if (userAnswer === "") {
        message.textContent = "Escribe una respuesta.";
        return;
    }

    try {
        const response = await fetch("/adivinar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ respuesta: userAnswer }),
        });

        const resultado = await response.json();

        if (!response.ok) {
            message.textContent = resultado.error;
            return;
        }

        if (resultado.correcta) {
            message.textContent =
                `¡Correcto! 🎉 Era "${resultado.respuesta}". +${resultado.puntos} puntos.`;
            terminarPartida(resultado);
            return;
        }

        answer.value = "";

        if (!resultado.terminada) {
            message.textContent = "Respuesta incorrecta. Aquí tienes otra pista.";
            showHint(resultado.pista);
        } else {
            message.textContent =
                `Se acabaron las pistas. La respuesta era: ${resultado.respuesta}.`;
            terminarPartida(resultado);
        }

    } catch (error) {
        console.error(error);
        message.textContent = "No se pudo revisar la respuesta.";
    }
}

guessButton.addEventListener("click", checkAnswer);

answer.addEventListener("keydown", function(event) {

    if (event.key === "Enter") {
        checkAnswer();
    }

});

newGameButton.addEventListener("click", newGame);
language.addEventListener("change", newGame);

newGame();
