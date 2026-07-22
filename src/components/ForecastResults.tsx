import React, { useState } from 'react';
import { Award, MessageSquare, BarChart3, Star, AlertTriangle, CheckCircle, HelpCircle, Briefcase, Zap, AlertOctagon, Sliders, RefreshCw } from 'lucide-react';

interface ForecastResultsProps {
  data: Record<string, any>;
}

interface XAIDriver {
  name: string;
  value: string | number;
  impact: number;
  description: string;
  status: 'positive' | 'negative' | 'neutral';
}

interface XAIWeights {
  gpa: number;
  backlogs_bonus: number;
  backlogs_penalty: number;
  dsa: number;
  attendance: number;
  internships: number;
  github: number;
  cp: number;
}

const calculateXAI = (inputs: Record<string, any> = {}, scores: Record<string, any> = {}, weights: XAIWeights): XAIDriver[] => {
  const parseNum = (val: any, fallback = 0) => {
    if (val === undefined || val === null || val === '') return fallback;
    const parsed = parseFloat(val);
    return isNaN(parsed) ? fallback : parsed;
  };

  const isValidProfile = (url: any) => {
    if (!url) return false;
    const str = String(url).trim().toLowerCase();
    return str !== '' && str !== 'none' && str !== 'null' && !str.endsWith('/u/') && !str.endsWith('/profile/') && !str.endsWith('/users/');
  };

  const cpiVal = parseNum(inputs.cpi || inputs.gpa || inputs.CPI || inputs["Current CPI"], 7.5);
  const backlogsVal = parseNum(inputs.backlogs || inputs["Backlogs Count"], 0);
  const dsaVal = parseNum(inputs.dsa_marks || inputs["DSA marks (in Btech)"], 70);
  const attendanceVal = parseNum(inputs.attendance || inputs["What is your attendance in your current semester?"], 85);
  const internshipsVal = parseNum(inputs.internships_count || inputs["Number of internships completed"], 0);
  const githubScore = scores.github_score || 0;
  const cpScore = scores.cp_score || 0;

  const hasGithub = isValidProfile(inputs.github_url || inputs.github || inputs["GitHub Profile URL"]);
  const hasCp = isValidProfile(inputs.leetcode_url || inputs.leetcode || inputs["Leetcode"]) ||
                isValidProfile(inputs.codeforces_url || inputs.codeforces || inputs["Codeforces"]) ||
                isValidProfile(inputs.codechef_url || inputs.codechef || inputs["Codechef"]) ||
                isValidProfile(inputs.hackerrank_url || inputs.hackerrank || inputs["Hackerrank"]);

  const drivers: XAIDriver[] = [];

  // 1. GPA Attribution
  if (cpiVal >= 8.5) {
    drivers.push({
      name: 'Academic GPA (CPI)',
      value: cpiVal,
      impact: weights.gpa,
      description: `GPA of ${cpiVal} is well above average, heavily driving the tech score.`,
      status: 'positive'
    });
  } else if (cpiVal >= 7.5) {
    drivers.push({
      name: 'Academic GPA (CPI)',
      value: cpiVal,
      impact: Math.round(weights.gpa * 0.48),
      description: `GPA of ${cpiVal} is standard and meets requirements, contributing positively.`,
      status: 'positive'
    });
  } else if (cpiVal >= 6.0) {
    drivers.push({
      name: 'Academic GPA (CPI)',
      value: cpiVal,
      impact: Math.round(weights.gpa * 0.08),
      description: `GPA of ${cpiVal} is average, with minimal prediction impact.`,
      status: 'neutral'
    });
  } else {
    drivers.push({
      name: 'Academic GPA (CPI)',
      value: cpiVal,
      impact: -Math.round(weights.gpa * 0.72),
      description: `GPA of ${cpiVal} is below standard, negatively gating readiness classification.`,
      status: 'negative'
    });
  }

  // 2. Backlogs Attribution
  if (backlogsVal === 0) {
    drivers.push({
      name: 'Active Backlogs',
      value: backlogsVal,
      impact: weights.backlogs_bonus,
      description: 'Zero active backlogs ensures eligibility compliance.',
      status: 'positive'
    });
  } else {
    const penalty = -weights.backlogs_penalty * backlogsVal;
    drivers.push({
      name: 'Active Backlogs',
      value: backlogsVal,
      impact: penalty,
      description: `${backlogsVal} active backlog(s) triggers high risk and score penalties.`,
      status: 'negative'
    });
  }

  // 3. DSA Marks Attribution
  if (dsaVal >= 85) {
    drivers.push({
      name: 'DSA Course Marks',
      value: `${dsaVal}%`,
      impact: weights.dsa,
      description: `DSA marks of ${dsaVal}% indicates highly competitive programming foundations.`,
      status: 'positive'
    });
  } else if (dsaVal >= 70) {
    drivers.push({
      name: 'DSA Course Marks',
      value: `${dsaVal}%`,
      impact: Math.round(weights.dsa * 0.4),
      description: `DSA marks of ${dsaVal}% demonstrates sufficient algorithmic foundations.`,
      status: 'positive'
    });
  } else if (dsaVal >= 50) {
    drivers.push({
      name: 'DSA Course Marks',
      value: `${dsaVal}%`,
      impact: 0,
      description: `DSA marks of ${dsaVal}% is average, showing neutral placement correlation.`,
      status: 'neutral'
    });
  } else {
    drivers.push({
      name: 'DSA Course Marks',
      value: `${dsaVal}%`,
      impact: -Math.round(weights.dsa * 0.75),
      description: `DSA marks of ${dsaVal}% is low, flagging major coding knowledge gaps.`,
      status: 'negative'
    });
  }

  // 4. Attendance Attribution
  if (attendanceVal >= 85) {
    drivers.push({
      name: 'Semester Attendance',
      value: `${attendanceVal}%`,
      impact: weights.attendance,
      description: `Attendance is high at ${attendanceVal}%, supporting strong academic discipline.`,
      status: 'positive'
    });
  } else if (attendanceVal >= 75) {
    drivers.push({
      name: 'Semester Attendance',
      value: `${attendanceVal}%`,
      impact: 0,
      description: `Attendance of ${attendanceVal}% is standard and satisfies eligibility gates.`,
      status: 'neutral'
    });
  } else {
    drivers.push({
      name: 'Semester Attendance',
      value: `${attendanceVal}%`,
      impact: -weights.attendance * 2,
      description: `Attendance is critically low at ${attendanceVal}%, raising placement risk factors.`,
      status: 'negative'
    });
  }

  // 5. Internships Attribution
  if (internshipsVal > 0) {
    drivers.push({
      name: 'Internships Completed',
      value: internshipsVal,
      impact: weights.internships,
      description: `${internshipsVal} internship(s) completed highly boosts industry alignment score.`,
      status: 'positive'
    });
  } else {
    drivers.push({
      name: 'Internships Completed',
      value: internshipsVal,
      impact: -Math.round(weights.internships * 0.33),
      description: 'No completed internships reduces hands-on industry exposure.',
      status: 'negative'
    });
  }

  // 6. GitHub Profile Attribution
  if (!hasGithub) {
    drivers.push({
      name: 'GitHub Agent Rating',
      value: 'Not Linked',
      impact: 0,
      description: 'No GitHub profile linked. Evaluation is based on academic and resume data.',
      status: 'neutral'
    });
  } else if (githubScore >= 75) {
    drivers.push({
      name: 'GitHub Agent Rating',
      value: `${githubScore.toFixed(0)}%`,
      impact: weights.github,
      description: 'Highly active repository contribution and regular commit activity verified.',
      status: 'positive'
    });
  } else if (githubScore >= 45) {
    drivers.push({
      name: 'GitHub Agent Rating',
      value: `${githubScore.toFixed(0)}%`,
      impact: Math.round(weights.github * 0.5),
      description: 'Steady open-source contribution and code repository commits verified.',
      status: 'positive'
    });
  } else if (githubScore > 0) {
    drivers.push({
      name: 'GitHub Agent Rating',
      value: `${githubScore.toFixed(0)}%`,
      impact: Math.round(weights.github * 0.1),
      description: 'Average repository metrics, with low predictive correlation.',
      status: 'neutral'
    });
  } else {
    drivers.push({
      name: 'GitHub Agent Rating',
      value: 'None',
      impact: -Math.round(weights.github * 0.5),
      description: 'No GitHub commits found; penalised for lack of code contribution evidence.',
      status: 'negative'
    });
  }

  // 7. CP Clout Attribution
  if (!hasCp) {
    drivers.push({
      name: 'CP Platform Clout',
      value: 'Not Linked',
      impact: 0,
      description: 'No CP platform profile linked. Algorithmic rating is omitted from evaluation.',
      status: 'neutral'
    });
  } else if (cpScore < githubScore && githubScore >= 60) {
    drivers.push({
      name: 'CP Platform Clout',
      value: `${cpScore.toFixed(0)}%`,
      impact: 0,
      description: 'CP platform activity is low, but compensated by strong GitHub contribution rating.',
      status: 'neutral'
    });
  } else if (cpScore >= 75) {
    drivers.push({
      name: 'CP Platform Clout',
      value: `${cpScore.toFixed(0)}%`,
      impact: weights.cp,
      description: 'Excellent problem solving ratings on LeetCode/Codeforces.',
      status: 'positive'
    });
  } else if (cpScore >= 45) {
    drivers.push({
      name: 'CP Platform Clout',
      value: `${cpScore.toFixed(0)}%`,
      impact: Math.round(weights.cp * 0.45),
      description: 'Consistent daily problems solved and contest activity verified.',
      status: 'positive'
    });
  } else if (cpScore > 0) {
    drivers.push({
      name: 'CP Platform Clout',
      value: `${cpScore.toFixed(0)}%`,
      impact: Math.round(weights.cp * 0.09),
      description: 'Minor competitive programming practice, with neutral prediction impact.',
      status: 'neutral'
    });
  } else {
    drivers.push({
      name: 'CP Platform Clout',
      value: 'None',
      impact: -Math.round(weights.cp * 0.45),
      description: 'No CP platform activity found; penalised for lack of algorithmic evidence.',
      status: 'negative'
    });
  }

  return drivers;
};

export const ForecastResults: React.FC<ForecastResultsProps> = ({ data }) => {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [weights, setWeights] = useState<XAIWeights>(() => {
    const saved = localStorage.getItem('xai_weights');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {}
    }
    return {
      gpa: 25,
      backlogs_bonus: 8,
      backlogs_penalty: 12,
      dsa: 20,
      attendance: 10,
      internships: 15,
      github: 20,
      cp: 22
    };
  });

  const handleWeightChange = (key: keyof XAIWeights, val: number) => {
    const updated = { ...weights, [key]: val };
    setWeights(updated);
    localStorage.setItem('xai_weights', JSON.stringify(updated));
  };

  const resetWeights = () => {
    const defaults = {
      gpa: 25,
      backlogs_bonus: 8,
      backlogs_penalty: 12,
      dsa: 20,
      attendance: 10,
      internships: 15,
      github: 20,
      cp: 22
    };
    setWeights(defaults);
    localStorage.setItem('xai_weights', JSON.stringify(defaults));
  };

  if (!data) {
    return (
      <div className="glass-card" style={{ padding: 48, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', minHeight: 400, textAlign: 'center', gap: 16 }}>
        <HelpCircle size={48} style={{ color: 'var(--text-dim)' }} />
        <div style={{ fontWeight: 700, fontSize: '1.2rem' }}>No Forecast Generated Yet</div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', maxWidth: 360 }}>
          Select a student from the sidebar database, adjust parameters in the form, and hit submit to run the predictive multi-agent forecast.
        </p>
      </div>
    );
  }

  const { scores = {}, evaluations = {}, inter_agent_consensus = {}, semantic_profile = {}, forecasting = {} } = data;
  const masterScore = scores.master_score || 0;
  const placementProb = forecasting.placement_probability || 0;
  const isPlaceable = placementProb >= 50;

  // Render a custom radial gauge for Placement Probability
  const renderGauge = (probability: number) => {
    const strokeDashoffset = 377 - (377 * probability) / 100;
    return (
      <div className="gauge-visualizer">
        <svg className="gauge-svg" width="140" height="140" viewBox="0 0 140 140">
          <defs>
            <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="var(--color-primary)" />
              <stop offset="50%" stopColor="var(--color-secondary)" />
              <stop offset="100%" stopColor="var(--color-accent)" />
            </linearGradient>
          </defs>
          <circle className="gauge-bg" cx="70" cy="70" r="60" />
          <circle 
            className="gauge-fill" 
            cx="70" 
            cy="70" 
            r="60" 
            strokeDashoffset={strokeDashoffset} 
          />
        </svg>
        <div className="gauge-center-text">
          <span className="gauge-percent">{probability}%</span>
          <span className="gauge-desc">Probability</span>
        </div>
      </div>
    );
  };

  // Render SVG-based scores bar chart (Resume, GitHub, CP, Master)
  const renderAgentScoresChart = () => {
    const chartScores = [
      { label: 'Resume', val: scores.resume_score || 0, color: 'var(--color-secondary)' },
      { label: 'GitHub', val: scores.github_score || 0, color: 'var(--color-accent)' },
      { label: 'CP', val: scores.cp_score || 0, color: 'var(--color-warning)' },
      { label: 'Master', val: scores.master_score || 0, color: 'var(--color-primary)' }
    ];

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 14, width: '100%', padding: '10px 0' }}>
        {chartScores.map((item) => (
          <div key={item.label} style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: 600 }}>
              <span style={{ color: 'var(--text-muted)' }}>{item.label} Score</span>
              <span>{item.val.toFixed(1)} / 100</span>
            </div>
            <div style={{ height: 8, width: '100%', background: 'rgba(255,255,255,0.03)', borderRadius: 4, overflow: 'hidden' }}>
              <div 
                style={{ 
                  height: '100%', 
                  width: `${item.val}%`, 
                  background: item.color, 
                  borderRadius: 4, 
                  boxShadow: `0 0 10px ${item.color}33`,
                  transition: 'width 1s ease-out' 
                }} 
              />
            </div>
          </div>
        ))}
      </div>
    );
  };

  // Render sub-scores breakdowns
  const renderSubScoresGrid = () => {
    const resumeSub = evaluations.resume_agent?.sub_scores || {};
    const githubSub = evaluations.github_agent?.sub_scores || {};
    
    return (
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        {/* Resume subscore items */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <h4 style={{ fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-dim)', letterSpacing: '0.05em', borderBottom: '1px solid var(--border-color)', paddingBottom: 6 }}>Resume Breakdown</h4>
          {Object.entries(resumeSub).map(([key, val]) => (
            <div key={key} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
              <span style={{ color: 'var(--text-muted)' }}>{key.replace('S_', '')}</span>
              <span style={{ fontWeight: 600 }}>{Number(val).toFixed(0)}%</span>
            </div>
          ))}
        </div>
        
        {/* GitHub subscore items */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <h4 style={{ fontSize: '0.8rem', textTransform: 'uppercase', color: 'var(--text-dim)', letterSpacing: '0.05em', borderBottom: '1px solid var(--border-color)', paddingBottom: 6 }}>GitHub Breakdown</h4>
          {Object.entries(githubSub).map(([key, val]) => (
            <div key={key} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
              <span style={{ color: 'var(--text-muted)' }}>{key}</span>
              <span style={{ fontWeight: 600 }}>{Number(val).toFixed(0)}%</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="glass-card" style={{ padding: 24, display: 'flex', flexDirection: 'column' }}>
      {/* Dynamic Tab Selector */}
      <div className="tabs-header">
        <button className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>
          <Award size={16} />
          Overview
        </button>
        <button className={`tab-button ${activeTab === 'debate' ? 'active' : ''}`} onClick={() => setActiveTab('debate')}>
          <MessageSquare size={16} />
          Brainstorm Chat
        </button>
        <button className={`tab-button ${activeTab === 'plots' ? 'active' : ''}`} onClick={() => setActiveTab('plots')}>
          <BarChart3 size={16} />
          Metrics & Plots
        </button>
        <button className={`tab-button ${activeTab === 'ontology' ? 'active' : ''}`} onClick={() => setActiveTab('ontology')}>
          <Briefcase size={16} />
          Ontology & Gap Analysis
        </button>
        <button className={`tab-button ${activeTab === 'xai' ? 'active' : ''}`} onClick={() => setActiveTab('xai')}>
          <Zap size={16} style={{ color: activeTab === 'xai' ? 'var(--color-primary)' : '' }} />
          Explainable AI (XAI)
        </button>
        <button className={`tab-button ${activeTab === 'debug' ? 'active' : ''}`} onClick={() => setActiveTab('debug')}>
          <Sliders size={16} style={{ color: activeTab === 'debug' ? 'var(--color-danger)' : '' }} />
          Debug Details
        </button>
      </div>

      {/* TAB CONTENT: OVERVIEW */}
      {activeTab === 'overview' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--border-color)', paddingBottom: 16 }}>
            <div>
              <h2 style={{ fontSize: '1.6rem', fontWeight: 800, margin: 0, color: 'var(--text-main)' }}>{data.name || 'Unknown Student'}</h2>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-dim)', marginTop: 4 }}>Roll No: {data.student_id || 'N/A'}</div>
            </div>
          </div>

          <div className="prediction-banner">
            <div>
              <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-dim)', letterSpacing: '0.05em', marginBottom: 4, fontWeight: 700 }}>
                Placement Classification
              </div>
              <h3 style={{ fontSize: '1.4rem', fontWeight: 800, marginBottom: 8 }}>
                {isPlaceable ? 'Placeable Student' : 'Needs Development'}
              </h3>
              <div className={`prediction-badge ${isPlaceable ? 'badge-placeable' : 'badge-unplaceable'}`}>
                {isPlaceable ? 'Sufficient Readiness' : 'Critical Readiness Gaps'}
              </div>
            </div>
            {renderGauge(placementProb)}
          </div>

          <div className="score-metrics-grid">
            <div className="metric-card">
              <div className="metric-label">Master Rating</div>
              <div className="metric-value" style={{ color: 'var(--color-primary)' }}>{masterScore.toFixed(1)}</div>
              <div style={{ fontSize: '0.65rem', color: 'var(--text-dim)', fontWeight: 700, textTransform: 'uppercase' }}>
                Performance Score
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Data Completeness</div>
              <div className="metric-value" style={{ color: (scores.completeness_score || 100) < 60 ? 'var(--color-warning)' : 'var(--color-success)' }}>
                {scores.completeness_score !== undefined ? `${scores.completeness_score}%` : '100%'}
              </div>
              <div style={{ fontSize: '0.65rem', color: 'var(--text-dim)', fontWeight: 700, textTransform: 'uppercase' }}>
                Confidence: {scores.confidence_level || 'High'}
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Salary Estimate</div>
              <div className="metric-value" style={{ fontSize: '1.2rem', padding: '6px 0' }}>
                {forecasting.expected_salary_band?.min_lpa || 'N/A'}-{forecasting.expected_salary_band?.max_lpa || 'N/A'} LPA
              </div>
              <div style={{ fontSize: '0.65rem', color: 'var(--text-dim)', fontWeight: 700, textTransform: 'uppercase' }}>
                {forecasting.expected_salary_band?.label || 'Unknown Tier'}
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Domain Area</div>
              <div className="metric-value" style={{ fontSize: '1rem', padding: '8px 0', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {forecasting.predicted_domain || semantic_profile.primary_domain || 'Systems'}
              </div>
              <div style={{ fontSize: '0.65rem', color: 'var(--text-dim)', fontWeight: 700, textTransform: 'uppercase' }}>
                Primary Focus
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Market Readiness</div>
              <div className="metric-value" style={{ fontSize: '1.1rem', padding: '6px 0' }}>
                {forecasting.career_readiness || 'Ready'}
              </div>
              <div style={{ fontSize: '0.65rem', color: 'var(--text-dim)', fontWeight: 700, textTransform: 'uppercase' }}>
                Employability Status
              </div>
            </div>
          </div>

          {/* NEW: Input Data Availability Chart */}
          <div className="glass-card" style={{ padding: 20, background: 'rgba(6, 8, 19, 0.2)' }}>
            <h4 style={{ fontSize: '0.9rem', marginBottom: 15, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
              <CheckCircle size={16} style={{ color: 'var(--color-primary)' }} />
              Data Availability Checklist
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
              {[
                { label: 'Resume Uploaded', present: (data.scores?.resume_score ?? 0) > 0 },
                { label: 'GitHub Profile', present: !!(data.inputs?.github_url || data.inputs?.github || data.inputs?.['GitHub Profile URL']) },
                { label: 'CP Profile (LeetCode etc)', present: !!(data.inputs?.leetcode_url || data.inputs?.codeforces_url || data.inputs?.codechef_url || data.inputs?.hackerrank_url) },
                { label: 'GPA / CPI', present: !!data.inputs?.cpi },
                { label: 'Active Backlogs', present: data.inputs?.backlogs !== undefined && data.inputs?.backlogs !== null && data.inputs?.backlogs !== '' },
                { label: 'DSA Marks', present: !!data.inputs?.dsa_marks },
                { label: 'Semester Attendance', present: !!data.inputs?.attendance },
                { label: 'Internships Count', present: data.inputs?.internships_count !== undefined && data.inputs?.internships_count !== null && data.inputs?.internships_count !== '' },
              ].map((item, idx) => (
                <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 12px', background: 'rgba(255,255,255,0.02)', borderRadius: 8, border: '1px solid var(--border-color)' }}>
                  {item.present ? 
                    <CheckCircle size={16} style={{ color: 'var(--color-success)' }} /> : 
                    <div style={{ color: 'var(--color-danger)', fontWeight: 'bold', fontSize: '1rem', lineHeight: 1, padding: '0 2px' }}>✕</div>
                  }
                  <span style={{ fontSize: '0.8rem', color: item.present ? 'var(--text-main)' : 'var(--text-dim)' }}>
                    {item.label}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h4 style={{ fontSize: '0.9rem', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
              <Zap size={16} style={{ color: 'var(--color-primary)' }} />
              Forecaster Evaluation & Reasoning
            </h4>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: 1.5, background: 'rgba(255,255,255,0.01)', padding: 16, borderRadius: 10, border: '1px solid var(--border-color)', margin: 0 }}>
              {forecasting.reasoning || 'No forecast explanation provided.'}
            </p>
          </div>

          <div>
            <h4 style={{ fontSize: '0.9rem', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
              <Briefcase size={16} style={{ color: 'var(--color-success)' }} />
              Salary Package Prediction Details
            </h4>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: 1.5, background: 'rgba(16, 185, 129, 0.04)', padding: 16, borderRadius: 10, border: '1px solid rgba(16, 185, 129, 0.15)', margin: 0 }}>
              {forecasting.salary_reasoning || 'No detailed salary explanation provided.'}
            </p>
          </div>

          {/* NEW: Historical Validation Verification Section */}
          {data.historical_analysis && data.historical_analysis.status === 'success' && (
            <div style={{ 
              background: 'rgba(16, 185, 129, 0.04)', 
              border: '1.5px solid rgba(16, 185, 129, 0.25)', 
              borderRadius: 12, 
              padding: 18, 
              display: 'flex', 
              flexDirection: 'column', 
              gap: 12 
            }}>
              <h4 style={{ 
                fontSize: '0.9rem', 
                fontWeight: 700, 
                color: 'var(--color-success)', 
                display: 'flex', 
                alignItems: 'center', 
                gap: 8, 
                margin: 0 
              }}>
                <CheckCircle size={16} />
                GLA Historical Validation (Verifiable Proof)
              </h4>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: 1.5, margin: 0 }}>
                {data.historical_analysis.explanation}
              </p>
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(3, 1fr)', 
                gap: 12, 
                marginTop: 4, 
                textAlign: 'center' 
              }}>
                <div style={{ background: 'rgba(255,255,255,0.02)', padding: '10px 6px', borderRadius: 8, border: '1px solid var(--border-color)' }}>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700 }}>Matches Found</div>
                  <div style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-main)', marginTop: 4 }}>{data.historical_analysis.matched_students_count}</div>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.02)', padding: '10px 6px', borderRadius: 8, border: '1px solid var(--border-color)' }}>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700 }}>Observed Rate</div>
                  <div style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--color-success)', marginTop: 4 }}>{data.historical_analysis.historical_placement_rate}%</div>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.02)', padding: '10px 6px', borderRadius: 8, border: '1px solid var(--border-color)' }}>
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700 }}>Avg Package</div>
                  <div style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--color-accent)', marginTop: 4 }}>{data.historical_analysis.average_salary_lpa} LPA</div>
                </div>
              </div>
            </div>
          )}

          {forecasting.key_differentiators && forecasting.key_differentiators.length > 0 && (
            <div>
              <h4 style={{ fontSize: '0.9rem', marginBottom: 8 }}>Key Strengths & Differentiators</h4>
              <div className="points-list">
                {forecasting.key_differentiators.map((point: string, i: number) => (
                  <div key={i} className="points-list-item">
                    <CheckCircle size={14} className="points-list-item-bullet bullet-strength" />
                    <span>{point}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB CONTENT: BRAINSTORM CHAT */}
      {activeTab === 'debate' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: 4 }}>Inter-Agent Debate Transcript</h3>
            <p style={{ color: 'var(--text-dim)', fontSize: '0.8rem', marginBottom: 12 }}>
              Transcript of dialogue where GitHub, Resume, and Competitive Programming (CP) agents debating listed skills against actual evidence to reach domain validation consensus.
            </p>
          </div>
          
          <div className="chat-transcript-container">
            {inter_agent_consensus.inter_agent_brainstorm_transcript?.map((chat: any, i: number) => {
              const nameLower = String(chat.agent).toLowerCase();
              let agentClass = 'github';
              if (nameLower.includes('resume')) agentClass = 'resume';
              if (nameLower.includes('cp') || nameLower.includes('programming')) agentClass = 'cp';

              return (
                <div key={i} className={`chat-bubble ${agentClass}`}>
                  <div className="chat-bubble-sender">
                    <Star size={10} fill="currentColor" />
                    {chat.agent}
                  </div>
                  <div className="chat-bubble-text">{chat.message}</div>
                </div>
              );
            })}
          </div>

          <div style={{ padding: 14, background: 'rgba(99, 102, 241, 0.04)', border: '1px solid rgba(99, 102, 241, 0.15)', borderRadius: 10, fontSize: '0.8rem', lineHeight: 1.45 }}>
            <span style={{ fontWeight: 700, color: 'var(--color-primary)' }}>Consensus Verdict: </span>
            {inter_agent_consensus.validation_reasoning || 'Consensus reasoning not recorded.'}
          </div>
        </div>
      )}

      {/* TAB CONTENT: PERFORMANCE PLOTS */}
      {activeTab === 'plots' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: 4 }}>Quantitative Performance Breakdown</h3>
            <p style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>
              Visualization of core agent scores, alignment, and sub-score components.
            </p>
          </div>

          <div className="glass-card" style={{ padding: 20, background: 'rgba(6, 8, 19, 0.2)' }}>
            <h4 style={{ fontSize: '0.85rem', marginBottom: 15, fontWeight: 700 }}>Overall Evaluation Matrix</h4>
            {renderAgentScoresChart()}
          </div>

          <div className="glass-card" style={{ padding: 20, background: 'rgba(6, 8, 19, 0.2)' }}>
            <h4 style={{ fontSize: '0.85rem', marginBottom: 15, fontWeight: 700 }}>Fine-Grained Agent Metrics</h4>
            {renderSubScoresGrid()}
          </div>
          
          {evaluations.cp_agent?.sub_scores && (
            <div className="glass-card" style={{ padding: 20, background: 'rgba(6, 8, 19, 0.2)' }}>
              <h4 style={{ fontSize: '0.85rem', marginBottom: 15, fontWeight: 700 }}>Coding Platforms Evaluation</h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12 }}>
                {Object.entries(evaluations.cp_agent.sub_scores).map(([pName, pData]: [string, any]) => (
                  <div key={pName} style={{ padding: 12, background: 'rgba(13, 17, 39, 0.4)', borderRadius: 8, border: '1px solid var(--border-color)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                      <span style={{ textTransform: 'capitalize', fontWeight: 700, fontSize: '0.8rem' }}>{pName}</span>
                      <span style={{ fontSize: '0.7rem', color: 'var(--color-primary)', background: 'rgba(99, 102, 241, 0.1)', padding: '2px 6px', borderRadius: 10 }}>
                        {pData.persona || 'Developer'}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                      Solved: {pData.solved_count || 0}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                      Aptitude: {pData.total ? pData.total.toFixed(0) : 0}% Clout
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB CONTENT: ONTOLOGY & GAP ANALYSIS */}
      {activeTab === 'ontology' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
            <div>
              <h4 style={{ fontSize: '0.85rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 10 }}>
                Domain Classification (Ontology)
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)' }}>
                  Validated Primary Domain: <span style={{ color: 'var(--color-accent)' }}>{inter_agent_consensus.validated_primary_domain || 'General Software Engineering'}</span>
                </div>
                <div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 6 }}>Domain Confidence Match:</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div style={{ height: 6, flexGrow: 1, background: 'rgba(255, 255, 255, 0.05)', borderRadius: 3, overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${inter_agent_consensus.domain_validation_score || 80}%`, background: 'var(--color-accent)', borderRadius: 3 }} />
                    </div>
                    <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>{inter_agent_consensus.domain_validation_score || 80}%</span>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <h4 style={{ fontSize: '0.85rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 10 }}>
                Recommended Industry Roles
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {forecasting.recommended_roles?.map((role: string, i: number) => (
                  <div key={i} style={{ padding: '8px 12px', background: 'rgba(99, 102, 241, 0.05)', border: '1px solid var(--border-color)', borderRadius: 8, fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-main)' }}>
                    {role}
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: 16 }}>
            <h4 style={{ fontSize: '0.85rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 10 }}>
              Verified Skills Cross-Check
            </h4>
            <div className="skills-flex-wrap">
              {inter_agent_consensus.verified_skills?.map((item: any, i: number) => (
                <div key={i} className="skill-badge skill-badge-verified">
                  <CheckCircle size={10} />
                  {item.skill} ({item.evidence_source})
                </div>
              ))}
              {inter_agent_consensus.unverified_resume_claims?.map((claim: string, i: number) => (
                <div key={i} className="skill-badge skill-badge-unverified">
                  <AlertOctagon size={10} />
                  Unverified: {claim}
                </div>
              ))}
              {inter_agent_consensus.verified_skills?.length === 0 && (
                <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', fontStyle: 'italic' }}>
                  No parsed verified skills found.
                </div>
              )}
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, borderTop: '1px solid var(--border-color)', paddingTop: 16 }}>
            <div>
              <h4 style={{ fontSize: '0.85rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 6 }}>
                <AlertTriangle size={14} style={{ color: 'var(--color-danger)' }} />
                Identified Gaps & Risk Factors
              </h4>
              <div className="points-list">
                {forecasting.risk_factors?.map((risk: string, i: number) => (
                  <div key={i} className="points-list-item">
                    <AlertOctagon size={14} className="points-list-item-bullet bullet-gap" />
                    <span>{risk}</span>
                  </div>
                ))}
                {forecasting.risk_factors?.length === 0 && (
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', fontStyle: 'italic' }}>No placement risk factors logged.</div>
                )}
              </div>
            </div>

            <div>
              <h4 style={{ fontSize: '0.85rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 10, display: 'flex', alignItems: 'center', gap: 6 }}>
                <Zap size={14} style={{ color: 'var(--color-warning)' }} />
                Actionable Recommendations
              </h4>
              <div className="points-list">
                {forecasting.improvement_areas?.map((item: string, i: number) => (
                  <div key={i} className="points-list-item">
                    <CheckCircle size={14} className="points-list-item-bullet bullet-diff" style={{ color: 'var(--color-warning)' }} />
                    <span>{item}</span>
                  </div>
                ))}
                {forecasting.improvement_areas?.length === 0 && (
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', fontStyle: 'italic' }}>No recommendations loaded.</div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB CONTENT: EXPLAINABLE AI (XAI) */}
      {activeTab === 'xai' && (() => {
        // Build raw inputs fallback
        const rawInputs = data.inputs || {
          cpi: data.raw_data?.gpa || data.raw_data?.["Current CPI"] || data.raw_data?.CPI || 7.5,
          backlogs: data.raw_data?.backlogs || data.raw_data?.["Backlogs Count"] || 0,
          dsa_marks: data.raw_data?.dsa_marks || data.raw_data?.["DSA marks (in Btech)"] || 70,
          attendance: data.raw_data?.attendance || data.raw_data?.["What is your attendance in your current semester?"] || 85,
          internships_count: data.raw_data?.internships_count || data.raw_data?.["Number of internships completed"] || 0,
          github_url: data.raw_data?.github || data.raw_data?.["GitHub Profile URL"] || '',
          leetcode_url: data.raw_data?.leetcode || data.raw_data?.["Leetcode"] || ''
        };

        const drivers = calculateXAI(rawInputs, scores, weights);

        // Sort drivers to find top catalyst and top risk
        const sortedDrivers = [...drivers].sort((a, b) => b.impact - a.impact);
        const topCatalyst = sortedDrivers[0];
        const topRisk = sortedDrivers[sortedDrivers.length - 1];

        const maxImpact = Math.max(...drivers.map(d => Math.abs(d.impact)), 1);

        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: 4 }}>Explainable AI (XAI) - Parameter Attribution</h3>
              <p style={{ color: 'var(--text-dim)', fontSize: '0.8rem', margin: 0 }}>
                This dashboard explains the prediction weights. View the visual contribution of each parameter below: green bars represent positive catalysts, and red bars represent negative risks.
              </p>
            </div>

            {/* Weight Configuration Panel */}
            <div className="glass-card" style={{ padding: 20, background: 'rgba(99, 102, 241, 0.02)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, borderBottom: '1px solid var(--border-color)', paddingBottom: 12 }}>
                <div>
                  <h4 style={{ fontSize: '0.9rem', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Sliders size={16} style={{ color: 'var(--color-primary)' }} />
                    Configure Dynamic Parameter Weights
                  </h4>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                    Interactively tune model attribution thresholds and scaling factors
                  </span>
                </div>
                <button 
                  onClick={resetWeights} 
                  className="tab-button"
                  style={{ padding: '6px 12px', fontSize: '0.75rem', borderRadius: 8, display: 'flex', alignItems: 'center', gap: 6, width: 'auto', flex: 'none' }}
                >
                  <RefreshCw size={12} /> Reset to Defaults
                </button>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 }}>
                {/* GPA Weight Slider */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.78rem', fontWeight: 700 }}>GPA Weight</span>
                    <span style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--color-primary)' }}>{weights.gpa} pts</span>
                  </div>
                  <input 
                    type="range" 
                    min="0" 
                    max="50" 
                    value={weights.gpa} 
                    onChange={(e) => handleWeightChange('gpa', parseInt(e.target.value))}
                    style={{ width: '100%', height: 4, borderRadius: 2, background: 'rgba(255,255,255,0.1)', accentColor: 'var(--color-primary)', cursor: 'pointer' }}
                  />
                  <span style={{ fontSize: '0.62rem', color: 'var(--text-dim)' }}>Maximum positive catalyst points for high GPA</span>
                </div>

                {/* Backlogs Bonus Slider */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.78rem', fontWeight: 700 }}>No Backlogs Bonus</span>
                    <span style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--color-success)' }}>+{weights.backlogs_bonus} pts</span>
                  </div>
                  <input 
                    type="range" 
                    min="0" 
                    max="20" 
                    value={weights.backlogs_bonus} 
                    onChange={(e) => handleWeightChange('backlogs_bonus', parseInt(e.target.value))}
                    style={{ width: '100%', height: 4, borderRadius: 2, background: 'rgba(255,255,255,0.1)', accentColor: 'var(--color-success)', cursor: 'pointer' }}
                  />
                  <span style={{ fontSize: '0.62rem', color: 'var(--text-dim)' }}>Reward points for having zero backlogs</span>
                </div>

                {/* Backlogs Penalty Slider */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.78rem', fontWeight: 700 }}>Backlog Penalty</span>
                    <span style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--color-danger)' }}>-{weights.backlogs_penalty} pts/each</span>
                  </div>
                  <input 
                    type="range" 
                    min="0" 
                    max="30" 
                    value={weights.backlogs_penalty} 
                    onChange={(e) => handleWeightChange('backlogs_penalty', parseInt(e.target.value))}
                    style={{ width: '100%', height: 4, borderRadius: 2, background: 'rgba(255,255,255,0.1)', accentColor: 'var(--color-danger)', cursor: 'pointer' }}
                  />
                  <span style={{ fontSize: '0.62rem', color: 'var(--text-dim)' }}>Deduction multiplier per active backlog</span>
                </div>

                {/* DSA Marks Slider */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.78rem', fontWeight: 700 }}>DSA Marks Weight</span>
                    <span style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--color-accent)' }}>{weights.dsa} pts</span>
                  </div>
                  <input 
                    type="range" 
                    min="0" 
                    max="40" 
                    value={weights.dsa} 
                    onChange={(e) => handleWeightChange('dsa', parseInt(e.target.value))}
                    style={{ width: '100%', height: 4, borderRadius: 2, background: 'rgba(255,255,255,0.1)', accentColor: 'var(--color-accent)', cursor: 'pointer' }}
                  />
                  <span style={{ fontSize: '0.62rem', color: 'var(--text-dim)' }}>Maximum positive catalyst points for high DSA marks</span>
                </div>

                {/* Attendance Slider */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.78rem', fontWeight: 700 }}>Attendance Weight</span>
                    <span style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--color-warning)' }}>{weights.attendance} pts</span>
                  </div>
                  <input 
                    type="range" 
                    min="0" 
                    max="30" 
                    value={weights.attendance} 
                    onChange={(e) => handleWeightChange('attendance', parseInt(e.target.value))}
                    style={{ width: '100%', height: 4, borderRadius: 2, background: 'rgba(255,255,255,0.1)', accentColor: 'var(--color-warning)', cursor: 'pointer' }}
                  />
                  <span style={{ fontSize: '0.62rem', color: 'var(--text-dim)' }}>Maximum positive catalyst points for attendance</span>
                </div>

                {/* Internships Slider */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.78rem', fontWeight: 700 }}>Internship Weight</span>
                    <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#ec4899' }}>{weights.internships} pts</span>
                  </div>
                  <input 
                    type="range" 
                    min="0" 
                    max="40" 
                    value={weights.internships} 
                    onChange={(e) => handleWeightChange('internships', parseInt(e.target.value))}
                    style={{ width: '100%', height: 4, borderRadius: 2, background: 'rgba(255,255,255,0.1)', accentColor: '#ec4899', cursor: 'pointer' }}
                  />
                  <span style={{ fontSize: '0.62rem', color: 'var(--text-dim)' }}>Maximum reward points for completed internships</span>
                </div>

                {/* GitHub Slider */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.78rem', fontWeight: 700 }}>GitHub Weight</span>
                    <span style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--color-primary)' }}>{weights.github} pts</span>
                  </div>
                  <input 
                    type="range" 
                    min="0" 
                    max="40" 
                    value={weights.github} 
                    onChange={(e) => handleWeightChange('github', parseInt(e.target.value))}
                    style={{ width: '100%', height: 4, borderRadius: 2, background: 'rgba(255,255,255,0.1)', accentColor: 'var(--color-primary)', cursor: 'pointer' }}
                  />
                  <span style={{ fontSize: '0.62rem', color: 'var(--text-dim)' }}>Maximum reward points for active GitHub repositories</span>
                </div>

                {/* CP Clout Slider */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.78rem', fontWeight: 700 }}>CP Clout Weight</span>
                    <span style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--color-secondary)' }}>{weights.cp} pts</span>
                  </div>
                  <input 
                    type="range" 
                    min="0" 
                    max="40" 
                    value={weights.cp} 
                    onChange={(e) => handleWeightChange('cp', parseInt(e.target.value))}
                    style={{ width: '100%', height: 4, borderRadius: 2, background: 'rgba(255,255,255,0.1)', accentColor: 'var(--color-secondary)', cursor: 'pointer' }}
                  />
                  <span style={{ fontSize: '0.62rem', color: 'var(--text-dim)' }}>Maximum reward points for LeetCode/Codeforces rating</span>
                </div>
              </div>
            </div>

            {/* Side-by-side Top Catalyst & Top Risk Summary Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              {/* Positive Catalyst Card */}
              {topCatalyst && topCatalyst.impact > 0 && (
                <div style={{
                  background: 'rgba(16, 185, 129, 0.03)',
                  border: '1px solid rgba(16, 185, 129, 0.2)',
                  borderRadius: 12,
                  padding: 16,
                  display: 'flex',
                  gap: 12,
                  alignItems: 'flex-start'
                }}>
                  <CheckCircle size={20} style={{ color: 'var(--color-success)', flexShrink: 0, marginTop: 2 }} />
                  <div>
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-success)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      Primary Positive Catalyst
                    </div>
                    <div style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginTop: 4 }}>
                      {topCatalyst.name} (+{topCatalyst.impact} pts)
                    </div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 4, lineHeight: 1.4 }}>
                      {topCatalyst.description}
                    </div>
                  </div>
                </div>
              )}

              {/* Negative Risk Card */}
              {topRisk && topRisk.impact < 0 && (
                <div style={{
                  background: 'rgba(239, 68, 68, 0.03)',
                  border: '1px solid rgba(239, 68, 68, 0.2)',
                  borderRadius: 12,
                  padding: 16,
                  display: 'flex',
                  gap: 12,
                  alignItems: 'flex-start'
                }}>
                  <AlertTriangle size={20} style={{ color: 'var(--color-danger)', flexShrink: 0, marginTop: 2 }} />
                  <div>
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-danger)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      Primary Risk Factor
                    </div>
                    <div style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-main)', marginTop: 4 }}>
                      {topRisk.name} ({topRisk.impact} pts)
                    </div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 4, lineHeight: 1.4 }}>
                      {topRisk.description}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Custom Bidirectional SHAP/Attribution Bar Chart */}
            <div className="glass-card" style={{ padding: 24, background: 'rgba(6, 8, 19, 0.2)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                <h4 style={{ fontSize: '0.85rem', fontWeight: 700, margin: 0 }}>Parameter Contribution Waterfall</h4>
                <div style={{ display: 'flex', gap: 12, fontSize: '0.7rem', color: 'var(--text-dim)' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <span style={{ width: 8, height: 8, borderRadius: 2, background: 'var(--color-danger)' }} /> Negative Impact
                  </span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <span style={{ width: 8, height: 8, borderRadius: 2, background: 'var(--color-success)' }} /> Positive Impact
                  </span>
                </div>
              </div>

              {/* SHAP Chart Rows */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                {drivers.map((d, idx) => {
                  const isPos = d.impact >= 0;
                  const widthPercent = Math.min(100, (Math.abs(d.impact) / maxImpact) * 100);
                  
                  return (
                    <div key={idx} style={{ display: 'grid', gridTemplateColumns: '160px 1fr 70px', alignItems: 'center', gap: 16 }}>
                      {/* Name & value */}
                      <div>
                        <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-main)' }}>{d.name}</div>
                        <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', marginTop: 1 }}>
                          Actual: <strong style={{ color: 'var(--text-muted)' }}>{d.value}</strong>
                        </div>
                      </div>

                      {/* Zero-centered bar */}
                      <div style={{ position: 'relative', height: 12, background: 'rgba(255,255,255,0.01)', border: '1px solid rgba(255,255,255,0.03)', borderRadius: 6, overflow: 'hidden', display: 'flex' }}>
                        <div style={{ position: 'absolute', left: '50%', top: 0, bottom: 0, width: 1, background: 'rgba(255,255,255,0.08)', zIndex: 1 }} />
                        
                        {isPos ? (
                          <>
                            <div style={{ width: '50%' }} />
                            <div 
                              style={{ 
                                width: `${widthPercent / 2}%`, 
                                background: 'linear-gradient(90deg, var(--color-primary) 0%, var(--color-success) 100%)', 
                                borderRadius: '0 3px 3px 0',
                                boxShadow: '0 0 6px rgba(16, 185, 129, 0.15)'
                              }} 
                            />
                          </>
                        ) : (
                          <>
                            <div style={{ width: `${50 - (widthPercent / 2)}%` }} />
                            <div 
                              style={{ 
                                width: `${widthPercent / 2}%`, 
                                background: 'linear-gradient(90deg, var(--color-danger) 0%, var(--color-secondary) 100%)', 
                                borderRadius: '3px 0 0 3px',
                                boxShadow: '0 0 6px rgba(239, 68, 68, 0.15)'
                              }} 
                            />
                            <div style={{ width: '50%' }} />
                          </>
                        )}
                      </div>

                      {/* Value label */}
                      <div style={{ textAlign: 'right', fontSize: '0.8rem', fontWeight: 800, color: isPos ? 'var(--color-success)' : 'var(--color-danger)' }}>
                        {isPos ? '+' : ''}{d.impact.toFixed(0)} pts
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Qualitative attribution descriptions */}
            <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: 16 }}>
              <h4 style={{ fontSize: '0.85rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 12 }}>
                Detailed Attribution Logic & Insights
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {drivers.map((d, idx) => (
                  <div key={idx} style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: 10, 
                    fontSize: '0.78rem',
                    padding: '8px 12px',
                    background: 'rgba(255,255,255,0.01)',
                    borderRadius: 8,
                    border: '1px solid var(--border-color)'
                  }}>
                    {d.status === 'positive' && <CheckCircle size={14} style={{ color: 'var(--color-success)' }} />}
                    {d.status === 'negative' && <AlertOctagon size={14} style={{ color: 'var(--color-danger)' }} />}
                    {d.status === 'neutral' && <HelpCircle size={14} style={{ color: 'var(--color-accent)' }} />}
                    
                    <span style={{ fontWeight: 700, minWidth: 140 }}>{d.name}:</span>
                    <span style={{ color: 'var(--text-muted)' }}>{d.description}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
      })()}

      {/* TAB CONTENT: DEBUG DETAILS */}
      {activeTab === 'debug' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: 4 }}>Detailed Score Calculations</h3>
            <p style={{ color: 'var(--text-dim)', fontSize: '0.8rem', marginBottom: 12 }}>
              Debug view showing exactly how the Master Score was calculated for this specific student.
            </p>
          </div>

          <div className="glass-card" style={{ padding: 20, background: 'rgba(6, 8, 19, 0.2)' }}>
            <h4 style={{ fontSize: '0.85rem', marginBottom: 15, fontWeight: 700 }}>Master Score Math</h4>
            
            <div style={{ 
              background: 'rgba(99,102,241,0.06)', 
              border: '1px solid rgba(99,102,241,0.2)', 
              borderRadius: 10, 
              padding: 16,
              fontFamily: '"JetBrains Mono", monospace',
              fontSize: '0.85rem',
              color: 'var(--color-primary)'
            }}>
              <div>// Master Score Formula Calculation</div>
              <br/>
              <div style={{ color: 'var(--text-main)' }}>Numerator = </div>
              <div style={{ paddingLeft: 20 }}>
                ({(scores.resume_score || 0).toFixed(2)} [Resume] × {(scores.weightages?.W_resume ?? 9).toFixed(1)}) +
              </div>
              <div style={{ paddingLeft: 20 }}>
                ({(scores.github_score || 0).toFixed(2)} [GitHub] × {(scores.weightages?.W_github ?? 15).toFixed(1)}) +
              </div>
              <div style={{ paddingLeft: 20 }}>
                ({(scores.cp_score || 0).toFixed(2)} [CP] × {(scores.weightages?.W_cp ?? 3).toFixed(1)}) +
              </div>
              <div style={{ paddingLeft: 20 }}>
                ({(scores.score_breakdown?.cpi?.normalized || 0).toFixed(2)} [CPI] × {(scores.weightages?.W_cpi ?? 20).toFixed(1)}) +
              </div>
              <div style={{ paddingLeft: 20 }}>
                ({(scores.score_breakdown?.dsa_marks?.normalized || 0).toFixed(2)} [DSA] × {(scores.weightages?.W_dsa ?? 18).toFixed(1)}) +
              </div>
              <div style={{ paddingLeft: 20 }}>
                ({(scores.score_breakdown?.english_marks?.normalized || 0).toFixed(2)} [English] × {(scores.weightages?.W_english ?? 17).toFixed(1)}) +
              </div>
              <div style={{ paddingLeft: 20 }}>
                ({(scores.score_breakdown?.internships?.normalized || 0).toFixed(2)} [Internships] × {(scores.weightages?.W_internships ?? 15).toFixed(1)}) +
              </div>
              <div style={{ paddingLeft: 20 }}>
                ({(scores.score_breakdown?.backlogs?.normalized || 0).toFixed(2)} [Backlogs] × {(scores.weightages?.W_backlogs ?? 3).toFixed(1)}) +
              </div>
              <div style={{ paddingLeft: 20 }}>
                ({(scores.score_breakdown?.attendance?.normalized || 0).toFixed(2)} [Attendance] × {(scores.weightages?.W_attendance ?? 0).toFixed(1)})
              </div>
              <br/>
              <div style={{ color: 'var(--text-dim)' }}>
                Total Weight = {(scores.weightages?.total_weight ?? 100).toFixed(1)}
              </div>
              <br/>
              <div style={{ color: 'var(--color-success)', fontWeight: 'bold' }}>
                Master Score = {(masterScore).toFixed(2)} / 100
              </div>
            </div>
          </div>
          
          <div className="glass-card" style={{ padding: 20, background: 'rgba(6, 8, 19, 0.2)' }}>
            <h4 style={{ fontSize: '0.85rem', marginBottom: 15, fontWeight: 700 }}>Raw API Payload (JSON)</h4>
            <div style={{
              background: '#0d1117',
              border: '1px solid #30363d',
              borderRadius: 8,
              padding: 16,
              overflow: 'auto',
              maxHeight: 400,
              fontSize: '0.75rem',
              fontFamily: '"JetBrains Mono", monospace',
              color: '#e6edf3'
            }}>
              <pre style={{ margin: 0 }}>
                {JSON.stringify(data, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
