import React, { useEffect, useMemo, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const sampleTracks = [
  { title: 'Bubblegum Modem', artist: 'Cassette.exe', tag: 'hyperpop' },
  { title: 'Glitter Dial-Up', artist: 'Y2K Angels', tag: 'club edit' },
  { title: 'Pixel Heartbreak', artist: 'Neon Tape', tag: 'demo' },
];

function formatTime(seconds) {
  if (!Number.isFinite(seconds)) {
    return '0:00';
  }

  const minutes = Math.floor(seconds / 60);
  const rest = Math.floor(seconds % 60)
    .toString()
    .padStart(2, '0');

  return `${minutes}:${rest}`;
}

function App() {
  const audioRef = useRef(null);
  const canvasRef = useRef(null);
  const fileInputRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const sourceRef = useRef(null);
  const animationRef = useRef(null);

  const [track, setTrack] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState(0.72);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);

  const trackLabel = useMemo(() => {
    if (!track) {
      return 'Nessun brano caricato';
    }

    return track.name.replace(/\.[^/.]+$/, '');
  }, [track]);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume;
    }
  }, [volume]);

  useEffect(() => {
    drawVisualizer();

    return () => {
      cancelAnimationFrame(animationRef.current);
    };
  }, [track, isPlaying]);

  useEffect(() => {
    return () => {
      if (track?.url) {
        URL.revokeObjectURL(track.url);
      }
    };
  }, [track]);

  function connectAudioGraph() {
    const audio = audioRef.current;

    if (!audio) {
      return;
    }

    if (!audioContextRef.current) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      audioContextRef.current = new AudioContext();
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 128;
    }

    if (!sourceRef.current) {
      sourceRef.current = audioContextRef.current.createMediaElementSource(audio);
      sourceRef.current.connect(analyserRef.current);
      analyserRef.current.connect(audioContextRef.current.destination);
    }
  }

  async function togglePlayback() {
    const audio = audioRef.current;

    if (!audio || !track) {
      fileInputRef.current?.click();
      return;
    }

    connectAudioGraph();
    await audioContextRef.current?.resume();

    if (audio.paused) {
      await audio.play();
      setIsPlaying(true);
    } else {
      audio.pause();
      setIsPlaying(false);
    }
  }

  function handleFileChange(event) {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    if (track?.url) {
      URL.revokeObjectURL(track.url);
    }

    const nextTrack = {
      name: file.name,
      size: file.size,
      url: URL.createObjectURL(file),
    };

    setTrack(nextTrack);
    setProgress(0);
    setCurrentTime(0);
    setDuration(0);
    setIsPlaying(false);
  }

  function handleTimeUpdate() {
    const audio = audioRef.current;

    if (!audio) {
      return;
    }

    const nextDuration = audio.duration || 0;
    const nextTime = audio.currentTime || 0;

    setDuration(nextDuration);
    setCurrentTime(nextTime);
    setProgress(nextDuration ? (nextTime / nextDuration) * 100 : 0);
  }

  function handleSeek(event) {
    const audio = audioRef.current;
    const nextProgress = Number(event.target.value);

    setProgress(nextProgress);

    if (audio && duration) {
      audio.currentTime = (nextProgress / 100) * duration;
    }
  }

  function drawVisualizer() {
    const canvas = canvasRef.current;

    if (!canvas) {
      return;
    }

    const context = canvas.getContext('2d');
    const barCount = 34;
    const data = analyserRef.current
      ? new Uint8Array(analyserRef.current.frequencyBinCount)
      : null;

    const paint = (time = 0) => {
      const width = canvas.width;
      const height = canvas.height;
      const gap = 5;
      const barWidth = (width - gap * (barCount - 1)) / barCount;

      context.clearRect(0, 0, width, height);

      if (data && isPlaying) {
        analyserRef.current.getByteFrequencyData(data);
      }

      for (let index = 0; index < barCount; index += 1) {
        const frequencyValue = data?.[index] || 0;
        const idleWave =
          Math.sin(time * 0.004 + index * 0.62) * 0.5 +
          Math.cos(time * 0.002 + index * 0.2) * 0.5;
        const idleHeight = 28 + (idleWave + 1) * 34;
        const audioHeight = (frequencyValue / 255) * (height - 16);
        const barHeight = Math.max(12, isPlaying ? audioHeight : idleHeight);
        const x = index * (barWidth + gap);
        const y = height - barHeight;

        const gradient = context.createLinearGradient(0, y, 0, height);
        gradient.addColorStop(0, '#ffffff');
        gradient.addColorStop(0.18, '#7df9ff');
        gradient.addColorStop(0.58, '#ff2bd6');
        gradient.addColorStop(1, '#7a2cff');

        context.fillStyle = gradient;
        context.shadowColor = '#ff2bd6';
        context.shadowBlur = 13;
        context.beginPath();
        context.roundRect(x, y, barWidth, barHeight, 999);
        context.fill();
        context.shadowBlur = 0;
      }

      animationRef.current = requestAnimationFrame(paint);
    };

    cancelAnimationFrame(animationRef.current);
    animationRef.current = requestAnimationFrame(paint);
  }

  return (
    <main className="app-shell">
      <section className="player-panel" aria-label="Personal Cassette Player">
        <div className="topbar">
          <p className="brand-kicker">personal cassette player</p>
          <button className="ghost-button" type="button" onClick={() => fileInputRef.current?.click()}>
            Carica audio
          </button>
        </div>

        <div className="hero-grid">
          <div className="cassette">
            <div className="cassette-header">
              <span>Side A</span>
              <span>90 min</span>
            </div>

            <div className="cassette-label">
              <p className="now-playing">Now playing</p>
              <h1>{trackLabel}</h1>
            </div>

            <div className="reels" aria-hidden="true">
              <div className={`reel ${isPlaying ? 'spinning' : ''}`}>
                <span />
              </div>
              <div className="tape-window">
                <span />
              </div>
              <div className={`reel ${isPlaying ? 'spinning reverse' : ''}`}>
                <span />
              </div>
            </div>

            <div className="cassette-footer">
              <span>chrome</span>
              <span>hyperpop mix</span>
            </div>
          </div>

          <div className="visualizer-card">
            <canvas ref={canvasRef} width="720" height="250" aria-label="Visualizzatore audio a barre" />
            <div className="scanline" />
          </div>
        </div>

        <div className="controls">
          <button className="play-button" type="button" onClick={togglePlayback}>
            {isPlaying ? 'Pausa' : track ? 'Play' : 'Scegli brano'}
          </button>

          <label className="range-field">
            <span>{formatTime(currentTime)}</span>
            <input
              aria-label="Avanzamento brano"
              type="range"
              min="0"
              max="100"
              value={progress}
              onChange={handleSeek}
            />
            <span>{formatTime(duration)}</span>
          </label>

          <label className="volume-field">
            <span>Volume</span>
            <input
              aria-label="Volume"
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={volume}
              onChange={(event) => setVolume(Number(event.target.value))}
            />
          </label>
        </div>

        <div className="playlist">
          <div>
            <p className="section-label">Mini playlist</p>
            <h2>Starter tracks</h2>
          </div>

          <div className="track-list">
            {sampleTracks.map((item, index) => (
              <article className="track-item" key={item.title}>
                <span>{String(index + 1).padStart(2, '0')}</span>
                <div>
                  <h3>{item.title}</h3>
                  <p>{item.artist}</p>
                </div>
                <strong>{item.tag}</strong>
              </article>
            ))}
          </div>
        </div>
      </section>

      <input
        ref={fileInputRef}
        className="sr-only"
        type="file"
        accept="audio/*"
        onChange={handleFileChange}
      />

      <audio
        ref={audioRef}
        src={track?.url}
        onEnded={() => setIsPlaying(false)}
        onLoadedMetadata={handleTimeUpdate}
        onTimeUpdate={handleTimeUpdate}
      />
    </main>
  );
}

createRoot(document.getElementById('root')).render(<App />);
