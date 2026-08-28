import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import audioService from '../services/audioService';
import { useLiveAudioRecorder } from '../hooks/useLiveAudioRecorder';
import { 
  UploadCloud, 
  Mic, 
  MicOff, 
  Heart, 
  Wind, 
  Sliders, 
  FileAudio, 
  CheckCircle2, 
  AlertCircle, 
  Play, 
  Pause,
  RotateCcw,
  Activity,
  ArrowRight
} from 'lucide-react';

const CHEST_LOCATIONS = {
  heart: [
    { id: 'Apex', label: 'Apex (Mitral Valve area)' },
    { id: 'LUSB', label: 'LUSB (Pulmonary Valve area)' },
    { id: 'RUSB', label: 'RUSB (Aortic Valve area)' },
    { id: 'LLSB', label: 'LLSB (Tricuspid Valve area)' },
    { id: 'LC', label: 'Left Clavicular' },
    { id: 'RC', label: 'Right Clavicular' },
  ],
  lung: [
    { id: 'LUA', label: 'Left Upper Anterior' },
    { id: 'RUA', label: 'Right Upper Anterior' },
    { id: 'LMA', label: 'Left Mid Anterior' },
    { id: 'RMA', label: 'Right Mid Anterior' },
    { id: 'LLA', label: 'Left Lower Anterior' },
    { id: 'RLA', label: 'Right Lower Anterior' },
  ],
  mixed: [
    { id: 'Apex', label: 'Apex' },
    { id: 'LUSB', label: 'Left Upper Sternal Border' },
    { id: 'LUA', label: 'Left Upper Anterior' },
  ],
};

export const NewAnalysisPage: React.FC = () => {
  const [mode, setMode] = useState<'upload' | 'record'>('upload');
  const [file, setFile] = useState<File | null>(null);
  const [uploadAudioUrl, setUploadAudioUrl] = useState<string | null>(null);
  const [isPlayingUpload, setIsPlayingUpload] = useState(false);
  const [isPlayingRecord, setIsPlayingRecord] = useState(false);
  
  const [category, setCategory] = useState<'heart' | 'lung' | 'mixed'>('heart');
  const [location, setLocation] = useState('Apex');
  const [patientGender, setPatientGender] = useState<'M' | 'F' | 'Other'>('M');
  const [patientAge, setPatientAge] = useState<string>('45');
  const [clinicalNotes, setClinicalNotes] = useState('');
  
  const [loadingStep, setLoadingStep] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const uploadAudioRef = useRef<HTMLAudioElement>(null);
  const recordAudioRef = useRef<HTMLAudioElement>(null);
  const navigate = useNavigate();

  // In-browser MediaRecorder Hook
  const {
    isRecording,
    recordingTime,
    audioBlob,
    audioUrl: recordedAudioUrl,
    audioLevel,
    startRecording,
    stopRecording,
    resetRecording,
    error: recorderError,
  } = useLiveAudioRecorder();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      if (!selected.name.toLowerCase().endsWith('.wav')) {
        setError('Only .wav format files from digital stethoscopes are supported.');
        return;
      }
      setError(null);
      setFile(selected);
      setUploadAudioUrl(URL.createObjectURL(selected));
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const dropped = e.dataTransfer.files[0];
      if (!dropped.name.toLowerCase().endsWith('.wav')) {
        setError('Only .wav audio recordings are supported.');
        return;
      }
      setError(null);
      setFile(dropped);
      setUploadAudioUrl(URL.createObjectURL(dropped));
    }
  };

  const handleCategoryChange = (newCat: 'heart' | 'lung' | 'mixed') => {
    setCategory(newCat);
    setLocation(CHEST_LOCATIONS[newCat][0].id);
  };

  const togglePlayUpload = () => {
    if (!uploadAudioRef.current) return;
    if (isPlayingUpload) {
      uploadAudioRef.current.pause();
      setIsPlayingUpload(false);
    } else {
      uploadAudioRef.current.play();
      setIsPlayingUpload(true);
    }
  };

  const togglePlayRecord = () => {
    if (!recordAudioRef.current) return;
    if (isPlayingRecord) {
      recordAudioRef.current.pause();
      setIsPlayingRecord(false);
    } else {
      recordAudioRef.current.play();
      setIsPlayingRecord(true);
    }
  };

  const formatTimer = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    let audioToSubmit: File | null = null;
    let fileName = '';

    if (mode === 'upload') {
      if (!file) {
        setError('Please select or drop a .wav digital stethoscope recording.');
        return;
      }
      audioToSubmit = file;
      fileName = file.name;
    } else {
      if (!audioBlob) {
        setError('Please record audio with the in-browser stethoscope recorder.');
        return;
      }
      fileName = `live_steth_${Date.now()}.wav`;
      audioToSubmit = new File([audioBlob], fileName, { type: 'audio/wav' });
    }

    try {
      // Step 1: POST /api/audio/upload
      setLoadingStep('Uploading audio recording to clinical archive...');
      const uploadFormData = new FormData();
      uploadFormData.append('file', audioToSubmit);
      uploadFormData.append('sound_category', category);
      uploadFormData.append('chest_location', location);
      if (patientGender) uploadFormData.append('patient_gender', patientGender);
      if (patientAge) uploadFormData.append('patient_age', patientAge);
      if (clinicalNotes) uploadFormData.append('clinical_notes', clinicalNotes);

      const recordingMeta = await audioService.uploadAudio(uploadFormData);

      // Step 2: POST /api/audio/analyze
      setLoadingStep('Running Mel-Spectrogram transformation & Grad-CAM neural inference...');
      const analyzeFormData = new FormData();
      analyzeFormData.append('recording_id', recordingMeta.id);

      const analysisResult = await audioService.analyzeAudio(analyzeFormData);

      // Transition to result page
      navigate('/analysis-result', {
        state: {
          result: analysisResult,
          file_name: fileName,
          chest_location: location,
        },
      });
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'AI screening failed. Please check your audio file.';
      setError(msg);
      setLoadingStep(null);
    }
  };

  const hasValidAudio = (mode === 'upload' && file !== null) || (mode === 'record' && audioBlob !== null);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      
      {/* Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-100 tracking-tight">
          New Auscultation Screening
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Upload or capture digital stethoscope audio for instant Mel-spectrogram & Grad-CAM neural diagnosis.
        </p>
      </div>

      {(error || recorderError) && (
        <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/20 flex items-start gap-3 text-rose-400 text-sm">
          <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
          <span>{error || recorderError}</span>
        </div>
      )}

      {/* Mode Switcher Tabs */}
      <div className="grid grid-cols-2 p-1.5 bg-slate-900 border border-slate-800 rounded-2xl">
        <button
          type="button"
          onClick={() => setMode('upload')}
          className={`py-2.5 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 ${
            mode === 'upload'
              ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/20'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <UploadCloud className="w-4 h-4" />
          <span>Upload .WAV File</span>
        </button>
        <button
          type="button"
          onClick={() => setMode('record')}
          className={`py-2.5 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 ${
            mode === 'record'
              ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/20'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Mic className="w-4 h-4" />
          <span>Record Live Stethoscope</span>
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        
        {/* Input Container: Upload vs Live Recording */}
        {mode === 'upload' ? (
          <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl">
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3">
              1. Digital Stethoscope Audio File (.wav)
            </label>

            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all ${
                file
                  ? 'border-cyan-500/50 bg-cyan-500/5'
                  : 'border-slate-800 hover:border-slate-700 bg-slate-950/50 hover:bg-slate-950/80'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".wav"
                onChange={handleFileChange}
                className="hidden"
              />

              {file ? (
                <div className="flex flex-col items-center gap-3">
                  <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center border border-cyan-500/20">
                    <FileAudio className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-sm text-slate-200">{file.name}</h3>
                    <span className="text-xs text-slate-500">
                      {(file.size / 1024).toFixed(1)} KB • Digital PCM WAV
                    </span>
                  </div>
                  <span className="text-xs font-medium text-cyan-400 bg-cyan-500/10 px-3 py-1 rounded-full border border-cyan-500/20 mt-1">
                    Audio Loaded (Click to change)
                  </span>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-3">
                  <div className="w-12 h-12 rounded-2xl bg-slate-800 text-slate-400 flex items-center justify-center">
                    <UploadCloud className="w-6 h-6" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-200">
                      Drag & drop digital stethoscope recording, or <span className="text-cyan-400">browse</span>
                    </p>
                    <p className="text-xs text-slate-500 mt-1">Standard 16-bit PCM WAV (1s – 60s)</p>
                  </div>
                </div>
              )}
            </div>

            {/* Audio Preview Player */}
            {uploadAudioUrl && (
              <div className="mt-4 p-3 bg-slate-950 border border-slate-800 rounded-xl flex items-center justify-between">
                <audio
                  ref={uploadAudioRef}
                  src={uploadAudioUrl}
                  onEnded={() => setIsPlayingUpload(false)}
                  className="hidden"
                />
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={togglePlayUpload}
                    className="w-9 h-9 rounded-xl bg-cyan-500 text-white flex items-center justify-center shadow-md shadow-cyan-500/20 hover:scale-105 active:scale-95 transition-transform"
                  >
                    {isPlayingUpload ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 fill-white ml-0.5" />}
                  </button>
                  <span className="text-xs font-medium text-slate-300">Preview Audio File</span>
                </div>
                <span className="text-xs text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Ready
                </span>
              </div>
            )}
          </div>
        ) : (
          /* Live Recording Component */
          <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-6">
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
              1. In-Browser Live Stethoscope Recording
            </label>

            <div className="bg-slate-950 rounded-2xl border border-slate-800 p-6 flex flex-col items-center justify-center text-center gap-5">
              
              {/* Timer Display */}
              <div className="flex flex-col items-center">
                <span className="font-mono text-3xl sm:text-4xl font-black text-slate-100 tracking-wider">
                  {formatTimer(recordingTime)}
                </span>
                <span className="text-xs text-slate-500 mt-1">
                  {isRecording ? 'Listening via Stethoscope/Microphone...' : 'Recommended duration: 5 – 15 seconds'}
                </span>
              </div>

              {/* Audio Meter Visualizer */}
              {isRecording && (
                <div className="w-full max-w-xs space-y-2">
                  <div className="flex justify-between text-[10px] text-slate-400">
                    <span>Input Level</span>
                    <span className="text-cyan-400">{audioLevel}%</span>
                  </div>
                  <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-cyan-500 to-rose-500 transition-all duration-75"
                      style={{ width: `${audioLevel}%` }}
                    ></div>
                  </div>
                </div>
              )}

              {/* Recording Controls */}
              <div className="flex items-center gap-4">
                {!isRecording ? (
                  <button
                    type="button"
                    onClick={startRecording}
                    className="px-6 py-3 rounded-2xl bg-rose-600 hover:bg-rose-500 text-white font-bold text-sm shadow-xl shadow-rose-600/30 flex items-center gap-2.5 transition-all hover:scale-105 active:scale-95"
                  >
                    <Mic className="w-5 h-5" />
                    <span>{audioBlob ? 'Record Again' : 'Start Recording'}</span>
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={stopRecording}
                    className="px-6 py-3 rounded-2xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-sm shadow-xl shadow-amber-500/30 flex items-center gap-2.5 transition-all animate-pulse"
                  >
                    <MicOff className="w-5 h-5" />
                    <span>Stop Recording</span>
                  </button>
                )}

                {audioBlob && !isRecording && (
                  <button
                    type="button"
                    onClick={resetRecording}
                    className="p-3 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                    title="Clear Recording"
                  >
                    <RotateCcw className="w-5 h-5" />
                  </button>
                )}
              </div>

              {/* Recorded Audio Playback */}
              {recordedAudioUrl && !isRecording && (
                <div className="w-full mt-2 p-3 bg-slate-900 border border-slate-800 rounded-xl flex items-center justify-between">
                  <audio
                    ref={recordAudioRef}
                    src={recordedAudioUrl}
                    onEnded={() => setIsPlayingRecord(false)}
                    className="hidden"
                  />
                  <div className="flex items-center gap-3">
                    <button
                      type="button"
                      onClick={togglePlayRecord}
                      className="w-9 h-9 rounded-xl bg-cyan-500 text-white flex items-center justify-center shadow-md shadow-cyan-500/20 hover:scale-105 active:scale-95 transition-transform"
                    >
                      {isPlayingRecord ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 fill-white ml-0.5" />}
                    </button>
                    <span className="text-xs font-medium text-slate-300">Playback Captured Stethoscope Audio</span>
                  </div>
                  <span className="text-xs text-emerald-400 flex items-center gap-1 font-semibold">
                    <CheckCircle2 className="w-4 h-4" />
                    Encoded (4000 Hz WAV)
                  </span>
                </div>
              )}

            </div>
          </div>
        )}

        {/* Diagnostic Category & Auscultation Site */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-6">
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
            2. Sound Category & Chest Auscultation Site
          </label>

          {/* Category Toggle Buttons */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <button
              type="button"
              onClick={() => handleCategoryChange('heart')}
              className={`p-4 rounded-2xl border text-center transition-all flex flex-col items-center gap-2 ${
                category === 'heart'
                  ? 'border-rose-500/50 bg-rose-500/10 text-rose-300 shadow-lg shadow-rose-500/10'
                  : 'border-slate-800 bg-slate-950/40 text-slate-400 hover:border-slate-700'
              }`}
            >
              <Heart className="w-6 h-6 text-rose-400" />
              <span className="text-xs font-bold uppercase tracking-wider">Heart Sounds</span>
            </button>

            <button
              type="button"
              onClick={() => handleCategoryChange('lung')}
              className={`p-4 rounded-2xl border text-center transition-all flex flex-col items-center gap-2 ${
                category === 'lung'
                  ? 'border-cyan-500/50 bg-cyan-500/10 text-cyan-300 shadow-lg shadow-cyan-500/10'
                  : 'border-slate-800 bg-slate-950/40 text-slate-400 hover:border-slate-700'
              }`}
            >
              <Wind className="w-6 h-6 text-cyan-400" />
              <span className="text-xs font-bold uppercase tracking-wider">Lung Sounds</span>
            </button>

            <button
              type="button"
              onClick={() => handleCategoryChange('mixed')}
              className={`p-4 rounded-2xl border text-center transition-all flex flex-col items-center gap-2 ${
                category === 'mixed'
                  ? 'border-blue-500/50 bg-blue-500/10 text-blue-300 shadow-lg shadow-blue-500/10'
                  : 'border-slate-800 bg-slate-950/40 text-slate-400 hover:border-slate-700'
              }`}
            >
              <Sliders className="w-6 h-6 text-blue-400" />
              <span className="text-xs font-bold uppercase tracking-wider">Mixed Sounds</span>
            </button>
          </div>

          {/* Location Dropdown */}
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-2">
              Chest Anatomical Location:
            </label>
            <select
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
            >
              {CHEST_LOCATIONS[category].map((loc) => (
                <option key={loc.id} value={loc.id}>
                  {loc.id} — {loc.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Patient Context (Optional) */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
            3. Patient Information (Optional)
          </label>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-slate-400 mb-1.5">Gender</label>
              <select
                value={patientGender}
                onChange={(e) => setPatientGender(e.target.value as any)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
              >
                <option value="M">Male (M)</option>
                <option value="F">Female (F)</option>
                <option value="Other">Other / Unspecified</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1.5">Age (Years)</label>
              <input
                type="number"
                value={patientAge}
                onChange={(e) => setPatientAge(e.target.value)}
                placeholder="Age in years"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs text-slate-400 mb-1.5">Clinical Notes</label>
            <textarea
              rows={2}
              value={clinicalNotes}
              onChange={(e) => setClinicalNotes(e.target.value)}
              placeholder="e.g. Holosystolic murmur audible at apex radiating to axilla..."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loadingStep !== null || !hasValidAudio}
          className="w-full py-4 rounded-2xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-extrabold text-base shadow-xl shadow-cyan-500/25 hover:opacity-95 hover:scale-[1.01] active:scale-[0.99] transition-all flex items-center justify-center gap-3 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {loadingStep ? (
            <div className="flex items-center gap-3">
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
              <span className="text-sm">{loadingStep}</span>
            </div>
          ) : (
            <>
              <Activity className="w-5 h-5" />
              <span>Run AI Stethoscope Diagnosis</span>
              <ArrowRight className="w-5 h-5" />
            </>
          )}
        </button>

      </form>
    </div>
  );
};
