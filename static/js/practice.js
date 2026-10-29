/**
 * QUIZ CLASH - SOLO PRACTICE DRILL
 */

let practiceQuestions = [];
let currentIndex = 0;
let userScore = 0;
let correctCount = 0;
let answeredCurrent = false;

async function startPractice() {
  const cat = document.getElementById('pracCategory').value;
  const diff = document.getElementById('pracDifficulty').value;
  const count = document.getElementById('pracCount').value;

  window.soundEngine.play('click');

  try {
    const res = await fetch(`/api/practice/questions?category_id=${cat}&difficulty=${diff}&count=${count}`);
    const data = await res.json();

    if (!data || data.length === 0) {
      showToast('No questions found for the selected filter.', 'warning');
      return;
    }

    practiceQuestions = data;
    currentIndex = 0;
    userScore = 0;
    correctCount = 0;

    document.getElementById('practiceSetupView').style.display = 'none';
    document.getElementById('practiceSummaryView').style.display = 'none';
    document.getElementById('practiceQuizView').style.display = 'block';

    renderCurrentPractice();
    window.soundEngine.play('start');
  } catch (err) {
    showToast('Failed to load practice questions.', 'danger');
  }
}

function renderCurrentPractice() {
  answeredCurrent = false;
  const q = practiceQuestions[currentIndex];

  document.getElementById('pracCategoryBadge').innerText = q.category_name || 'Category';
  document.getElementById('pracDiffBadge').innerText = (q.difficulty || 'medium').toUpperCase();
  document.getElementById('pracCounter').innerText = `QUESTION ${currentIndex + 1}/${practiceQuestions.length}`;
  document.getElementById('pracScoreBadge').innerText = `Score: ${userScore}`;
  document.getElementById('pracQuestionText').innerText = q.question_text;

  // Set options
  const opts = q.options;
  document.getElementById('pracTextA').innerText = opts.A;
  document.getElementById('pracTextB').innerText = opts.B;
  document.getElementById('pracTextC').innerText = opts.C;
  document.getElementById('pracTextD').innerText = opts.D;

  // Reset states
  ['A', 'B', 'C', 'D'].forEach(letter => {
    const btn = document.getElementById(`pracBtn${letter}`);
    btn.className = 'option-btn';
    btn.disabled = false;
  });

  document.getElementById('pracExpPanel').style.display = 'none';
  document.getElementById('pracNextBtn').style.display = 'none';
}

function choosePracticeAnswer(choice) {
  if (answeredCurrent) return;
  answeredCurrent = true;

  const q = practiceQuestions[currentIndex];
  const correct = q.correct_option.toUpperCase();
  const isCorrect = (choice.toUpperCase() === correct);

  // Disable options
  ['A', 'B', 'C', 'D'].forEach(letter => {
    document.getElementById(`pracBtn${letter}`).disabled = true;
  });

  // Reveal correct
  const correctBtn = document.getElementById(`pracBtn${correct}`);
  if (correctBtn) correctBtn.classList.add('correct');

  if (isCorrect) {
    userScore += 100;
    correctCount += 1;
    document.getElementById('pracScoreBadge').innerText = `Score: ${userScore}`;
    window.soundEngine.play('correct');
  } else {
    const wrongBtn = document.getElementById(`pracBtn${choice}`);
    if (wrongBtn) wrongBtn.classList.add('incorrect');
    window.soundEngine.play('wrong');
  }

  // Show explanation
  if (q.explanation) {
    document.getElementById('pracExpText').innerText = q.explanation;
    document.getElementById('pracExpPanel').style.display = 'block';
  }

  // Show next button
  const nextBtn = document.getElementById('pracNextBtn');
  nextBtn.style.display = 'inline-flex';
  if (currentIndex === practiceQuestions.length - 1) {
    nextBtn.innerHTML = 'Complete Drill <i data-lucide="check"></i>';
  } else {
    nextBtn.innerHTML = 'Next Question <i data-lucide="arrow-right"></i>';
  }

  if (window.lucide) window.lucide.createIcons();
}

function nextPracticeQuestion() {
  window.soundEngine.play('click');
  currentIndex += 1;

  if (currentIndex < practiceQuestions.length) {
    renderCurrentPractice();
  } else {
    finishPractice();
  }
}

function finishPractice() {
  document.getElementById('practiceQuizView').style.display = 'none';
  document.getElementById('practiceSummaryView').style.display = 'block';

  document.getElementById('sumFinalScore').innerText = userScore;
  const acc = Math.round((correctCount / practiceQuestions.length) * 100);
  document.getElementById('sumAccuracy').innerText = `${acc}%`;
  document.getElementById('sumCorrect').innerText = `${correctCount}/${practiceQuestions.length}`;

  window.soundEngine.play('victory');
}

function restartPractice() {
  document.getElementById('practiceSummaryView').style.display = 'none';
  document.getElementById('practiceSetupView').style.display = 'block';
  window.soundEngine.play('click');
}
