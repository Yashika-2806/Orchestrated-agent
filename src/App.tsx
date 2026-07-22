import React, { useState, useEffect } from 'react';
import { ParameterForm } from './components/ParameterForm';
import { ForecastResults } from './components/ForecastResults';
import { FormulaEngine } from './components/FormulaEngine';
import { TrainingParameters } from './components/TrainingParameters';
import { WeightConfig, defaultWeights } from './components/WeightConfig';
import type { WeightValues } from './components/WeightConfig';
import { GraduationCap, RefreshCw, Layers, Sun, Moon, Zap, Sigma, Database } from 'lucide-react';

const LOADING_STEPS = [
  "Spawning agent environments...",
  "Executing Resume Agent (PDF Text Extraction)...",
  "Scraping GitHub repositories & activity metrics...",
  "Evaluating CP profiles (LeetCode, Codeforces, HackerRank)...",
  "Engaging Inter-Agent Communication Debate...",
  "Synthesizing Career Semantic Profile...",
  "Forecasting Placement Probability & Salary Bands..."
];

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

const App: React.FC = () => {
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(0);
  const [evaluationResult, setEvaluationResult] = useState<Record<string, any> | null>(null);
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    return (localStorage.getItem('theme') as 'dark' | 'light') || 'dark';
  });

  const [activeMode, setActiveMode] = useState<'sandbox' | 'bulk' | 'formula' | 'parameters'>('sandbox');
  const [activePortal, setActivePortal] = useState<'v1' | 'v2'>(() => {
    return (localStorage.getItem('activePortal') as 'v1' | 'v2') || 'v1';
  });
  const [bulkFile, setBulkFile] = useState<File | null>(null);
  const [bulkSubmitting, setBulkSubmitting] = useState<boolean>(false);
  const [bulkResults, setBulkResults] = useState<any[] | null>(null);
  const [selectedBulkStudent, setSelectedBulkStudent] = useState<any | null>(null);
  const [weights, setWeights] = useState<WeightValues>(defaultWeights);
  const [bulkSearchQuery, setBulkSearchQuery] = useState<string>('');
  const [bulkResumes, setBulkResumes] = useState<FileList | null>(null);

  // Apply theme to document element
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Apply version-specific theme class
  useEffect(() => {
    localStorage.setItem('activePortal', activePortal);
    if (activePortal === 'v2') {
      document.documentElement.classList.add('portal-v2');
    } else {
      document.documentElement.classList.remove('portal-v2');
    }
  }, [activePortal]);

  // Cycle through loading steps during submission
  useEffect(() => {
    let interval: any;
    if (submitting) {
      setCurrentStepIndex(0);
      interval = setInterval(() => {
        setCurrentStepIndex((prev) => {
          if (prev < LOADING_STEPS.length - 1) {
            return prev + 1;
          }
          return prev;
        });
      }, 3500); // Shift message every 3.5s
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [submitting]);



  const handleFormSubmit = async (formData: FormData) => {
    setSubmitting(true);
    setEvaluationResult(null);

    try {
      formData.append('version', activePortal);
      Object.entries(weights).forEach(([key, val]) => {
        formData.append(key, val.toString());
      });
      const response = await fetch(`${API_BASE}/api/evaluate`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Server returned an error during prediction');
      }

      const result = await response.json();
      setEvaluationResult(result);
    } catch (error: any) {
      console.error(error);
      alert('Error: ' + (error.message || 'Failed to complete forecast prediction. Running fallback simulation instead.'));
    } finally {
      setSubmitting(false);
    }
  };

  const handleBulkSubmit = async () => {
    if (!bulkFile) return;
    setBulkSubmitting(true);
    setBulkResults(null);
    setSelectedBulkStudent(null);
    
    const formData = new FormData();
    formData.append('file', bulkFile);
    formData.append('version', activePortal);
    
    if (bulkResumes) {
      for (let i = 0; i < bulkResumes.length; i++) {
        formData.append('resumes', bulkResumes[i]);
      }
    }
    
    Object.entries(weights).forEach(([key, val]) => {
      formData.append(key, val.toString());
    });
    
    try {
      const response = await fetch('/api/evaluate-bulk', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Server error running bulk predictions');
      }
      
      const results = await response.json();
      setBulkResults(results);
      if (results.length > 0) {
        setSelectedBulkStudent(results[0]);
      }
    } catch (error: any) {
      console.error(error);
      alert('Error: ' + (error.message || 'Failed to complete bulk predictions. Please verify spreadsheet columns.'));
    } finally {
      setBulkSubmitting(false);
    }
  };

  const handleTemplateUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      const formData = new FormData();
      formData.append('file', file);
      try {
        const response = await fetch('/api/upload-template', {
          method: 'POST',
          body: formData
        });
        if (response.ok) {
          alert('Template uploaded successfully! Future downloads will use this template.');
        } else {
          alert('Failed to upload template.');
        }
      } catch (err) {
        alert('Error uploading template.');
      }
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header-bar">
        <div className="header-title-container">
          <div className="header-logo-glow" style={{ background: activePortal === 'v2' ? 'var(--color-secondary)' : 'var(--color-primary)' }} />
          <h1 style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: 10 }}>
            <Layers size={18} style={{ color: 'var(--color-primary)', transition: 'color var(--transition-normal)' }} />
            GLATalentForecast Sandbox
            {activePortal === 'v2' && (
              <span className="v2-badge" style={{
                background: 'linear-gradient(135deg, #8b5cf6 0%, #d946ef 100%)',
                color: 'white',
                fontSize: '0.65rem',
                padding: '2px 8px',
                borderRadius: '12px',
                fontWeight: 700,
                letterSpacing: '0.05em',
                boxShadow: '0 0 10px rgba(217, 70, 239, 0.4)',
                animation: 'pulse 2s infinite'
              }}>
                AGENT V2
              </span>
            )}
          </h1>
        </div>

        {/* Mode Selector Tabs */}
        <div style={{ display: 'flex', gap: 8, background: 'rgba(99, 102, 241, 0.04)', padding: 4, borderRadius: 10, border: '1px solid var(--border-color)' }}>
          <button 
            type="button"
            onClick={() => setActiveMode('sandbox')}
            className={`tab-button ${activeMode === 'sandbox' ? 'active' : ''}`}
            style={{ padding: '6px 16px', fontSize: '0.8rem', flex: 'none', width: 'auto', display: 'flex', alignItems: 'center', gap: 6 }}
          >
            <Zap size={14} /> Sandbox Mode
          </button>
          <button 
            type="button"
            onClick={() => setActiveMode('bulk')}
            className={`tab-button ${activeMode === 'bulk' ? 'active' : ''}`}
            style={{ padding: '6px 16px', fontSize: '0.8rem', flex: 'none', width: 'auto', display: 'flex', alignItems: 'center', gap: 6 }}
          >
            <Layers size={14} /> Bulk Predictions
          </button>
          <button 
            type="button"
            onClick={() => setActiveMode('formula')}
            className={`tab-button ${activeMode === 'formula' ? 'active' : ''}`}
            style={{ padding: '6px 16px', fontSize: '0.8rem', flex: 'none', width: 'auto', display: 'flex', alignItems: 'center', gap: 6 }}
          >
            <Sigma size={14} /> Formula Engine
          </button>
          <button 
            type="button"
            onClick={() => setActiveMode('parameters')}
            className={`tab-button ${activeMode === 'parameters' ? 'active' : ''}`}
            style={{ padding: '6px 16px', fontSize: '0.8rem', flex: 'none', width: 'auto', display: 'flex', alignItems: 'center', gap: 6 }}
          >
            <Database size={14} /> Parameters
          </button>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
          {/* Portal Switcher */}
          <div style={{ display: 'flex', gap: 4, background: 'rgba(99, 102, 241, 0.04)', padding: 3, borderRadius: 8, border: '1px solid var(--border-color)' }}>
            <button 
              type="button"
              onClick={() => setActivePortal('v1')}
              className={`tab-button ${activePortal === 'v1' ? 'active' : ''}`}
              style={{ padding: '4px 12px', fontSize: '0.72rem', fontWeight: 600, flex: 'none', width: 'auto', display: 'flex', alignItems: 'center', gap: 4, borderRadius: 6 }}
            >
              V1 Engine
            </button>
            <button 
              type="button"
              onClick={() => setActivePortal('v2')}
              className={`tab-button ${activePortal === 'v2' ? 'active' : ''}`}
              style={{ 
                padding: '4px 12px', 
                fontSize: '0.72rem', 
                fontWeight: 600, 
                flex: 'none', 
                width: 'auto', 
                display: 'flex', 
                alignItems: 'center', 
                gap: 4, 
                borderRadius: 6,
                background: activePortal === 'v2' ? 'linear-gradient(135deg, #8b5cf6 0%, #d946ef 100%)' : '',
                color: activePortal === 'v2' ? '#fff' : '',
                border: activePortal === 'v2' ? 'none' : ''
              }}
            >
              V2 Premium
            </button>
          </div>

          <button 
            type="button"
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            className="theme-toggle-btn"
            title="Toggle color theme"
          >
            {theme === 'dark' ? <Sun size={15} /> : <Moon size={15} />}
            <span style={{ fontSize: '0.78rem', fontWeight: 600 }}>
              {theme === 'dark' ? 'Light Theme' : 'Dark Theme'}
            </span>
          </button>
        </div>
      </header>

      {/* Global Configuration applies to both Sandbox and Bulk */}
      {activeMode !== 'formula' && activeMode !== 'parameters' && (
        <WeightConfig weights={weights} onChange={setWeights} />
      )}

      {activeMode === 'parameters' ? (
        <main className="main-dashboard" style={{ display: 'block', maxWidth: 1100, margin: '0 auto' }}>
          <TrainingParameters />
        </main>
      ) : activeMode === 'formula' ? (
        <main className="main-dashboard" style={{ display: 'block', maxWidth: 1100, margin: '0 auto' }}>
          <FormulaEngine />
        </main>
      ) : activeMode === 'sandbox' ? (
        <main className="main-dashboard">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            <ParameterForm 
              initialValues={{}} 
              onSubmit={handleFormSubmit} 
              submitting={submitting} 
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            {submitting ? (
              <div className="glass-card loading-overlay">
                <div className="spinner-glow">
                  <div className="spinner-inner" />
                </div>
                <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', gap: 8 }}>
                  <div style={{ fontWeight: 700, fontSize: '1.1rem' }}>Executing Orchestrator Agents</div>
                  <p style={{ color: 'var(--text-dim)', fontSize: '0.85rem' }}>
                    Please wait, gathering cross-platform evidence and consensus matrix.
                  </p>
                </div>
                <div className="loading-steps-container">
                  {LOADING_STEPS.map((step, i) => {
                    let stepClass = "";
                    if (i === currentStepIndex) stepClass = "active";
                    else if (i < currentStepIndex) stepClass = "completed";
                    return (
                      <div key={i} className={`loading-step ${stepClass}`}>
                        <div className="loading-step-bullet" />
                        <span>{step}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              <ForecastResults data={evaluationResult!} />
            )}
          </div>
        </main>
      ) : activeMode === 'bulk' ? (
        <main className="main-dashboard">
          {/* Left panel: File Upload & Student Selection List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            <div className="glass-card" style={{ padding: 24 }}>
              <h3 style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8, fontSize: '1.05rem', fontWeight: 700 }}>
                <Layers size={18} style={{ color: 'var(--color-primary)' }} />
                Bulk Predictions Upload
              </h3>
              
              {/* Download / Upload CSV Template Buttons */}
              <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
                <a 
                  href={`/api/download-template?version=${activePortal}`} 
                  download
                  className="theme-toggle-btn"
                  style={{ flex: 1, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 6, justifyContent: 'center', fontSize: '0.75rem', padding: '8px 12px', background: 'rgba(99, 102, 241, 0.05)', border: '1px solid var(--border-color)', borderRadius: 8, color: 'var(--text-main)', cursor: 'pointer' }}
                >
                  <GraduationCap size={14} /> Download Template
                </a>
                <label className="theme-toggle-btn" style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 6, justifyContent: 'center', fontSize: '0.75rem', padding: '8px 12px', background: 'rgba(236, 72, 153, 0.05)', border: '1px solid var(--border-color)', borderRadius: 8, color: 'var(--text-main)', cursor: 'pointer' }}>
                  <RefreshCw size={14} /> Upload Custom
                  <input type="file" accept=".csv,.xlsx,.xls" style={{display: 'none'}} onChange={handleTemplateUpload} />
                </label>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                <label className="form-label" style={{ fontSize: '0.8rem' }}>Upload Student Spreadsheet</label>
                <input 
                  type="file" 
                  accept=".csv,.xlsx,.xls" 
                  onChange={(e) => {
                    if (e.target.files && e.target.files.length > 0) {
                      setBulkFile(e.target.files[0]);
                    }
                  }}
                  style={{ display: 'none' }}
                  id="bulk-file-input"
                />
                <label 
                  htmlFor="bulk-file-input"
                  className={`file-upload-area ${bulkFile ? 'has-file' : ''}`}
                  style={{ padding: '20px 16px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', border: '2px dashed var(--border-color)', borderRadius: 10, cursor: 'pointer', textAlign: 'center', gap: 6 }}
                >
                  <RefreshCw size={20} className="file-upload-icon" />
                  <div style={{ fontWeight: 600, fontSize: '0.78rem' }}>
                    {bulkFile ? bulkFile.name : 'Select Spreadsheet'}
                  </div>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-dim)' }}>
                    Excel (.xlsx) or CSV format
                  </div>
                </label>

                {/* Multiple Resume File Upload */}
                <label className="form-label" style={{ fontSize: '0.8rem', marginTop: 6 }}>Upload Resumes (Multiple PDFs)</label>
                <input 
                  type="file" 
                  multiple
                  accept=".pdf" 
                  onChange={(e) => {
                    if (e.target.files && e.target.files.length > 0) {
                      setBulkResumes(e.target.files);
                    }
                  }}
                  style={{ display: 'none' }}
                  id="bulk-resumes-input"
                />
                <label 
                  htmlFor="bulk-resumes-input"
                  className={`file-upload-area ${bulkResumes ? 'has-file' : ''}`}
                  style={{ padding: '20px 16px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', border: '2px dashed var(--border-color)', borderRadius: 10, cursor: 'pointer', textAlign: 'center', gap: 6 }}
                >
                  <RefreshCw size={20} className="file-upload-icon" />
                  <div style={{ fontWeight: 600, fontSize: '0.78rem' }}>
                    {bulkResumes ? `${bulkResumes.length} PDF(s) Selected` : 'Select Student Resumes'}
                  </div>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-dim)' }}>
                    Match PDFs by Roll No or Student Name
                  </div>
                </label>
                
                <button 
                  type="button"
                  onClick={handleBulkSubmit}
                  disabled={bulkSubmitting || !bulkFile}
                  className="btn-primary"
                  style={{ marginTop: 8 }}
                >
                  {bulkSubmitting ? 'Evaluating Students Batch...' : 'Run Bulk Predictions'}
                </button>
              </div>
            </div>

            {bulkResults && (
              <div className="glass-card" style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 12, overflow: 'hidden', minHeight: 350, maxHeight: 400 }}>
                <h3 style={{ fontSize: '0.9rem', fontWeight: 700, margin: 0 }}>Processed Students ({bulkResults.length})</h3>
                
                <input 
                  type="text"
                  placeholder="Search students..."
                  value={bulkSearchQuery}
                  onChange={(e) => setBulkSearchQuery(e.target.value)}
                  className="form-input"
                  style={{ margin: 0, padding: '8px 12px', fontSize: '0.8rem' }}
                />
                
                <div style={{ overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 8, paddingRight: 4 }}>
                  {bulkResults
                    .filter(s => s.name.toLowerCase().includes(bulkSearchQuery.toLowerCase()) || s.student_id.includes(bulkSearchQuery))
                    .map((student, idx) => {
                      const prob = student.forecasting?.placement_probability || 0;
                      const isAct = selectedBulkStudent?.student_id === student.student_id;
                      
                      return (
                        <div 
                          key={student.student_id || idx}
                          onClick={() => setSelectedBulkStudent(student)}
                          style={{
                            background: isAct ? 'rgba(99, 102, 241, 0.15)' : 'rgba(255,255,255,0.01)',
                            border: isAct ? '1.5px solid var(--color-primary)' : '1px solid var(--border-color)',
                            borderRadius: 8,
                            padding: '10px 12px',
                            cursor: 'pointer',
                            transition: 'all var(--transition-fast)'
                          }}
                        >
                          <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--text-main)' }}>{student.name}</div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: 4 }}>
                            <span>Roll: {student.student_id}</span>
                            <span style={{ color: prob >= 50 ? 'var(--color-success)' : 'var(--color-danger)', fontWeight: 600 }}>
                              {prob}% Prob
                            </span>
                          </div>
                        </div>
                      );
                    })}
                </div>
              </div>
            )}
          </div>

          {/* Right panel: Detailed Results */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            {bulkSubmitting ? (
              <div className="glass-card loading-overlay" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 48, minHeight: 400 }}>
                <div className="spinner-glow" style={{ marginBottom: 16 }}>
                  <div className="spinner-inner" />
                </div>
                <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', gap: 8 }}>
                  <div style={{ fontWeight: 700, fontSize: '1.1rem' }}>Processing Bulk Predictions</div>
                  <p style={{ color: 'var(--text-dim)', fontSize: '0.85rem' }}>
                    Running parallel multi-agent orchestrator algorithms on spreadsheet records...
                  </p>
                </div>
              </div>
            ) : selectedBulkStudent ? (
              <ForecastResults data={selectedBulkStudent} />
            ) : (
              <div className="glass-card" style={{ padding: 48, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', minHeight: 400, textAlign: 'center', gap: 16 }}>
                <Layers size={48} style={{ color: 'var(--text-dim)' }} />
                <div style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-main)' }}>Select Student to Inspect</div>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', maxWidth: 320, margin: 0, lineHeight: 1.4 }}>
                  Upload a student sheet on the left, click predictions, and select any processed student from the list to view their detailed metrics.
                </p>
              </div>
            )}
          </div>
        </main>
      ) : null}
    </div>
  );
};

export default App;
