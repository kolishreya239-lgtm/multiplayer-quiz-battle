/**
 * QUIZ CLASH - LOBBY SCRIPT
 * Manages Socket.IO lobby state, ready toggles, host controls, and comms
 */

let socket = null;
let isHost = false;
let myPlayerState = null;

document.addEventListener('DOMContentLoaded', () => {
  initLobbySocket();
});

function initLobbySocket() {
  socket = io();

  socket.on('connect', () => {
    // Join room lobby on server
    socket.emit('join_lobby', { room_code: window.ROOM_CODE });
  });

  socket.on('lobby_updated', roomData => {
    renderLobby(roomData);
  });

  socket.on('player_joined', data => {
    showToast(`${data.username} joined the lobby!`, 'info');
    appendChatMessage('System', `${data.username} connected.`, '#00e5ff');
    window.soundEngine.play('click');
  });

  socket.on('player_left', data => {
    showToast(`${data.username} left the lobby.`, 'warning');
    appendChatMessage('System', `${data.username} disconnected.`, '#ff2a6d');
  });

  socket.on('chat_received', data => {
    appendChatMessage(data.sender, data.message, '#f8fafc', data.timestamp);
    window.soundEngine.play('tick');
  });

  socket.on('error_message', data => {
    showToast(data.message, 'danger');
    window.soundEngine.play('wrong');
  });

  socket.on('game_starting', data => {
    window.soundEngine.play('start');
    const overlay = document.getElementById('countdownOverlay');
    const numDisplay = document.getElementById('countdownNumber');
    overlay.style.display = 'flex';

    let count = data.countdown || 3;
    numDisplay.innerText = count;

    const interval = setInterval(() => {
      count -= 1;
      if (count > 0) {
        numDisplay.innerText = count;
        window.soundEngine.play('tick');
      } else {
        clearInterval(interval);
        window.location.href = `/battle/${data.room_code}`;
      }
    }, 1000);
  });
}

function renderLobby(room) {
  const container = document.getElementById('playerSlotsContainer');
  const countDisplay = document.getElementById('playerCountDisplay');
  const hostSettingsCard = document.getElementById('hostSettingsCard');
  const toggleReadyBtn = document.getElementById('toggleReadyBtn');
  const startMatchBtn = document.getElementById('startMatchBtn');

  if (!container) return;

  countDisplay.innerText = room.players.length;
  isHost = (room.host_sid === socket.id);
  myPlayerState = room.players.find(p => p.sid === socket.id);

  // Show host controls if host
  if (isHost) {
    hostSettingsCard.style.display = 'block';
  } else {
    hostSettingsCard.style.display = 'none';
  }

  // Update ready button
  if (myPlayerState) {
    if (myPlayerState.is_ready) {
      toggleReadyBtn.innerHTML = '<i data-lucide="x-circle"></i> Cancel Ready';
      toggleReadyBtn.className = 'btn-cyber btn-cyber-outline';
    } else {
      toggleReadyBtn.innerHTML = '<i data-lucide="check-circle-2"></i> Ready Up';
      toggleReadyBtn.className = 'btn-cyber btn-cyber-primary';
    }
  }

  // Check start match conditions (>= 2 players and all ready, or 1 player in practice)
  const canStart = (room.players.length >= 2 || room.game_mode === 'practice') && room.players.every(p => p.is_ready);

  if (isHost) {
    startMatchBtn.style.display = 'inline-flex';
    if (canStart) {
      startMatchBtn.disabled = false;
      startMatchBtn.style.opacity = '1';
      startMatchBtn.title = 'Start the match!';
    } else {
      startMatchBtn.disabled = true;
      startMatchBtn.style.opacity = '0.5';
      startMatchBtn.title = 'Need at least 2 players and all must be Ready';
    }
  } else {
    startMatchBtn.style.display = 'none';
  }

  // Render 4 slots
  container.innerHTML = '';
  const totalSlots = 4;
  for (let i = 0; i < totalSlots; i++) {
    const player = room.players[i];
    const slotDiv = document.createElement('div');

    if (player) {
      const isPlayerHost = (player.sid === room.host_sid);
      const isReady = player.is_ready;

      slotDiv.className = `lobby-slot occupied ${isReady ? 'is-ready' : ''}`;
      slotDiv.innerHTML = `
        <div class="slot-avatar">
          ${getAvatarEmoji(player.avatar)}
        </div>
        <div class="slot-info" style="flex-grow: 1;">
          <div style="display: flex; align-items: center; gap: 0.4rem;">
            <span class="slot-username">${escapeHtml(player.username)}</span>
            ${isPlayerHost ? '<i data-lucide="crown" style="color: #ffd700; width: 16px; height: 16px;"></i>' : ''}
          </div>
          <div class="slot-status-pill ${isReady ? 'text-green' : 'text-amber'}">
            ${isReady ? '✓ Ready to Battle' : '⏳ Waiting...'}
          </div>
        </div>
      `;
    } else {
      slotDiv.className = 'lobby-slot empty';
      slotDiv.style.opacity = '0.4';
      slotDiv.style.borderStyle = 'dashed';
      slotDiv.innerHTML = `
        <div class="slot-avatar" style="border-style: dashed; color: var(--text-muted);">
          <i data-lucide="user-plus"></i>
        </div>
        <div class="slot-info">
          <span class="slot-username text-muted">Empty Slot</span>
          <span style="font-size: 0.75rem; color: var(--text-muted);">Awaiting Challenger</span>
        </div>
      `;
    }
    container.appendChild(slotDiv);
  }

  if (window.lucide) {
    window.lucide.createIcons();
  }
}

function toggleReady() {
  if (socket) {
    socket.emit('toggle_ready');
    window.soundEngine.play('click');
  }
}

function startMatch() {
  if (socket && isHost) {
    socket.emit('start_game');
    window.soundEngine.play('click');
  }
}

function updateSettings() {
  if (!socket || !isHost) return;

  const catVal = document.getElementById('settingCategory').value;
  const diffVal = document.getElementById('settingDifficulty').value;
  const qCountVal = document.getElementById('settingQuestionCount').value;
  const qTimeVal = document.getElementById('settingQuestionTime').value;

  socket.emit('update_room_settings', {
    category_id: catVal,
    difficulty: diffVal,
    question_count: qCountVal,
    question_time: qTimeVal
  });
}

function sendChat(e) {
  e.preventDefault();
  const input = document.getElementById('chatInput');
  const msg = input.value.trim();
  if (!msg || !socket) return;

  socket.emit('send_chat', { message: msg });
  input.value = '';
}

function appendChatMessage(sender, text, color = '#ffffff', time = '') {
  const container = document.getElementById('chatMessages');
  if (!container) return;

  const msgDiv = document.createElement('div');
  msgDiv.className = 'chat-msg';
  msgDiv.innerHTML = `
    <div class="chat-msg-header" style="color: ${color};">
      <span>${escapeHtml(sender)}</span>
      <span style="font-size: 0.7rem; color: var(--text-muted);">${time}</span>
    </div>
    <div style="color: #cbd5e1; word-break: break-word;">${escapeHtml(text)}</div>
  `;
  container.appendChild(msgDiv);
  container.scrollTop = container.scrollHeight;
}

function getAvatarEmoji(avatar) {
  switch (avatar) {
    case 'cyber_ninja': return '🥷';
    case 'pixel_queen': return '👑';
    case 'neon_falcon': return '🦅';
    case 'shadow_knight': return '⚔️';
    case 'code_wizard': return '🧙‍♂️';
    case 'mecha_titan': return '🤖';
    case 'quantum_ghost': return '👻';
    default: return '🦊';
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}
