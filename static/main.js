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
    const actionButtonsContainer = document.getElementById('action-buttons');
    const gameLog = document.getElementById('game-log');

    let state = {
        players: {},
        combat: null, // { combat_id, attacker_name, attacks: [] }
    };

    // --- LOGGING ---
    function log(message) {
        console.log(message);
        const formattedMessage = Array.isArray(message) ? message.join('\n') :
                               typeof message === 'object' ? JSON.stringify(message, null, 2) :
                               message;
        gameLog.innerHTML += formattedMessage + '\n';
        gameLog.scrollTop = gameLog.scrollHeight;
    }

    // --- API HELPERS ---
    async function apiCall(endpoint, method = 'GET', body = null) {
        const options = { method, headers: { 'Content-Type': 'application/json' } };
        if (body) options.body = JSON.stringify(body);
        try {
            const response = await fetch(`${API_PREFIX}${endpoint}`, options);
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || 'API request failed');
            return data;
        } catch (error) {
            log(`Error: ${error.message}`);
            // Si es un error de maná, no queremos que la UI se bloquee
            if (error.message.includes("suficiente maná")) {
                return { error: true, message: error.message };
            }
            state.combat = null; // Terminar combate si hay otro error
            updateCombatUI();
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
                li.textContent = `${p.name} (${p.role} L${p.level}) HP:${p.hp}/${p.max_hp} MP:${p.mp}/${p.max_mp}`;
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
        if (!name) { log('Por favor, introduce un nombre.'); return; }
        const newPlayer = await apiCall('/players/', 'POST', { name, role: playerRoleSelect.value });
        if (newPlayer) {
            log(`Jugador '${newPlayer.name}' creado.`);
            playerNameInput.value = '';
            refreshPlayers();
        }
    }

    async function handleStartCombat() {
        const player1 = player1Select.value;
        const player2 = player2Select.value;
        if (player1 === player2) { log('Un jugador no puede luchar consigo mismo.'); return; }
        
        log(`Iniciando combate: ${player1} vs ${player2}...`);
        const result = await apiCall('/combat/start', 'POST', { player1_name: player1, player2_name: player2 });
        if (result) {
            state.combat = { combat_id: result.combat_id, attacker_name: result.attacker_name, attacks: [] };
            log(result.message);
            updateCombatUI();
        }
    }

    async function handleTakeTurn(attackName) {
        if (!state.combat) return;
        const result = await apiCall('/combat/turn', 'POST', { ...state.combat, attack_name: attackName });
        if (result) {
            // Si es un error de maná, solo mostramos el mensaje y actualizamos la UI
            if (result.error) {
                log(result.message);
                updateCombatUI();
                return;
            }

            log(result.log);
            // Actualizar HP/MP en la lista de jugadores
            refreshPlayers(); 

            if (result.session_ended) {
                state.combat = null;
            } else {
                state.combat.attacker_name = result.next_turn;
            }
            updateCombatUI();
        }
    }

    async function updateCombatUI() {
        if (state.combat) {
            combatZone.classList.remove('hidden');
            const attackerName = state.combat.attacker_name;
            const attacker = state.players[attackerName];
            if (!attacker) return; // Esperar a que se actualicen los players
            
            turnInfo.textContent = `Turno de: ${attackerName} (MP: ${attacker.mp}/${attacker.max_mp})`;
            
            // Obtener ataques y generar botones
            const attacks = await apiCall(`/combat/attacks/${attackerName}`);
            if (!attacks) return;
            state.combat.attacks = attacks;
            
            actionButtonsContainer.innerHTML = ''; // Limpiar botones anteriores
            attacks.forEach(attack => {
                const button = document.createElement('button');
                button.textContent = `${attack.name} (${attack.cost} MP)`;
                button.title = `Tipo: ${attack.type}, Poder: ${attack.power}`;
                button.disabled = attacker.mp < attack.cost;
                button.addEventListener('click', () => handleTakeTurn(attack.name));
                actionButtonsContainer.appendChild(button);
            });
        } else {
            combatZone.classList.add('hidden');
        }
    }

    // --- EVENT LISTENERS ---
    createPlayerBtn.addEventListener('click', handleCreatePlayer);
    startCombatBtn.addEventListener('click', handleStartCombat);

    // Inicialización
    refreshPlayers();
});
