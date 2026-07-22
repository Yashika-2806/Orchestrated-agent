import React from 'react';
import { Database, Activity, ShieldCheck, TrendingUp, BarChart3, Zap, Layers, FileText, BookOpen, Sliders } from 'lucide-react';

export const TrainingParameters: React.FC = () => {
  return (
    <div className="section-card" style={{ maxWidth: 900, margin: '0 auto', animation: 'fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1)' }}>
      <div style={{ marginBottom: 24, paddingBottom: 16, borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: 12 }}>
        <div style={{ background: 'var(--color-primary-glow)', padding: 10, borderRadius: 12, color: 'var(--color-primary)' }}>
          <Database size={24} />
        </div>
        <div>
          <h2 style={{ fontSize: '1.25rem', marginBottom: 4 }}>Training & Testing Parameters</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: 0 }}>
            Under the hood: How the Orchestrator evaluates profiles and predicts career trajectories using historical benchmarks and real-time inference.
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
        
        {/* Training Time Parameters Section */}
        <div className="agent-box">
          <div className="agent-header">
            <div className="agent-icon-wrapper" style={{ background: 'rgba(99, 102, 241, 0.1)', color: '#6366f1' }}>
              <TrendingUp size={20} />
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: '1rem', color: '#6366f1' }}>"Training Time" (Historical Baselines)</h3>
              <p style={{ margin: '4px 0 0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Static parameters used to ground predictions (from benchmarks.json).
              </p>
            </div>
          </div>
          <div className="agent-content" style={{ display: 'grid', gap: 16 }}>
            <div style={{ background: 'var(--bg-card)', padding: 16, borderRadius: 8, border: '1px solid var(--border-color)' }}>
              <h4 style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.9rem', marginBottom: 8 }}>
                <BarChart3 size={16} style={{ color: '#6366f1' }}/> Placement Probability Curve
              </h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-color)', margin: '0 0 12px 0' }}>Maps Master Scores to historical placement rates:</p>
              <ul style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0, paddingLeft: 20, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 6 }}>
                <li><strong>0-20:</strong> 10% (Critical Gap)</li>
                <li><strong>20-35:</strong> 25% (Below Avg)</li>
                <li><strong>35-50:</strong> 45% (Average)</li>
                <li><strong>50-60:</strong> 60% (Above Avg)</li>
                <li><strong>60-70:</strong> 75% (Good)</li>
                <li><strong>70-80:</strong> 88% (Strong)</li>
                <li><strong>80-90:</strong> 95% (Excellent)</li>
                <li><strong>90-100:</strong> 99% (Exceptional)</li>
              </ul>
            </div>

            <div style={{ background: 'var(--bg-card)', padding: 16, borderRadius: 8, border: '1px solid var(--border-color)' }}>
              <h4 style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.9rem', marginBottom: 8 }}>
                <ShieldCheck size={16} style={{ color: '#6366f1' }}/> Salary Market Anchors (LPA)
              </h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-color)', margin: '0 0 12px 0' }}>Expected salary bands grouped by domain and tier:</p>
              <ul style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0, paddingLeft: 20, display: 'grid', gap: 6 }}>
                <li><strong>Web Development:</strong> 3-5 LPA (Entry), 5-8 LPA (Mid), 14-25 LPA (Premium)</li>
                <li><strong>AI/ML:</strong> 4-6 LPA (Entry), 6-10 LPA (Mid), 18-35 LPA (Premium)</li>
                <li><strong>Systems Engineering:</strong> 3-5 LPA (Entry), 5-8.5 LPA (Mid), 15-30 LPA (Premium)</li>
              </ul>
            </div>

            <div style={{ background: 'var(--bg-card)', padding: 16, borderRadius: 8, border: '1px solid var(--border-color)' }}>
              <h4 style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.9rem', marginBottom: 8 }}>
                <BookOpen size={16} style={{ color: '#6366f1' }}/> Domain Ontology Dictionary
              </h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-color)', margin: '0 0 12px 0' }}>The "brain" mapping over 100+ raw technical skills to 11 overarching industry domains and job titles.</p>
              <ul style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0, paddingLeft: 20, display: 'grid', gap: 6 }}>
                <li><strong>Skill-to-Domain:</strong> Maps 'React', 'Node.js' -&gt; 'Web Development'; 'PyTorch', 'TensorFlow' -&gt; 'AI/ML'.</li>
                <li><strong>Domain-to-Role:</strong> Maps 'DevOps' -&gt; 'Cloud Engineer', 'SRE'.</li>
              </ul>
            </div>

            <div style={{ background: 'var(--bg-card)', padding: 16, borderRadius: 8, border: '1px solid var(--border-color)' }}>
              <h4 style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.9rem', marginBottom: 8 }}>
                <Sliders size={16} style={{ color: '#6366f1' }}/> Master Weighting Configuration
              </h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-color)', margin: '0 0 12px 0' }}>The exact mathematical hyperparameters that dictate how strictly agents grade the students.</p>
              <ul style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0, paddingLeft: 20, display: 'grid', gap: 6 }}>
                <li><strong>GitHub Weights:</strong> Bonuses for stars, forks, and optimal commit/PR target ratios.</li>
                <li><strong>Resume Penalties:</strong> Dynamically scaled by graduation year. Deductions for length (page limits) and broken URLs.</li>
                <li><strong>CP Benchmarks:</strong> Hardcoded targets for LeetCode hard counts, Codeforces rating, and CodeChef stars.</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Inference Time Parameters Section */}
        <div className="agent-box">
          <div className="agent-header">
            <div className="agent-icon-wrapper" style={{ background: 'rgba(16, 185, 129, 0.1)', color: '#10b981' }}>
              <Activity size={20} />
            </div>
            <div>
              <h3 style={{ margin: 0, fontSize: '1rem', color: '#10b981' }}>"Inference Time" (Live Testing)</h3>
              <p style={{ margin: '4px 0 0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Real-time metrics evaluated dynamically by the Orchestrator Agent.
              </p>
            </div>
          </div>
          
          <div className="agent-content" style={{ display: 'grid', gap: 16 }}>
            <div style={{ background: 'var(--bg-card)', padding: 16, borderRadius: 8, border: '1px solid var(--border-color)' }}>
              <h4 style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.9rem', marginBottom: 8 }}>
                <Layers size={16} style={{ color: '#10b981' }}/> Flat Weighted Score Calculation
              </h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-color)', margin: '0 0 12px 0' }}>Evaluates a fixed 100-point distributed weighting across technical and academic pillars:</p>
              <ul style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0, paddingLeft: 20, display: 'grid', gap: 6 }}>
                <li><strong>Academic Pillar:</strong> CPI (20%), DSA (18%), English (17%), Internships (15%), Backlogs (3%)</li>
                <li><strong>Technical Profile:</strong> GitHub (15%), Resume (9%), CP (3%)</li>
                <li><strong>Missing Data:</strong> Missing profiles (e.g. no GitHub) simply contribute 0 points to their respective weighted bucket.</li>
              </ul>
            </div>

            <div style={{ background: 'var(--bg-card)', padding: 16, borderRadius: 8, border: '1px solid var(--border-color)' }}>
              <h4 style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.9rem', marginBottom: 8 }}>
                <Zap size={16} style={{ color: '#ef4444' }}/> Employability Hard Gating
              </h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-color)', margin: '0 0 12px 0' }}>If any pillar fails these thresholds, the student is flagged as HIGH RISK (≤ 25% placement):</p>
              <ul style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0, paddingLeft: 20, display: 'grid', gap: 6 }}>
                <li><strong>Tech Competence Pillar:</strong> Must score {'>'} 35.0 (Derived from CP and GitHub)</li>
                <li><strong>Communication Pillar:</strong> Must score {'>'} 30.0 (Derived from Resume)</li>
                <li><strong>Market Readiness Pillar:</strong> Must score {'>'} 20.0 (Derived from GitHub and Resume)</li>
              </ul>
            </div>

            <div style={{ background: 'var(--bg-card)', padding: 16, borderRadius: 8, border: '1px solid var(--border-color)' }}>
              <h4 style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '0.9rem', marginBottom: 8 }}>
                <FileText size={16} style={{ color: '#f59e0b' }}/> Live Backtesting Validation
              </h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-color)', margin: 0 }}>
                The backend cross-references the student's parameters (GPA, DSA marks, backlogs) against 591 real historical records (merge_cont_update.xlsx) to output a verifiable live placement rate and salary range for matching peers.
              </p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
