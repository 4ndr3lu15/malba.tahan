document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const introOverlay = document.getElementById('intro-overlay');
    const endOverlay = document.getElementById('end-overlay');
    const startBtn = document.getElementById('start-btn');
    const weighBtn = document.getElementById('weigh-btn');
    const identifyBtn = document.getElementById('identify-btn');
    const resetBtn = document.getElementById('reset-btn');
    const playAgainBtn = document.getElementById('play-again-btn');

    const messageArea = document.getElementById('message-area');
    const measurementCountSpan = document.getElementById('measurement-count');

    const stagingArea = document.getElementById('staging-area');
    const leftPanItems = document.querySelector('.left-pan .pan-items');
    const rightPanItems = document.querySelector('.right-pan .pan-items');

    const leftPan = document.getElementById('left-pan');
    const rightPan = document.getElementById('right-pan');

    const scaleBeam = document.getElementById('scale-beam');
    const leftPanWrapper = document.querySelector('.left-pan-wrapper');
    const rightPanWrapper = document.querySelector('.right-pan-wrapper');

    // Game State
    const TOTAL_BALLS = 8;
    const MAX_MEASUREMENTS = 2;
    let measurementsTaken = 0;
    let heavyBallId = null;
    let identifyMode = false;
    let balls = []; // Array of ball DOM elements indexed 0–7

    // Ball state tracking: 'staging' | 'left' | 'right'
    // Keys are always numbers (not strings) to avoid type ambiguity.
    let ballLocations = {};
    let selectedBallId = null;

    // Tracks whether the scale tilt is currently showing a weighing result.
    // Movements only reset the visual AFTER a new weighing has been set up.
    let scaleResultPending = false;

    // ------------------------------------------------------------------
    // Pan click disambiguation: distinguishes single click from double click.
    // A single click on a pan places the selected ball.
    // A double click on a pan returns ALL balls to staging.
    // Without this, the browser fires click THEN dblclick on a double click,
    // which would accidentally place a ball and immediately return it.
    // ------------------------------------------------------------------
    let panClickTimer = null;
    const PAN_CLICK_DELAY = 250; // ms — threshold between single and double click

    function handlePanSingleOrDouble(panSide) {
        if (panClickTimer !== null) {
            // Second click arrived within delay → it's a double click
            clearTimeout(panClickTimer);
            panClickTimer = null;
            handlePanDoubleClick();
        } else {
            // First click — wait to see if a second arrives
            panClickTimer = setTimeout(() => {
                panClickTimer = null;
                handlePanClick(panSide);
            }, PAN_CLICK_DELAY);
        }
    }

    // ------------------------------------------------------------------
    // Initialization
    // ------------------------------------------------------------------
    function initGame() {
        measurementsTaken = 0;
        identifyMode = false;
        scaleResultPending = false;

        // Clear any pending pan timer from a previous session
        if (panClickTimer !== null) {
            clearTimeout(panClickTimer);
            panClickTimer = null;
        }

        document.body.classList.remove('selection-mode');
        identifyBtn.classList.remove('active-mode');
        identifyBtn.textContent = "Identificar Bola Pesada";

        // Identify button is disabled until at least one weighing is done
        identifyBtn.disabled = true;

        updateStats();
        resetScaleVisuals();

        // Pick a random ball to be heavy
        heavyBallId = Math.floor(Math.random() * TOTAL_BALLS);

        createBalls();
        setMessage("Coloque bolas na balança. Clique em uma esfera e depois em um dos pratos (sempre 2 cliques).", "");
        weighBtn.disabled = true;
    }

    function createBalls() {
        stagingArea.innerHTML = '';
        leftPanItems.innerHTML = '';
        rightPanItems.innerHTML = '';
        balls = [];
        ballLocations = {};
        selectedBallId = null;

        for (let i = 0; i < TOTAL_BALLS; i++) {
            const ball = document.createElement('div');
            ball.classList.add('ball');
            ball.textContent = i + 1; // Visual numbers 1–8
            ball.dataset.id = i;

            // Weight logic: normal ball = 10, heavy ball = 11 (purely internal)
            ball.addEventListener('click', () => handleBallClick(i, ball));

            stagingArea.appendChild(ball);
            balls.push(ball);
            ballLocations[i] = 'staging';
        }
    }

    // ------------------------------------------------------------------
    // Interaction Logic
    // ------------------------------------------------------------------

    /**
     * handleBallClick — called on every ball click.
     *
     * Mechanic rules:
     *  - In identify mode: the click is a guess.
     *  - In staging: first click selects; clicking the same ball deselects.
     *    After a ball is selected the player must click a PAN (2nd click) to
     *    move it — clicking another staging ball just changes the selection.
     *  - On a pan: clicking a pan-ball counts as the first click toward
     *    returning it. The player must click the ball AGAIN (second click on
     *    the same ball) to confirm returning it to staging.
     *    This mirrors the "2 clicks to move" rule symmetrically.
     */
    function handleBallClick(id, ballElement) {
        if (identifyMode) {
            handleIdentification(id);
            return;
        }

        const currentLocation = ballLocations[id];

        if (currentLocation === 'staging') {
            if (selectedBallId === id) {
                // Second click on the same staged ball → deselect
                ballElement.classList.remove('selected');
                selectedBallId = null;
                setMessage("Seleção removida.", "");
            } else {
                // Select this ball (deselect the previous one if any)
                if (selectedBallId !== null) {
                    balls[selectedBallId].classList.remove('selected');
                }
                ballElement.classList.add('selected');
                selectedBallId = id;
                setMessage(`Bola ${id + 1} selecionada. Clique no prato esquerdo ou direito para colocar.`, "");
            }
        } else {
            // Ball is on a pan.
            // First click on a pan-ball: select it (shows intent to return).
            // Second click on the SAME pan-ball: actually return it to staging.
            if (selectedBallId === id) {
                // Confirmed second click → return to staging
                ballElement.classList.remove('selected');
                selectedBallId = null;
                moveBall(id, 'staging');
                setMessage(`Bola ${id + 1} devolvida à área de preparação.`, "");
            } else {
                // First click on this pan-ball — select it and deselect previous
                if (selectedBallId !== null) {
                    balls[selectedBallId].classList.remove('selected');
                }
                ballElement.classList.add('selected');
                selectedBallId = id;
                setMessage(`Bola ${id + 1} selecionada no prato. Clique nela novamente para devolver à área de preparação.`, "");
            }
        }
    }

    /**
     * handlePanClick — fires on a confirmed single click on a pan.
     * Places the currently selected ball onto that pan (if any is selected).
     */
    function handlePanClick(panSide) {
        if (identifyMode) return;

        if (selectedBallId !== null) {
            // Only move a staged ball to the pan; ignore if the selected ball
            // is already on a pan (that interaction is handled by handleBallClick).
            if (ballLocations[selectedBallId] === 'staging') {
                moveBall(selectedBallId, panSide);
                balls[selectedBallId].classList.remove('selected');
                selectedBallId = null;
            }
        }
    }

    /**
     * handlePanDoubleClick — fires on a confirmed double click on EITHER pan.
     * Returns ALL balls from both pans to the staging area.
     */
    function handlePanDoubleClick() {
        if (identifyMode) return;

        const idsOnScale = Object.keys(ballLocations)
            .map(Number)
            .filter(id => ballLocations[id] === 'left' || ballLocations[id] === 'right');

        idsOnScale.forEach((id) => {
            if (selectedBallId === id) {
                balls[id].classList.remove('selected');
                selectedBallId = null;
            }
            moveBall(id, 'staging');
        });

        if (idsOnScale.length > 0) {
            setMessage("Todas as bolas foram devolvidas à área de preparação.", "");
        }
    }

    /**
     * moveBall — updates location state and re-parents the DOM element.
     * Does NOT reset the scale visuals; that only happens when a NEW weighing
     * is triggered (scaleResultPending is cleared in performWeighing).
     */
    function moveBall(id, destination) {
        const ballElement = balls[id];
        ballLocations[id] = destination;

        ballElement.remove(); // Remove from current parent

        if (destination === 'left') {
            leftPanItems.appendChild(ballElement);
        } else if (destination === 'right') {
            rightPanItems.appendChild(ballElement);
        } else {
            stagingArea.appendChild(ballElement);
        }

        // If the player moves a ball after a weighing, clear the tilt so the
        // scale reflects the new (not-yet-weighed) state.
        if (scaleResultPending) {
            scaleResultPending = false;
            resetScaleVisuals();
        }

        checkWeighButtonState();
    }

    function checkWeighButtonState() {
        // Never re-enable Pesar if all measurements are already used
        if (measurementsTaken >= MAX_MEASUREMENTS) {
            weighBtn.disabled = true;
            return;
        }

        const leftCount = Object.values(ballLocations).filter(loc => loc === 'left').length;
        const rightCount = Object.values(ballLocations).filter(loc => loc === 'right').length;

        if (leftCount > 0 && leftCount === rightCount) {
            weighBtn.disabled = false;
            setMessage("Os pratos têm a mesma quantidade de esferas. Pronto para pesar.", "success");
        } else {
            weighBtn.disabled = true;
            if (leftCount > 0 || rightCount > 0) {
                setMessage("Quantidade desigual de esferas. Coloque o mesmo número em cada lado.", "error");
            } else {
                setMessage("Coloque a mesma quantidade de esferas em cada lado antes de pesar.", "");
            }
        }
    }

    // ------------------------------------------------------------------
    // Weighing Logic
    // ------------------------------------------------------------------
    function performWeighing() {
        if (measurementsTaken >= MAX_MEASUREMENTS) {
            setMessage("Você já usou todas as pesagens! Identifique a bola mais pesada.", "warning");
            return;
        }

        const leftBalls = Object.keys(ballLocations).map(Number).filter(id => ballLocations[id] === 'left');
        const rightBalls = Object.keys(ballLocations).map(Number).filter(id => ballLocations[id] === 'right');

        let leftWeight = leftBalls.length * 10;
        let rightWeight = rightBalls.length * 10;

        // Add extra weight if the heavy ball is on a pan
        if (leftBalls.includes(heavyBallId)) leftWeight += 1;
        if (rightBalls.includes(heavyBallId)) rightWeight += 1;

        measurementsTaken++;
        updateStats();

        // Show tilt and mark that a result is now displayed
        scaleResultPending = true;
        tiltScale(leftWeight, rightWeight);

        if (measurementsTaken >= MAX_MEASUREMENTS) {
            weighBtn.disabled = true;
            identifyBtn.disabled = false;
            setMessage(`Pesagem ${measurementsTaken} concluída. Agora você deve identificar qual esfera é a mais pesada!`, "warning");
            // Auto-activate identify mode after the animation settles
            setTimeout(() => {
                if (!identifyMode) toggleIdentifyMode();
            }, 1500);
        } else {
            identifyBtn.disabled = false;
            if (leftWeight > rightWeight) {
                setMessage("O lado esquerdo está mais pesado.", "success");
            } else if (rightWeight > leftWeight) {
                setMessage("O lado direito está mais pesado.", "success");
            } else {
                setMessage("Os dois lados estão em equilíbrio.", "success");
            }
        }
    }

    function tiltScale(leftWeight, rightWeight) {
        let angle = 0;
        if (leftWeight > rightWeight) angle = -15; // Heavier left → beam tips left
        else if (rightWeight > leftWeight) angle = 15;  // Heavier right → beam tips right

        scaleBeam.style.transform = `rotate(${angle}deg)`;

        // Counter-rotate pan wrappers to keep pans level
        leftPanWrapper.style.transform = `rotate(${-angle}deg)`;
        rightPanWrapper.style.transform = `rotate(${-angle}deg)`;
    }

    function resetScaleVisuals() {
        scaleBeam.style.transform = `rotate(0deg)`;
        leftPanWrapper.style.transform = `rotate(0deg)`;
        rightPanWrapper.style.transform = `rotate(0deg)`;
    }

    // ------------------------------------------------------------------
    // Identification Logic
    // ------------------------------------------------------------------
    function toggleIdentifyMode() {
        identifyMode = !identifyMode;

        if (identifyMode) {
            document.body.classList.add('selection-mode');
            identifyBtn.classList.add('active-mode');
            identifyBtn.textContent = "Cancelar Identificação";

            // Clear any pending ball selection
            if (selectedBallId !== null) {
                balls[selectedBallId].classList.remove('selected');
                selectedBallId = null;
            }

            balls.forEach(b => b.classList.add('identify-hover'));
            setMessage("Selecione a bola que você acha que é a mais pesada!", "warning");

            // Disable Pesar while identifying
            weighBtn.disabled = true;
        } else {
            document.body.classList.remove('selection-mode');
            identifyBtn.classList.remove('active-mode');
            identifyBtn.textContent = "Identificar Bola Pesada";
            balls.forEach(b => b.classList.remove('identify-hover'));

            // Re-evaluate weigh button — respects measurement limit
            checkWeighButtonState();

            if (measurementsTaken >= MAX_MEASUREMENTS) {
                setMessage("Identificação cancelada. Você usou todas as pesagens — identifique a bola.", "warning");
            } else {
                setMessage("Identificação cancelada. Continue pesando.", "");
            }
        }
    }

    function handleIdentification(guessedId) {
        if (guessedId === heavyBallId) {
            endGame(true, `Vitória! A bola ${guessedId + 1} realmente é a mais pesada.`);
        } else {
            endGame(false, `Fracasso! A bola ${guessedId + 1} não é a mais pesada. O Sultão está descontente.`);
        }
    }

    // ------------------------------------------------------------------
    // UI Updates
    // ------------------------------------------------------------------
    function updateStats() {
        measurementCountSpan.textContent = measurementsTaken;
    }

    function setMessage(text, type) {
        messageArea.textContent = text;
        messageArea.className = 'messages';
        if (type) messageArea.classList.add(type);
    }

    // ------------------------------------------------------------------
    // End Game
    // ------------------------------------------------------------------
    function endGame(isWin, msg) {
        const endTitle = document.getElementById('end-title');
        const endMessage = document.getElementById('end-message');

        endTitle.textContent = isWin ? "Vitória!" : "Derrota!";
        endTitle.style.color = isWin ? "var(--gold)" : "var(--accent-red)";
        endMessage.textContent = msg;

        endOverlay.classList.remove('hidden');
    }

    // ------------------------------------------------------------------
    // Event Listeners
    // ------------------------------------------------------------------
    startBtn.addEventListener('click', () => {
        introOverlay.classList.add('hidden');
        initGame();
    });

    resetBtn.addEventListener('click', initGame);

    playAgainBtn.addEventListener('click', () => {
        endOverlay.classList.add('hidden');
        initGame();
    });

    // Use unified single/double-click handler for both pans.
    // The native 'dblclick' event is NOT used — the disambiguation timer
    // handles both cases to prevent the click-then-dblclick ordering bug.
    leftPan.addEventListener('click', () => handlePanSingleOrDouble('left'));
    rightPan.addEventListener('click', () => handlePanSingleOrDouble('right'));

    weighBtn.addEventListener('click', performWeighing);
    identifyBtn.addEventListener('click', toggleIdentifyMode);

    // Clicking the staging area background while a staged ball is selected
    // deselects it (provides a way to cancel a selection without moving a ball).
    stagingArea.addEventListener('click', (e) => {
        if (e.target === stagingArea && selectedBallId !== null) {
            balls[selectedBallId].classList.remove('selected');
            selectedBallId = null;
            setMessage("Seleção removida.", "");
        }
    });
});
