import React, { useState } from 'react';
import { Settings2, ChevronDown, ChevronUp } from 'lucide-react';

export interface WeightValues {
  w_cpi: number;
  w_dsa: number;
  w_english: number;
  w_internships: number;
  w_github: number;
  w_resume: number;
  w_cp: number;
  w_backlogs: number;
  w_attendance: number;
}

export const defaultWeights: WeightValues = {
  w_cpi: 20,
  w_dsa: 18,
  w_english: 17,
  w_internships: 15,
  w_github: 15,
  w_resume: 9,
  w_cp: 3,
  w_backlogs: 3,
  w_attendance: 0
};

interface WeightConfigProps {
  weights: WeightValues;
  onChange: (newWeights: WeightValues) => void;
}

export const WeightConfig: React.FC<WeightConfigProps> = ({ weights, onChange }) => {
  const [expanded, setExpanded] = useState(false);

  const handleWeightChange = (key: keyof WeightValues, val: number) => {
    onChange({ ...weights, [key]: val });
  };

  const total = Object.values(weights).reduce((a, b) => a + b, 0);

  return (
    <div style={{
      marginBottom: 20,
      background: 'var(--panel-bg)',
      border: '1px solid var(--border-color)',
      borderRadius: 12,
      overflow: 'hidden'
    }}>
      <div 
        onClick={() => setExpanded(!expanded)}
        style={{
          padding: '16px 20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          cursor: 'pointer',
          background: 'rgba(255,255,255,0.02)'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Settings2 size={18} style={{ color: 'var(--color-primary)' }} />
          <div>
            <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-main)' }}>
              Scoring Weight Configuration
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: 2 }}>
              Adjust formula weights for predictions. Total: {total}
            </div>
          </div>
        </div>
        {expanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
      </div>
      
      {expanded && (
        <div style={{ padding: '20px', borderTop: '1px solid var(--border-color)' }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
            gap: 16
          }}>
            {[
              { id: 'w_cpi', label: 'CPI (GPA)', val: weights.w_cpi },
              { id: 'w_dsa', label: 'DSA Marks', val: weights.w_dsa },
              { id: 'w_english', label: 'English Marks', val: weights.w_english },
              { id: 'w_internships', label: 'Internships', val: weights.w_internships },
              { id: 'w_github', label: 'GitHub', val: weights.w_github },
              { id: 'w_resume', label: 'Resume', val: weights.w_resume },
              { id: 'w_cp', label: 'Competitive Prog', val: weights.w_cp },
              { id: 'w_backlogs', label: 'Backlogs', val: weights.w_backlogs },
              { id: 'w_attendance', label: 'Attendance', val: weights.w_attendance },
            ].map(item => (
              <div key={item.id} style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'flex', justifyContent: 'space-between' }}>
                  <span>{item.label}</span>
                  <span style={{ color: 'var(--text-main)' }}>{item.val}</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="1"
                  value={item.val}
                  onChange={(e) => handleWeightChange(item.id as keyof WeightValues, parseInt(e.target.value))}
                  style={{ width: '100%', accentColor: 'var(--color-primary)' }}
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
