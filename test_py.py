import librosa
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import warnings
warnings.filterwarnings('ignore')

class BachataAnalyzer:
    """
    Specialized analyzer for Bachata music
    Detects genre, separates instruments, and provides detailed analysis
    """
    
    def __init__(self, file_path, sr=22050):
        self.file_path = file_path
        self.sr = sr
        self.y = None
        self.duration = None
        self.is_bachata = False
        self.confidence = 0.0
        self.separated_sources = {}
        self.instrument_analysis = {}
        self.load_audio()
    
    def load_audio(self):
        """Load audio file and get basic properties"""
        try:
            self.y, self.sr = librosa.load(self.file_path, sr=self.sr)
            self.duration = librosa.get_duration(y=self.y, sr=self.sr)
            print(f"Audio loaded: {self.file_path}")
            print(f"Duration: {self.duration:.2f} seconds")
        except Exception as e:
            print(f"Error loading audio: {e}")
            raise
    
    def classify_bachata(self):
        """
        Classify if the music is bachata based on:
        - Tempo (120-140 BPM typical for bachata)
        - Rhythmic patterns
        - Spectral characteristics
        """
        # Tempo analysis
        tempo, beats = librosa.beat.beat_track(y=self.y, sr=self.sr)
        
        # Bachata tempo range
        is_bachata_tempo = 120 <= tempo <= 140
        tempo_score = 1.0 if is_bachata_tempo else max(0, 1 - abs(tempo - 130) / 50)
        
        # Analyze rhythm patterns
        onset_env = librosa.onset.onset_strength(y=self.y, sr=self.sr)
        
        # Bachata has characteristic 4/4 pattern with emphasis on 1 and 3
        # Analyze beat strength patterns
        beat_frames = librosa.beat.beat_track(y=self.y, sr=self.sr, trim=False)[1]
        beat_strengths = onset_env[beat_frames] if len(beat_frames) > 0 else []
        
        # Check for consistent 4/4 pattern
        rhythm_score = 0.0
        if len(beat_strengths) >= 8:
            # Group beats into measures (4 beats per measure)
            measures = [beat_strengths[i:i+4] for i in range(0, len(beat_strengths)-3, 4)]
            if measures:
                # Check if beats 1 and 3 are typically stronger
                pattern_scores = []
                for measure in measures[:min(10, len(measures))]:
                    if len(measure) == 4:
                        pattern_score = (measure[0] + measure[2]) / (sum(measure) + 1e-6)
                        pattern_scores.append(pattern_score)
                rhythm_score = np.mean(pattern_scores) if pattern_scores else 0.0
        
        # Spectral characteristics
        # Bachata typically has strong bass, clear percussion, and guitar presence
        spectral_centroid = librosa.feature.spectral_centroid(y=self.y, sr=self.sr)[0]
        spectral_rolloff = librosa.feature.spectral_rolloff(y=self.y, sr=self.sr)[0]
        
        # Check for characteristic frequency distribution
        mean_centroid = np.mean(spectral_centroid)
        # Bachata typically has centroid in mid-range due to guitar prominence
        centroid_score = 1.0 if 1500 <= mean_centroid <= 3500 else 0.5
        
        # Harmonic-percussive separation to check balance
        harmonic, percussive = librosa.effects.hpss(self.y)
        hp_ratio = np.sum(np.abs(harmonic)) / (np.sum(np.abs(percussive)) + 1e-6)
        # Bachata has both strong harmonic (guitars) and percussive (drums) content
        balance_score = 1.0 if 0.8 <= hp_ratio <= 2.0 else 0.5
        
        # Calculate overall confidence
        self.confidence = (tempo_score * 0.4 + 
                          rhythm_score * 0.3 + 
                          centroid_score * 0.15 + 
                          balance_score * 0.15)
        
        self.is_bachata = self.confidence > 0.6
        
        return {
            'is_bachata': self.is_bachata,
            'confidence': float(self.confidence),
            'tempo': float(tempo),
            'tempo_score': float(tempo_score),
            'rhythm_score': float(rhythm_score),
            'spectral_score': float(centroid_score),
            'balance_score': float(balance_score)
        }
    
    def separate_sources(self):
        """
        Separate audio into different instrument tracks
        Note: This is a simplified version. For production, use Demucs or Spleeter
        """
        print("Separating audio sources...")
        
        # Harmonic-percussive separation
        harmonic, percussive = librosa.effects.hpss(self.y, margin=3.0)
        
        # Further separate harmonic into bass and treble
        # Low-pass filter for bass
        sos_bass = signal.butter(4, 250, 'lowpass', fs=self.sr, output='sos')
        bass = signal.sosfilt(sos_bass, harmonic)
        
        # Band-pass for mid (guitars)
        sos_mid = signal.butter(4, [250, 4000], 'bandpass', fs=self.sr, output='sos')
        guitars = signal.sosfilt(sos_mid, harmonic)
        
        # High-pass for treble (lead guitar, some percussion)
        sos_high = signal.butter(4, 4000, 'highpass', fs=self.sr, output='sos')
        treble = signal.sosfilt(sos_high, self.y)
        
        # Separate percussion into low (kick, bongos) and high (guira)
        sos_perc_low = signal.butter(4, 1000, 'lowpass', fs=self.sr, output='sos')
        drums_low = signal.sosfilt(sos_perc_low, percussive)
        
        sos_perc_high = signal.butter(4, 8000, 'highpass', fs=self.sr, output='sos')
        guira = signal.sosfilt(sos_perc_high, percussive)
        
        self.separated_sources = {
            'bass': bass,
            'guitars': guitars,
            'drums_low': drums_low,
            'guira': guira,
            'treble': treble,
            'full_harmonic': harmonic,
            'full_percussive': percussive
        }
        
        return self.separated_sources
    
    def analyze_instruments(self):
        """Analyze each separated instrument track"""
        if not self.separated_sources:
            self.separate_sources()
        
        results = {}
        
        # Analyze bass
        bass = self.separated_sources['bass']
        bass_rms = librosa.feature.rms(y=bass)[0]
        results['bass'] = {
            'presence': float(np.mean(bass_rms)),
            'variation': float(np.std(bass_rms)),
            'active': float(np.mean(bass_rms) > 0.001)
        }
        
        # Analyze guitars
        guitars = self.separated_sources['guitars']
        guitar_rms = librosa.feature.rms(y=guitars)[0]
        guitar_zcr = librosa.feature.zero_crossing_rate(guitars)[0]
        results['guitars'] = {
            'presence': float(np.mean(guitar_rms)),
            'variation': float(np.std(guitar_rms)),
            'texture': float(np.mean(guitar_zcr)),  # Higher = more strumming
            'active': float(np.mean(guitar_rms) > 0.001)
        }
        
        # Analyze drums/bongos
        drums = self.separated_sources['drums_low']
        drums_onset = librosa.onset.onset_strength(y=drums, sr=self.sr)
        tempo_drums, beats_drums = librosa.beat.beat_track(
            onset_envelope=drums_onset, sr=self.sr
        )
        results['drums_bongos'] = {
            'presence': float(np.mean(drums_onset)),
            'tempo': float(tempo_drums),
            'beat_regularity': float(np.std(np.diff(beats_drums)) if len(beats_drums) > 1 else 0),
            'active': float(np.mean(drums_onset) > 0.1)
        }
        
        # Analyze guira
        guira = self.separated_sources['guira']
        guira_rms = librosa.feature.rms(y=guira)[0]
        guira_centroid = librosa.feature.spectral_centroid(y=guira, sr=self.sr)[0]
        results['guira'] = {
            'presence': float(np.mean(guira_rms)),
            'brightness': float(np.mean(guira_centroid)),
            'consistency': float(1.0 / (np.std(guira_rms) + 1e-6)),
            'active': float(np.mean(guira_rms) > 0.0001)
        }
        
        self.instrument_analysis = results
        return results
    
    def visualize_analysis(self, save_path='bachata_analysis.png'):
        """Create comprehensive visualization of the bachata analysis"""
        if not self.separated_sources:
            self.separate_sources()
        
        fig = plt.figure(figsize=(16, 12))
        
        # Create time axis
        time_frames = range(len(self.y))
        time_seconds = librosa.frames_to_time(time_frames, sr=self.sr)
        
        # 1. Original waveform
        ax1 = plt.subplot(6, 2, (1, 2))
        librosa.display.waveshow(self.y, sr=self.sr, ax=ax1, alpha=0.8)
        ax1.set_title(f'Original Audio - {"BACHATA" if self.is_bachata else "NOT BACHATA"} '
                     f'(Confidence: {self.confidence:.1%})', fontsize=12, fontweight='bold')
        ax1.set_xlabel('')
        
        # 2. Bass track
        ax2 = plt.subplot(6, 2, 3)
        librosa.display.waveshow(self.separated_sources['bass'], sr=self.sr, ax=ax2, color='darkblue')
        ax2.set_title('Bass Guitar', fontsize=10)
        ax2.set_xlabel('')
        ax2.set_ylabel('Amplitude', fontsize=8)
        
        # 3. Guitar track
        ax3 = plt.subplot(6, 2, 4)
        librosa.display.waveshow(self.separated_sources['guitars'], sr=self.sr, ax=ax3, color='green')
        ax3.set_title('Rhythm & Lead Guitars', fontsize=10)
        ax3.set_xlabel('')
        
        # 4. Drums/Bongos track
        ax4 = plt.subplot(6, 2, 5)
        librosa.display.waveshow(self.separated_sources['drums_low'], sr=self.sr, ax=ax4, color='red')
        ax4.set_title('Drums & Bongos', fontsize=10)
        ax4.set_xlabel('')
        ax4.set_ylabel('Amplitude', fontsize=8)
        
        # 5. Guira track
        ax5 = plt.subplot(6, 2, 6)
        librosa.display.waveshow(self.separated_sources['guira'], sr=self.sr, ax=ax5, color='orange')
        ax5.set_title('Güira (High Percussion)', fontsize=10)
        ax5.set_xlabel('')
        
        # 6. Instrument activity timeline
        ax6 = plt.subplot(6, 2, (7, 8))
        
        # Calculate activity levels over time
        hop_length = 512
        frame_length = 2048
        
        bass_activity = librosa.feature.rms(y=self.separated_sources['bass'], 
                                           frame_length=frame_length, hop_length=hop_length)[0]
        guitar_activity = librosa.feature.rms(y=self.separated_sources['guitars'],
                                             frame_length=frame_length, hop_length=hop_length)[0]
        drums_activity = librosa.feature.rms(y=self.separated_sources['drums_low'],
                                            frame_length=frame_length, hop_length=hop_length)[0]
        guira_activity = librosa.feature.rms(y=self.separated_sources['guira'],
                                            frame_length=frame_length, hop_length=hop_length)[0]
        
        times = librosa.frames_to_time(np.arange(len(bass_activity)), sr=self.sr, hop_length=hop_length)
        
        ax6.fill_between(times, 0, bass_activity * 4, alpha=0.7, label='Bass', color='darkblue')
        ax6.fill_between(times, bass_activity * 4, bass_activity * 4 + guitar_activity * 4, 
                        alpha=0.7, label='Guitars', color='green')
        ax6.fill_between(times, bass_activity * 4 + guitar_activity * 4,
                        bass_activity * 4 + guitar_activity * 4 + drums_activity * 4,
                        alpha=0.7, label='Drums/Bongos', color='red')
        ax6.fill_between(times, bass_activity * 4 + guitar_activity * 4 + drums_activity * 4,
                        bass_activity * 4 + guitar_activity * 4 + drums_activity * 4 + guira_activity * 4,
                        alpha=0.7, label='Güira', color='orange')
        
        ax6.set_title('Instrument Activity Timeline', fontsize=10)
        ax6.set_xlabel('Time (s)', fontsize=8)
        ax6.set_ylabel('Activity Level', fontsize=8)
        ax6.legend(loc='upper right', fontsize=8)
        ax6.grid(True, alpha=0.3)
        
        # 7. Spectrogram of full mix
        ax7 = plt.subplot(6, 2, (9, 10))
        D = librosa.amplitude_to_db(np.abs(librosa.stft(self.y)), ref=np.max)
        img = librosa.display.specshow(D, y_axis='log', x_axis='time', sr=self.sr, ax=ax7)
        ax7.set_title('Full Mix Spectrogram', fontsize=10)
        ax7.set_xlabel('Time (s)', fontsize=8)
        ax7.set_ylabel('Frequency (Hz)', fontsize=8)
        plt.colorbar(img, ax=ax7, format='%+2.0f dB')
        
        # 8. Rhythm pattern visualization
        ax8 = plt.subplot(6, 2, (11, 12))
        onset_env = librosa.onset.onset_strength(y=self.y, sr=self.sr)
        tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=self.sr)
        times = librosa.times_like(onset_env, sr=self.sr, hop_length=512)
        
        ax8.plot(times, onset_env, label='Onset Strength', alpha=0.8)
        ax8.vlines(times[beats], 0, onset_env.max(), color='r', alpha=0.6, 
                  linestyle='--', label=f'Beats (Tempo: {tempo:.1f} BPM)')
        ax8.set_title(f'Rhythm Analysis - Tempo: {tempo:.1f} BPM', fontsize=10)
        ax8.set_xlabel('Time (s)', fontsize=8)
        ax8.set_ylabel('Onset Strength', fontsize=8)
        ax8.legend(loc='upper right', fontsize=8)
        ax8.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.show()
        print(f"\nVisualization saved as '{save_path}'")
    
    def full_analysis(self):
        """Perform complete bachata analysis"""
        print("\n" + "="*60)
        print("BACHATA MUSIC ANALYZER")
        print("="*60)
        
        # Genre classification
        genre_result = self.classify_bachata()
        
        print(f"\n{'GENRE CLASSIFICATION':=^60}")
        print(f"Is Bachata: {'YES' if genre_result['is_bachata'] else 'NO'}")
        print(f"Confidence: {genre_result['confidence']:.1%}")
        print(f"Tempo: {genre_result['tempo']:.1f} BPM")
        print(f"  - Tempo Score: {genre_result['tempo_score']:.2f}")
        print(f"  - Rhythm Score: {genre_result['rhythm_score']:.2f}")
        print(f"  - Spectral Score: {genre_result['spectral_score']:.2f}")
        print(f"  - Balance Score: {genre_result['balance_score']:.2f}")
        
        if genre_result['is_bachata']:
            # Source separation
            self.separate_sources()
            
            # Instrument analysis
            inst_results = self.analyze_instruments()
            
            print(f"\n{'INSTRUMENT ANALYSIS':=^60}")
            
            for instrument, data in inst_results.items():
                if data['active']:
                    print(f"\n{instrument.upper().replace('_', ' ')}:")
                    print(f"  - Presence: {data['presence']:.4f}")
                    print(f"  - Variation: {data['variation']:.4f}")
                    
                    if 'tempo' in data:
                        print(f"  - Tempo: {data['tempo']:.1f} BPM")
                    if 'texture' in data:
                        print(f"  - Texture: {data['texture']:.4f}")
                    if 'brightness' in data:
                        print(f"  - Brightness: {data['brightness']:.1f} Hz")
            
            # Visualization
            print(f"\n{'GENERATING VISUALIZATION':=^60}")
            self.visualize_analysis()
            
        else:
            print("\n⚠️  This doesn't appear to be bachata music.")
            print("The analyzer works best with traditional bachata recordings.")
        
        print("\n" + "="*60)
        
        return {
            'genre_classification': genre_result,
            'instrument_analysis': self.instrument_analysis if genre_result['is_bachata'] else None
        }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        analyzer = BachataAnalyzer(sys.argv[1])
        analyzer.full_analysis()
    else:
        print("Usage: python bachata_analyzer.py <audio_file>")