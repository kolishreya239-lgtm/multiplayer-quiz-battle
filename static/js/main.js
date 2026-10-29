/**
 * QUIZ CLASH - MAIN JAVASCRIPT
 * Audio Engine (Web Audio API), UI Interactions, Toast Notifications
 */

// Sound Engine using Web Audio API (No missing MP3s, 100% reliable)
class SoundEngine {
  constructor() {
    this.ctx = null;
    this.muted = localStorage.getItem('qc_sound_muted') === 'true';
    this.initAudioContext();
  }

  initAudioContext() {
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    } catch (e) {
      console.warn('Web Audio API not supported in this browser.', e);
    }
  }

  resumeContext() {
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  toggleMute() {
    this.muted = !this.muted;
    localStorage.setItem('qc_sound_muted', this.muted);
    this.updateAudioIcons();
    return this.muted;
  }

  updateAudioIcons() {
    const btn = document.getElementById('audioToggleBtn');
    if (!btn) return;
    if (this.muted) {
      btn.innerHTML = '<i data-lucide="volume-x"></i>';
      btn.classList.add('muted');
    } else {
      btn.innerHTML = '<i data-lucide="volume-2"></i>';
      btn.classList.remove('muted');
    }
    if (window.lucide) {
      window.lucide.createIcons();
    }
  }

  play(type) {
    if (this.muted || !this.ctx) return;
    this.resumeContext();

    const now = this.ctx.currentTime;

    switch (type) {
      case 'click': {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(800, now);
        osc.frequency.exponentialRampToValueAtTime(400, now + 0.05);
        gain.gain.setValueAtTime(0.15, now);
        gain.gain.linearRampToValueAtTime(0.01, now + 0.05);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now);
        osc.stop(now + 0.05);
        break;
      }

      case 'tick': {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(1200, now);
        gain.gain.setValueAtTime(0.1, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.04);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now);
        osc.stop(now + 0.04);
        break;
      }

      case 'start': {
        // Energizing rising arpeggio
        const notes = [440, 554.37, 659.25, 880];
        notes.forEach((freq, idx) => {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.value = freq;
          const noteStart = now + idx * 0.08;
          gain.gain.setValueAtTime(0, noteStart);
          gain.gain.linearRampToValueAtTime(0.2, noteStart + 0.02);
          gain.gain.exponentialRampToValueAtTime(0.001, noteStart + 0.2);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start(noteStart);
          osc.stop(noteStart + 0.2);
        });
        break;
      }

      case 'correct': {
        // Bright victorious major chime
        [523.25, 659.25, 783.99, 1046.5].forEach((freq, i) => {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'sine';
          osc.frequency.value = freq;
          const nStart = now + i * 0.06;
          gain.gain.setValueAtTime(0.2, nStart);
          gain.gain.exponentialRampToValueAtTime(0.001, nStart + 0.35);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start(nStart);
          osc.stop(nStart + 0.35);
        });
        break;
      }

      case 'wrong': {
        // Deep warning buzzer
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(150, now);
        osc.frequency.linearRampToValueAtTime(90, now + 0.3);
        gain.gain.setValueAtTime(0.25, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now);
        osc.stop(now + 0.3);
        break;
      }

      case 'streak': {
        // Cyber powerup swell
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(300, now);
        osc.frequency.exponentialRampToValueAtTime(1200, now + 0.35);
        gain.gain.setValueAtTime(0.05, now);
        gain.gain.linearRampToValueAtTime(0.25, now + 0.25);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now);
        osc.stop(now + 0.4);
        break;
      }

      case 'victory': {
        // Fanfare chord
        const chords = [523.25, 659.25, 783.99, 1046.5];
        chords.forEach(f => {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.value = f;
          gain.gain.setValueAtTime(0.2, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 1.2);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start(now);
          osc.stop(now + 1.2);
        });
        break;
      }
    }
  }
}

// Global Sound Instance
window.soundEngine = new SoundEngine();

// Document Ready Handlers
document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lucide Icons
  if (window.lucide) {
    window.lucide.createIcons();
  }

  // Update sound icon
  window.soundEngine.updateAudioIcons();

  // Audio Toggle Button
  const audioBtn = document.getElementById('audioToggleBtn');
  if (audioBtn) {
    audioBtn.addEventListener('click', () => {
      window.soundEngine.toggleMute();
    });
  }

  // Bind click sounds to interactive cyber buttons
  document.querySelectorAll('.btn-cyber, .nav-link, .option-btn, .avatar-option').forEach(el => {
    el.addEventListener('click', () => {
      window.soundEngine.play('click');
    });
  });

  // Mobile Menu Drawer Toggle
  const navToggle = document.getElementById('navToggle');
  const navLinks = document.getElementById('navLinks');
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', () => {
      navLinks.classList.toggle('active');
    });
  }

  // Auto-dismiss alert toasts
  document.querySelectorAll('.cyber-alert').forEach(toast => {
    setTimeout(() => {
      toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      setTimeout(() => toast.remove(), 400);
    }, 4500);
  });
});

// Toast notification helper
function showToast(message, type = 'info') {
  const container = document.querySelector('.alert-container') || (() => {
    const c = document.createElement('div');
    c.className = 'alert-container';
    document.body.appendChild(c);
    return c;
  })();

  const alert = document.createElement('div');
  alert.className = `cyber-alert cyber-alert-${type}`;
  alert.innerHTML = `<span>${message}</span>`;
  container.appendChild(alert);

  setTimeout(() => {
    alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
    alert.style.opacity = '0';
    alert.style.transform = 'translateX(100%)';
    setTimeout(() => alert.remove(), 400);
  }, 4000);
}

// Clipboard copy helper
function copyToClipboard(text, successMessage = 'Copied to clipboard!') {
  navigator.clipboard.writeText(text).then(() => {
    showToast(successMessage, 'success');
    window.soundEngine.play('click');
  }).catch(() => {
    showToast('Failed to copy text', 'danger');
  });
}
