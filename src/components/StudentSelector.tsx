import React, { useState, useEffect } from 'react';
import { Search, Database, UserCheck, RefreshCw } from 'lucide-react';

interface Batch {
  id: string;
  label: string;
}

interface Student {
  roll_number: string;
  name: string;
  gpa: number | string;
  github: string;
  leetcode: string;
  row_index: number;
  raw_data: Record<string, any>;
}

interface StudentSelectorProps {
  onSelectStudent: (student: Student, batchId: string) => void;
  selectedRoll: string | null;
  version?: 'v1' | 'v2';
}

export const StudentSelector: React.FC<StudentSelectorProps> = ({ onSelectStudent, selectedRoll, version = 'v1' }) => {
  const [batches, setBatches] = useState<Batch[]>([]);
  const [selectedBatch, setSelectedBatch] = useState<string>('');
  const [students, setStudents] = useState<Student[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [loadingBatches, setLoadingBatches] = useState<boolean>(true);
  const [loadingStudents, setLoadingStudents] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch batches when version changes
  useEffect(() => {
    fetchBatches();
  }, [version]);

  // Fetch students when batch or version changes
  useEffect(() => {
    if (selectedBatch) {
      fetchStudents(selectedBatch);
    }
  }, [selectedBatch, version]);

  const fetchBatches = async () => {
    setLoadingBatches(true);
    setError(null);
    try {
      const res = await fetch(`/api/batches?version=${version}`);
      if (!res.ok) throw new Error('Failed to load batches');
      const data = await res.json();
      setBatches(data);
      if (data.length > 0) {
        // Find Year 6 or default to first
        const y6 = data.find((b: Batch) => b.id === 'year6');
        setSelectedBatch(y6 ? y6.id : data[0].id);
      }
    } catch (err: any) {
      setError(err.message || 'Error connecting to backend API');
    } finally {
      setLoadingBatches(false);
    }
  };

  const fetchStudents = async (batchId: string) => {
    setLoadingStudents(true);
    setStudents([]);
    try {
      const res = await fetch(`/api/students/${batchId}?version=${version}`);
      if (!res.ok) throw new Error('Failed to load students');
      const data = await res.json();
      setStudents(data);
    } catch (err: any) {
      setError(err.message || 'Error fetching student directory');
    } finally {
      setLoadingStudents(false);
    }
  };

  const filteredStudents = students.filter(
    (student) =>
      student.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      String(student.roll_number).includes(searchQuery)
  );

  return (
    <div className="sidebar-panel">
      <div className="sidebar-logo">
        <Database className="file-upload-icon" size={24} />
        <h2>Talent Forecast</h2>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', height: '100%', flexGrow: 1 }}>
        <label className="batch-select-label">Select Dataset Batch</label>
        {loadingBatches ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 0', color: 'var(--text-dim)', fontSize: '0.85rem' }}>
            <RefreshCw size={16} className="spinner-glow" style={{ animation: 'spin 2s linear infinite' }} />
            Loading datasets...
          </div>
        ) : (
          <select
            className="batch-select"
            value={selectedBatch}
            onChange={(e) => setSelectedBatch(e.target.value)}
          >
            {batches.map((b) => (
              <option key={b.id} value={b.id}>
                {b.label}
              </option>
            ))}
          </select>
        )}

        <div className="form-group" style={{ marginBottom: 15 }}>
          <label className="batch-select-label">Search Student</label>
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              placeholder="Search by name or roll..."
              className="student-search-input"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ margin: 0, paddingLeft: 36 }}
            />
            <Search size={16} style={{ position: 'absolute', left: 12, top: 12, color: 'var(--text-dim)' }} />
          </div>
        </div>

        <div className="student-list-container">
          <div className="batch-select-label" style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>Records ({filteredStudents.length})</span>
            {loadingStudents && <RefreshCw size={12} className="spinner-glow" style={{ animation: 'spin 1.5s linear infinite' }} />}
          </div>
          
          {error && (
            <div style={{ padding: 12, fontSize: '0.75rem', color: 'var(--color-danger)', background: 'rgba(239, 68, 68, 0.05)', borderRadius: 8, border: '1px solid rgba(239, 68, 68, 0.15)', marginBottom: 10 }}>
              {error}
              <button 
                onClick={fetchBatches} 
                style={{ background: 'none', border: 'none', color: 'var(--color-primary)', textDecoration: 'underline', cursor: 'pointer', display: 'block', marginTop: 4, fontStyle: 'italic' }}
              >
                Retry Connection
              </button>
            </div>
          )}

          <div className="student-scroll-list">
            {!loadingStudents && filteredStudents.length === 0 && (
              <div style={{ padding: 20, textAlign: 'center', fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                No records found
              </div>
            )}
            {filteredStudents.map((s) => {
              const isActive = selectedRoll === String(s.roll_number);
              return (
                <div
                  key={s.roll_number}
                  className={`student-item ${isActive ? 'active' : ''}`}
                  onClick={() => onSelectStudent(s, selectedBatch)}
                >
                  <div className="student-item-name">{s.name}</div>
                  <div className="student-item-meta">
                    <span>Roll: {s.roll_number}</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                      <UserCheck size={12} style={{ color: s.github ? 'var(--color-success)' : 'var(--text-dim)' }} />
                      CPI: {s.gpa || 'N/A'}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
