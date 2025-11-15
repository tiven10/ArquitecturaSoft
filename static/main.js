document.addEventListener('DOMContentLoaded', () => {
    const API_PREFIX = '/api/v1';

    // Elementos de la UI
    const createPlayerBtn = document.getElementById('create-player-btn');
    const playerNameInput = document.getElementById('player-name');
    const playerRoleSelect = document.getElementById('player-role');
    const playerList = document.getElementById('player-list');
    const player1Select = document.getElementById('player1-select');
    const player2Select = document.getElementById('player2-select');
    const startCombatBtn = document.getElementById('start-combat-btn');
    const combatZone = document.getElementById('combat-zone');
    const turnInfo = document.getElementById('turn-info');
    const attackFisicoBtn = document.getElementById('attack-fisico-btn');
    const attackMagicoBtn = document.getElementById('attack-magico-btn');
    const gameLog = document.getElementById('game-log');

    let state = {
        players: {},
        combat: null, // { combat_id, attacker_name }
    };

    // --- LOGGING ---
    function log(message) {
        console.log(message);
        if (Array.isArray(message)) {
            gameLog.innerHTML += message.join('\n') + '\n';
        } else if (typeof message === 'object') {
            gameLog.innerHTML += JSON.stringify(message, null, 2) + '\n';
        } else {
            gameLog.innerHTML += message + '\n';
        }
        gameLog.scrollTop = gameLog.scrollHeight; // Auto-scroll
    }

    // --- API HELPERS ---
    async function apiCall(endpoint, method = 'GET', body = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };
        if (body) {
            options.body = JSON.stringify(body);
        }
        try {
            const response = await fetch(`${API_PREFIX}${endpoint}`, options);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'API request failed');
            }
            return await response.json();
        } catch (error) {
            log(`Error: ${error.message}`);
            return null;
        }
    }

    // --- LÓGICA DE LA APLICACIÓN ---
    async function refreshPlayers() {
        const players = await apiCall('/players/');
        if (players) {
            state.players = {};
            playerList.innerHTML = '';
            [player1Select, player2Select].forEach(sel => sel.innerHTML = '');
            
            players.forEach(p => {
                state.players[p.name] = p;
                const li = document.createElement('li');
                li.textContent = `${p.name} (${p.role} - Lvl ${p.level})`;
                playerList.appendChild(li);

                [player1Select, player2Select].forEach(sel => {
                    const option = document.createElement('option');
                    option.value = p.name;
                    option.textContent = p.name;
                    sel.appendChild(option);
                });
            });
        }
    }

    async function handleCreatePlayer() {
        const name = playerNameInput.value.trim();
        const role = playerRoleSelect.value;
        if (!name) {
            log('Por favor, introduce un nombre para el jugador.');
            return;
        }
        const newPlayer = await apiCall('/players/', 'POST', { name, role });
        if (newPlayer) {
            log(`Jugador '${newPlayer.name}' creado con éxito.`);
            playerNameInput.value = '';
            refreshPlayers();
        }
    }

    async function handleStartCombat() {
        const player1 = player1Select.value;
        const player2 = player2Select.value;
        if (player1 === player2) {
            log('Un jugador no puede luchar contra sí mismo.');
            return;
        }

        log(`Iniciando combate entre ${player1} y ${player2}...`);
        const result = await apiCall('/combat/start', 'POST', { player1_name: player1, player2_name: player2 });
        if (result) {
            state.combat = {
                combat_id: result.combat_id,
                attacker_name: result.message[1].split(' ')[4].replace('.', '')
            };
            log(result.message);
            updateCombatUI();
        }
    }

    async function handleTakeTurn(attackType) {
        if (!state.combat) return;
        
        log(`Turno de ${state.combat.attacker_name}, usando: ${attackType}`);
        const result = await apiCall('/combat/turn', 'POST', {
            combat_id: state.combat.combat_id,
            attacker_name: state.combat.attacker_name,
            attack_type: attackType
        });

        if (result) {
            log(result.log);

            const winnerMsg = result.log.find(msg => msg.includes('es el ganador'));
            if (winnerMsg) {
                state.combat = null;
                refreshPlayers(); // Actualizar niveles, etc.
            } else {
                const nextTurnMsg = result.log.find(msg => msg.includes('Ahora es el turno de'));
                if (nextTurnMsg) {
                    state.combat.attacker_name = nextTurnMsg.split(' ')[5].replace('.', '');
                }
            }
            updateCombatUI();
        }
    }

    function updateCombatUI() {
        if (state.combat) {
            combatZone.classList.remove('hidden');
            turnInfo.textContent = `Turno de: ${state.combat.attacker_name}`;
            [attackFisicoBtn, attackMagicoBtn].forEach(btn => btn.disabled = false);
        } else {
            combatZone.classList.add('hidden');
            [attackFisicoBtn, attackMagicoBtn].forEach(btn => btn.disabled = true);
        }
    }

    // --- EVENT LISTENERS ---
    createPlayerBtn.addEventListener('click', handleCreatePlayer);
    startCombatBtn.addEventListener('click', handleStartCombat);
    attackFisicoBtn.addEventListener('click', () => handleTakeTurn('Ataque Físico'));
    attackMagicoBtn.addEventListener('click', () => handleTakeTurn('Hechizo de Fuego'));

    // Inicialización
    refreshPlayers();
});
