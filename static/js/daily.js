/**
 * QUIZ CLASH - DAILY CHALLENGE SCRIPT
 */

let dailyQuestions = [];
let dIndex = 0;
let userAnswers = {};
let responseTimes = {};
let questionStartTime = 0;
let dTimer = null;
let dTimeLeft = 15;

async function startDailyChallenge() {
  window.soundEngine.play('click');
  try {
    const res = await fetch('/api/daily-challenge/questions');
    const data = await res.json();

    if (!data || data.length === 0) {
      showToast('Daily questions could not be loaded.', 'danger');
      return;
    }

    dailyQuestions = data;
    dIndex = 0;
    userAnswers = {};
    responseTimes = {};

    document.getElementById('dailyStartCard').style.display = 'none';
    document.getElementById('dailyQuizView').style.display = 'block';

    window.soundEngine.play('start');
    renderDailyQuestion();
  } catch (e) {
    showToast('Failed to start daily challenge.', 'danger');
  }
}

function renderDailyQuestion() {
  if (dTimer) clearInterval(dTimer);

  const q = dailyQuestions[dIndex];
  document.getElementById('dailyCounter').innerText = `QUESTION ${dIndex + 1}/${dailyQuestions.length}`;
  document.getElementById('dailyCatBadge').innerText = q.category_name || 'Mixed';
  document.getElementById('dailyQuestionText').innerText = q.question_text;

  // Options
  const opts = q.options;
  document.getElementById('dTextA').innerText = opts.A;
  document.getElementById('dTextB').innerText = opts.B;
  document.getElementById('dTextC').innerText = opts.C;
  document.getElementById('dTextD').innerText = opts.D;

  ['A', 'B', 'C', 'D'].forEach(letter => {
    const btn = document.getElementById(`dBtn${letter}`);
    btn.className = 'option-btn';
    btn.disabled = false;
  });

  // Start 15s timer
  dTimeLeft = 15;
  questionStartTime = Date.now();
  updateTimerBadge();

  dTimer = setInterval(() => {
    dTimeLeft -= 1;
    updateTimerBadge();

    if (dTimeLeft <= 3 && dTimeLeft > 0) {
      window.soundEngine.play('tick');
    }

    if (dTimeLeft <= 0) {
      clearInterval(dTimer);
      // Timed out for this question
      recordDailyAnswer(null);
    }
  }, 1000);
}

function updateTimerBadge() {
  document.getElementById('dailyTimerBadge').innerText = `⏱️ ${dTimeLeft}s`;
}

function selectDailyOption(choice) {
  if (dTimer) clearInterval(dTimer);

  const btn = document.getElementById(`dBtn${choice}`);
  if (btn) btn.classList.add('selected');

  ['A', 'B', 'C', 'D'].forEach(l => {
    document.getElementById(`dBtn${l}`).disabled = true;
  });

  window.soundEngine.play('click');
  recordDailyAnswer(choice);
}

function recordDailyAnswer(choice) {
  const q = dailyQuestions[dIndex];
  const elapsed = Math.min(15.0, (Date.now() - questionStartTime) / 1000);

  userAnswers[q.id] = choice || '';
  responseTimes[q.id] = parseFloat(elapsed.toFixed(2));

  setTimeout(() => {
    dIndex += 1;
    if (dIndex < dailyQuestions.length) {
      renderDailyQuestion();
    } else {
      submitDailyChallenge();
    }
  }, 600);
}

async function submitDailyChallenge() {
  document.getElementById('dailyQuizView').style.display = 'none';

  try {
    const res = await fetch('/api/daily-challenge/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        answers: userAnswers,
        times: responseTimes
      })
    });

    const result = await res.json();
    if (!res.ok) {
      showToast(result.error || 'Submission error', 'danger');
      return;
    }

    // Show Results
    document.getElementById('dailyResultView').style.display = 'block';
    document.getElementById('dailyFinalScoreHeading').innerText = `Score: ${result.record.score} PTS (${result.record.correct_count}/5)`;

    const breakdownList = document.getElementById('dailyBreakdownList');
    breakdownList.innerHTML = '';

    result.breakdown.forEach(item => {
      const row = document.createElement('div');
      row.className = 'cyber-card';
      row.style.padding = '0.9rem 1.25rem';
      row.style.borderLeft = item.is_correct ? '4px solid var(--neon-green)' : '4px solid var(--neon-pink)';
      row.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
          <strong style="color: #fff; font-size: 0.95rem;">${escapeHtml(item.question_text)}</strong>
          <span class="badge-cyber ${item.is_correct ? 'badge-green' : 'badge-pink'}">
            ${item.is_correct ? `+${item.points} PTS` : '0 PTS'}
          </span>
        </div>
        <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.4rem;">
          Your Answer: <strong>${item.user_option || 'None (Timed Out)'}</strong> &bull; Correct: <strong class="text-green">${item.correct_option}</strong>
        </div>
        <div style="font-size: 0.8rem; color: var(--text-muted);">${escapeHtml(item.explanation || '')}</div>
      `;
      breakdownList.appendChild(row);
    });

    window.soundEngine.play('victory');
    if (typeof confetti === 'function') {
      confetti({ particleCount: 120, spread: 80, origin: { y: 0.6 } });
    }
  } catch (err) {
    showToast('Network error submitting daily challenge.', 'danger');
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}
