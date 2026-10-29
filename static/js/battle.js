/**
 * QUIZ CLASH - BATTLE ARENA ENGINE
 * Handles synchronized question delivery, countdown animations, answer submissions,
 * server validation reveals, live scoreboards, confetti, and victory screen.
 */

let socket = null;
let currentQuestionTime = 15;
let timerInterval = null;
let secondsRemaining = 15;
let myCurrentChoice = null;
let hasSubmitted = false;
const CIRCLE_CIRCUMFERENCE = 194.78; // 2 * PI * 31

document.addEventListener('DOMContentLoaded', () => {
  initBattleSocket();
});

function initBattleSocket() {
  socket = io();

  socket.on('connect', () => {
    // Re-verify room association
    socket.emit('join_lobby', { room_code: window.ROOM_CODE });
    document.getElementById('connectionStatusPill').innerHTML = '<i data-lucide="wifi"></i> Synced';
  });

  socket.on('disconnect', () => {
    const pill = document.getElementById('connectionStatusPill');
    pill.className = 'badge-cyber badge-pink';
    pill.innerHTML = '<i data-lucide="wifi-off"></i> Reconnecting';
  });

  // New Question Delivery
  socket.on('new_question', qData => {
    handleNewQuestion(qData);
  });

  // Someone submitted an answer
  socket.on('player_submitted', data => {
    handlePlayerSubmitted(data);
  });

  // Round Results Reveal
  socket.on('round_revealed', data => {
    handleRoundRevealed(data);
  });

  // Game Over
  socket.on('game_over', data => {
    handleGameOver(data);
  });
}

function handleNewQuestion(qData) {
  myCurrentChoice = null;
  hasSubmitted = false;

  // Reset UI elements
  document.getElementById('explanationPanel').style.display = 'none';
  document.getElementById('p1AnsweredPill').style.display = 'none';
  document.getElementById('p2AnsweredPill').style.display = 'none';

  // Set meta info
  document.getElementById('questionCounter').innerText = `QUESTION ${qData.question_number}/${qData.total_questions}`;
  document.getElementById('categoryBadge').innerText = qData.category_name;
  document.getElementById('difficultyBadge').innerText = qData.difficulty.toUpperCase();
  document.getElementById('questionPrompt').innerText = qData.question_text;

  // Set 4 Options
  const opts = qData.options;
  document.getElementById('optTextA').innerText = opts.A;
  document.getElementById('optTextB').innerText = opts.B;
  document.getElementById('optTextC').innerText = opts.C;
  document.getElementById('optTextD').innerText = opts.D;

  // Reset and enable all 4 option buttons
  ['A', 'B', 'C', 'D'].forEach(letter => {
    const btn = document.getElementById(`btnOpt${letter}`);
    btn.className = 'option-btn';
    btn.disabled = false;
  });

  // Update Scoreboard Players
  updateScoreboardPlayers(qData.players);

  // Start Synchronized Timer
  currentQuestionTime = qData.question_time || 15;
  startCountdown(currentQuestionTime);
}

function updateScoreboardPlayers(players) {
  if (!players || players.length === 0) return;

  // Assume Player 1 is Current User (or host) and Player 2 is Opponent
  let p1 = players.find(p => p.sid === socket.id) || players[0];
  let p2 = players.find(p => p.sid !== p1.sid) || (players.length > 1 ? players[1] : null);

  if (p1) {
    document.getElementById('p1Name').innerText = p1.username;
    document.getElementById('p1Score').innerText = p1.score;
    document.getElementById('p1Avatar').innerText = getAvatarEmoji(p1.avatar);
    if (p1.streak > 1) {
      document.getElementById('p1Streak').style.display = 'inline-flex';
      document.getElementById('p1StreakVal').innerText = p1.streak;
    } else {
      document.getElementById('p1Streak').style.display = 'none';
    }
  }

  if (p2) {
    document.getElementById('p2Name').innerText = p2.username;
    document.getElementById('p2Score').innerText = p2.score;
    document.getElementById('p2Avatar').innerText = getAvatarEmoji(p2.avatar);
    if (p2.streak > 1) {
      document.getElementById('p2Streak').style.display = 'inline-flex';
      document.getElementById('p2StreakVal').innerText = p2.streak;
    } else {
      document.getElementById('p2Streak').style.display = 'none';
    }
  } else {
    // Solo practice / waiting for 2nd
    document.getElementById('p2Name').innerText = 'Solo Target';
    document.getElementById('p2Score').innerText = '-';
  }
}

function startCountdown(duration) {
  if (timerInterval) clearInterval(timerInterval);

  secondsRemaining = duration;
  const timerCircle = document.getElementById('timerCircle');
  const timerSeconds = document.getElementById('timerSeconds');
  const linearBar = document.getElementById('linearTimerBar');

  timerCircle.style.stroke = 'var(--neon-cyan)';
  timerCircle.style.strokeDashoffset = '0';
  linearBar.style.width = '100%';
  timerSeconds.innerText = secondsRemaining;

  const startTime = Date.now();
  const totalMs = duration * 1000;

  timerInterval = setInterval(() => {
    const elapsedMs = Date.now() - startTime;
    const remainingMs = Math.max(0, totalMs - elapsedMs);
    const remainingSecs = Math.ceil(remainingMs / 1000);

    timerSeconds.innerText = remainingSecs;

    // Fraction elapsed
    const fraction = remainingMs / totalMs;
    const offset = CIRCLE_CIRCUMFERENCE * (1 - fraction);
    timerCircle.style.strokeDashoffset = offset;
    linearBar.style.width = `${(fraction * 100).toFixed(1)}%`;

    // Low time warning colors & sounds
    if (remainingSecs <= 4) {
      timerCircle.style.stroke = 'var(--neon-pink)';
      if (remainingSecs !== secondsRemaining) {
        window.soundEngine.play('tick');
      }
    }

    secondsRemaining = remainingSecs;

    if (remainingMs <= 0) {
      clearInterval(timerInterval);
      timerInterval = null;
    }
  }, 100);
}

function submitChoice(option) {
  if (hasSubmitted || !socket) return;
  hasSubmitted = true;
  myCurrentChoice = option;

  // Highlight chosen button
  const chosenBtn = document.getElementById(`btnOpt${option}`);
  if (chosenBtn) {
    chosenBtn.classList.add('selected');
  }

  // Lock all buttons
  ['A', 'B', 'C', 'D'].forEach(letter => {
    document.getElementById(`btnOpt${letter}`).disabled = true;
  });

  // Send answer to server
  socket.emit('submit_answer', { option: option });
  window.soundEngine.play('click');
}

function handlePlayerSubmitted(data) {
  // Show green checkmark on scoreboard for the player who answered
  const p1Name = document.getElementById('p1Name').innerText;
  if (data.username === p1Name) {
    document.getElementById('p1AnsweredPill').style.display = 'inline-flex';
  } else {
    document.getElementById('p2AnsweredPill').style.display = 'inline-flex';
  }
}

function handleRoundRevealed(data) {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }

  const correctOption = data.correct_option;
  const explanation = data.explanation;

  // Reveal correct answer in green
  const correctBtn = document.getElementById(`btnOpt${correctOption}`);
  if (correctBtn) {
    correctBtn.classList.remove('selected');
    correctBtn.classList.add('correct');
  }

  // If user selected wrong, turn red
  if (myCurrentChoice && myCurrentChoice !== correctOption) {
    const wrongBtn = document.getElementById(`btnOpt${myCurrentChoice}`);
    if (wrongBtn) {
      wrongBtn.classList.remove('selected');
      wrongBtn.classList.add('incorrect');
    }
    window.soundEngine.play('wrong');
  } else if (myCurrentChoice === correctOption) {
    window.soundEngine.play('correct');
  } else {
    // Unanswered / timed out
    window.soundEngine.play('wrong');
  }

  // Show explanation
  if (explanation) {
    const expPanel = document.getElementById('explanationPanel');
    document.getElementById('explanationText').innerText = explanation;
    expPanel.style.display = 'block';
  }

  // Update Scoreboard with new scores
  data.players.forEach(p => {
    const p1Name = document.getElementById('p1Name').innerText;
    if (p.username === p1Name) {
      document.getElementById('p1Score').innerText = p.score;
      if (p.streak > 1) {
        document.getElementById('p1Streak').style.display = 'inline-flex';
        document.getElementById('p1StreakVal').innerText = p.streak;
      } else {
        document.getElementById('p1Streak').style.display = 'none';
      }
    } else {
      document.getElementById('p2Score').innerText = p.score;
      if (p.streak > 1) {
        document.getElementById('p2Streak').style.display = 'inline-flex';
        document.getElementById('p2StreakVal').innerText = p.streak;
      } else {
        document.getElementById('p2Streak').style.display = 'none';
      }
    }
  });

  if (window.lucide) {
    window.lucide.createIcons();
  }
}

function handleGameOver(data) {
  const modal = document.getElementById('resultsModal');
  modal.style.display = 'block';

  const isDraw = data.is_draw;
  const isWinner = (!isDraw && data.winner_id === window.CURRENT_USER_ID);

  if (isWinner) {
    document.getElementById('winnerAnnouncement').innerText = 'VICTORY ROYALE!';
    document.getElementById('battleResultBadge').innerText = 'CHAMPION';
    document.getElementById('battleResultBadge').className = 'badge-cyber badge-green';
    document.getElementById('winnerTextSub').innerText = 'You outsmarted and outpaced your opponent in the arena.';
    window.soundEngine.play('victory');

    // Confetti Cannon!
    if (typeof confetti === 'function') {
      confetti({
        particleCount: 160,
        spread: 90,
        origin: { y: 0.6 }
      });
      setTimeout(() => {
        confetti({ particleCount: 80, angle: 60, spread: 55, origin: { x: 0 } });
        confetti({ particleCount: 80, angle: 120, spread: 55, origin: { x: 1 } });
      }, 400);
    }
  } else if (isDraw) {
    document.getElementById('winnerAnnouncement').innerText = 'HONORABLE DRAW';
    document.getElementById('battleResultBadge').innerText = 'STALEMATE';
    document.getElementById('battleResultBadge').className = 'badge-cyber badge-gold';
    document.getElementById('winnerTextSub').innerText = 'An equally matched battle of minds.';
    window.soundEngine.play('start');
  } else {
    document.getElementById('winnerAnnouncement').innerText = 'DEFEAT';
    document.getElementById('battleResultBadge').innerText = 'RUNNER UP';
    document.getElementById('battleResultBadge').className = 'badge-cyber badge-pink';
    document.getElementById('winnerTextSub').innerText = 'Victory slipped away. Train harder and strike back!';
    window.soundEngine.play('wrong');
  }

  // Render Podium Standings
  const podiumList = document.getElementById('podiumStandings');
  podiumList.innerHTML = '';
  data.ranked_players.forEach(p => {
    const isFirst = (p.rank === 1);
    const item = document.createElement('div');
    item.className = `podium-item ${isFirst ? 'first-place' : ''}`;
    item.innerHTML = `
      <div style="display: flex; align-items: center; gap: 1rem;">
        <span class="font-heading" style="font-size: 1.5rem; font-weight: 900; color: ${isFirst ? '#ffd700' : '#cbd5e1'};">#${p.rank}</span>
        <div style="width: 44px; height: 44px; border-radius: 50%; background: var(--bg-darker); display: flex; align-items: center; justify-content: center; font-size: 1.4rem;">
          ${getAvatarEmoji(p.avatar)}
        </div>
        <div style="text-align: left;">
          <h4 style="font-size: 1.05rem; margin-bottom: 0.1rem;">${escapeHtml(p.username)}</h4>
          <span style="font-size: 0.75rem; color: var(--text-muted);">${p.correct_count}/${p.total_answered} Correct &bull; ${p.avg_response_time}s Avg</span>
        </div>
      </div>
      <div style="text-align: right;">
        <span class="font-heading" style="font-size: 1.6rem; font-weight: 900; color: ${isFirst ? '#ffd700' : 'var(--neon-cyan)'};">${p.score}</span>
        <span style="display: block; font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">Points</span>
      </div>
    `;
    podiumList.appendChild(item);
  });

  // Find current user's personal breakdown
  const myStats = data.ranked_players.find(p => p.user_id === window.CURRENT_USER_ID) || data.ranked_players[0];
  if (myStats) {
    const accuracy = myStats.total_answered > 0 ? Math.round((myStats.correct_count / myStats.total_answered) * 100) : 0;
    document.getElementById('resAccuracy').innerText = `${accuracy}%`;
    document.getElementById('resAvgSpeed').innerText = `${myStats.avg_response_time}s`;
    document.getElementById('resMaxStreak').innerText = `🔥 ${myStats.max_streak}`;
  }

  // Display unlocked achievements
  const unlocked = data.unlocked_achievements && data.unlocked_achievements[socket.id];
  if (unlocked && unlocked.length > 0) {
    const achContainer = document.getElementById('unlockedAchievementsContainer');
    const achList = document.getElementById('unlockedAchievementsList');
    achContainer.style.display = 'block';
    achList.innerHTML = '';
    unlocked.forEach(a => {
      const row = document.createElement('div');
      row.style.cssText = 'padding: 0.5rem 0.75rem; background: var(--bg-surface); border-radius: 6px; font-size: 0.85rem;';
      row.innerHTML = `<strong class="text-green">${escapeHtml(a.title)}:</strong> ${escapeHtml(a.description)}`;
      achList.appendChild(row);
    });
    window.soundEngine.play('streak');
  }

  if (window.lucide) {
    window.lucide.createIcons();
  }
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
