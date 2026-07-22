import React, { useState, useEffect } from 'react';
import { Upload, Link2, GraduationCap, Users, Calendar, Award, ChevronDown, ChevronUp } from 'lucide-react';

interface ParameterFormProps {
  initialValues: Record<string, any>;
  onSubmit: (formData: FormData) => void;
  submitting: boolean;
}

export const ParameterForm: React.FC<ParameterFormProps> = ({ initialValues, onSubmit, submitting }) => {
  const [formFields, setFormFields] = useState<Record<string, any>>({});
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [activeSection, setActiveSection] = useState<string>('profiles');

  // Load initial values from selected student
  useEffect(() => {
    // Normalise keys from different CSV templates
    const normalized: Record<string, any> = {};
    
    // Default fallback templates
    const defaultFields = {
      name: '',
      roll_number: '',
      email: '',
      university: 'GLA University',
      gender: 'Male',
      course: 'B.Tech CSE',
      cpi: '8.0',
      backlogs: '0',
      attendance: '85',
      internships_count: '0',
      internship_company: '',
      internship_type: 'None',
      internship_stipend: '',
      aptitude_appeared: 'No',
      aptitude_percentile: '',
      github_url: '',
      linkedin_url: '',
      leetcode_url: '',
      codeforces_url: '',
      codechef_url: '',
      hackerrank_url: '',
      email_address: '',
      percentage_10th: '',
      board_10th: 'CBSE',
      city: '',
      percentage_12th: '',
      board_12th: 'CBSE',
      english_medium: 'Yes',
      father_occupation: '',
      mother_occupation: '',
      dsa_marks: '',
      english_marks: '',
      internship_secured: 'No',
      placement_status: 'Not Placed',
      placed_role_company: 'Not placed',
      salary_package: ''
    };

    // Merge in initialValues mapping flexibly
    Object.keys(defaultFields).forEach((key) => {
      normalized[key] = defaultFields[key as keyof typeof defaultFields];
    });

    if (initialValues) {
      // String name maps
      normalized.name = initialValues.name || initialValues.Name || '';
      normalized.roll_number = initialValues.roll_number || initialValues["University Roll No."] || initialValues["Roll No."] || '';
      normalized.email = initialValues.email || initialValues.Email || initialValues["Email address"] || '';
      normalized.email_address = initialValues["Email address"] || initialValues.email || '';
      
      normalized.university = initialValues.university || initialValues.University || 'GLA University';
      normalized.gender = initialValues.gender || initialValues.Gender || 'Male';
      normalized.course = initialValues.course || initialValues.Course || 'B.Tech CSE';
      normalized.cpi = initialValues.gpa || initialValues["Current CPI"] || initialValues.CPI || '8.0';
      normalized.backlogs = initialValues.backlogs || initialValues["Backlogs Count"] || '0';
      normalized.attendance = initialValues["What is your attendance in your current semester?"] || '85';
      
      normalized.internships_count = initialValues["Number of internships completed"] || '0';
      normalized.internship_company = initialValues["Company/organisation name (for your most recent internship)"] || '';
      normalized.internship_type = initialValues["Internship Type"] || 'None';
      normalized.internship_stipend = initialValues["Domain and Stipend of Internship (per month)"] || '';
      
      normalized.aptitude_appeared = initialValues["Have you appeared for any standardized aptitude test? (AMCAT, eLitmus, CoCubes, etc.)"] || 'No';
      normalized.aptitude_percentile = initialValues["If yes, what was your overall percentile in the standardized aptitude test?"] || '';
      
      normalized.github_url = initialValues.github || initialValues["GitHub Profile URL"] || '';
      normalized.linkedin_url = initialValues.linkedin || initialValues["LinkedIn Profile URL"] || '';
      normalized.leetcode_url = initialValues.leetcode || initialValues["Leetcode"] || '';
      normalized.codeforces_url = initialValues.codeforces || initialValues["Codeforces"] || '';
      normalized.codechef_url = initialValues.codechef || initialValues["Codechef"] || '';
      normalized.hackerrank_url = initialValues.hackerrank || initialValues["Hackerrank"] || '';

      // DYNAMIC VALUE SCANNING (Bypasses shifted columns in CSV files)
      Object.entries(initialValues).forEach(([, v]) => {
        if (typeof v === 'string') {
          const valLower = v.toLowerCase();
          if (valLower.includes('github.com/')) {
            normalized.github_url = v.trim();
          } else if (valLower.includes('linkedin.com/')) {
            normalized.linkedin_url = v.trim();
          } else if (valLower.includes('leetcode.com/')) {
            normalized.leetcode_url = v.trim();
          } else if (valLower.includes('codeforces.com/')) {
            normalized.codeforces_url = v.trim();
          } else if (valLower.includes('codechef.com/')) {
            normalized.codechef_url = v.trim();
          } else if (valLower.includes('hackerrank.com/')) {
            normalized.hackerrank_url = v.trim();
          }
        }
      });
      
      normalized.percentage_10th = initialValues["10th Percentage  Board of education"] || '';
      normalized.city = initialValues.City || initialValues.city || '';
      normalized.percentage_12th = initialValues["12th Percentage  Board of education"] || '';
      normalized.english_medium = initialValues["School was English Medium"] || 'Yes';
      normalized.father_occupation = initialValues["Father Occupation"] || '';
      normalized.mother_occupation = initialValues["Mother Occupation"] || '';
      
      normalized.dsa_marks = initialValues["DS80 m80rks (in 60.Te40h)"] || initialValues["DSA marks (in Btech)"] || '';
      normalized.english_marks = initialValues["English m80rks (in 60.Te40h)"] || initialValues["English marks (in BTech)"] || '';
      normalized.internship_secured = initialValues["internship secured"] || 'No';
      normalized.placement_status = initialValues["Placement status "] || initialValues["Placement status"] || 'Not Placed';
      normalized.placed_role_company = initialValues["If placed,then Describe your role and company name otherwise write Not placed."] || 'Not placed';
      normalized.salary_package = initialValues["If placed,Write your salary package?"] || '';
    }

    setFormFields(normalized);
    setResumeFile(null); // Reset file selection on student change
  }, [initialValues]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormFields((prev) => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setResumeFile(e.target.files[0]);
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const data = new FormData();
    Object.entries(formFields).forEach(([key, value]) => {
      data.append(key, String(value || ''));
    });
    if (resumeFile) {
      data.append('resume', resumeFile);
    }
    onSubmit(data);
  };

  const toggleSection = (section: string) => {
    setActiveSection(activeSection === section ? '' : section);
  };

  return (
    <form className="glass-card" style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 20 }} onSubmit={handleFormSubmit}>
      <h2 className="form-panel-title">
        <GraduationCap size={20} className="file-upload-icon" />
        Prediction Sandbox Form
      </h2>

      {/* SECTION 1: PROFILES & RESUME (Mandatory Inputs) */}
      <div style={{ display: 'flex', flexDirection: 'column', border: '1px solid var(--border-color)', borderRadius: 12, overflow: 'hidden' }}>
        <div 
          onClick={() => toggleSection('profiles')}
          style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 18px', background: 'rgba(99, 102, 241, 0.05)', cursor: 'pointer' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-main)' }}>
            <Link2 size={18} style={{ color: 'var(--color-primary)' }} />
            Developer Handles & Resume (Required)
          </div>
          {activeSection === 'profiles' ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
        
        {activeSection === 'profiles' && (
          <div style={{ padding: 18, display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">Student Name</label>
                <input type="text" name="name" className="form-input" value={formFields.name || ''} onChange={handleInputChange} required />
              </div>
              <div className="form-group">
                <label className="form-label">University Roll No</label>
                <input type="text" name="roll_number" className="form-input" value={formFields.roll_number || ''} onChange={handleInputChange} required />
              </div>
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">GitHub URL / Username</label>
                <input type="text" name="github_url" className="form-input" placeholder="github.com/username" value={formFields.github_url || ''} onChange={handleInputChange} />
              </div>
              <div className="form-group">
                <label className="form-label">LeetCode URL / Username</label>
                <input type="text" name="leetcode_url" className="form-input" placeholder="leetcode.com/u/username" value={formFields.leetcode_url || ''} onChange={handleInputChange} />
              </div>
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">LinkedIn Profile URL</label>
                <input type="text" name="linkedin_url" className="form-input" value={formFields.linkedin_url || ''} onChange={handleInputChange} />
              </div>
              <div className="form-group">
                <label className="form-label">Codeforces Username</label>
                <input type="text" name="codeforces_url" className="form-input" value={formFields.codeforces_url || ''} onChange={handleInputChange} />
              </div>
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">CodeChef Username</label>
                <input type="text" name="codechef_url" className="form-input" value={formFields.codechef_url || ''} onChange={handleInputChange} />
              </div>
              <div className="form-group">
                <label className="form-label">HackerRank Username</label>
                <input type="text" name="hackerrank_url" className="form-input" value={formFields.hackerrank_url || ''} onChange={handleInputChange} />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Upload Resume (PDF Only)</label>
              <label className={`file-upload-area ${resumeFile ? 'has-file' : ''}`}>
                <input type="file" accept=".pdf" style={{ display: 'none' }} onChange={handleFileChange} />
                <Upload size={24} className="file-upload-icon" />
                <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>
                  {resumeFile ? resumeFile.name : 'Choose or Drag Resume PDF'}
                </div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>
                  {resumeFile ? `${(resumeFile.size / 1024).toFixed(1)} KB` : 'PDF files only, max 5MB'}
                </div>
              </label>
            </div>
          </div>
        )}
      </div>

      {/* SECTION 2: ACADEMIC & INSTITUTIONAL METRICS */}
      <div style={{ display: 'flex', flexDirection: 'column', border: '1px solid var(--border-color)', borderRadius: 12, overflow: 'hidden' }}>
        <div 
          onClick={() => toggleSection('academics')}
          style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 18px', background: 'rgba(99, 102, 241, 0.05)', cursor: 'pointer' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-main)' }}>
            <Award size={18} style={{ color: 'var(--color-primary)' }} />
            Academic & Performance Metrics
          </div>
          {activeSection === 'academics' ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>

        {activeSection === 'academics' && (
          <div style={{ padding: 18, display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">Current CPI / CGPA</label>
                <input type="number" step="0.01" name="cpi" className="form-input" value={formFields.cpi || ''} onChange={handleInputChange} />
              </div>
              <div className="form-group">
                <label className="form-label">Backlogs Count</label>
                <input type="number" name="backlogs" className="form-input" value={formFields.backlogs || ''} onChange={handleInputChange} />
              </div>
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">DSA Marks (in Btech)</label>
                <input type="number" name="dsa_marks" className="form-input" value={formFields.dsa_marks || ''} onChange={handleInputChange} />
              </div>
              <div className="form-group">
                <label className="form-label">English Marks (in BTech)</label>
                <input type="number" name="english_marks" className="form-input" value={formFields.english_marks || ''} onChange={handleInputChange} />
              </div>
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">Course Program</label>
                <input type="text" name="course" className="form-input" value={formFields.course || ''} onChange={handleInputChange} />
              </div>
              <div className="form-group">
                <label className="form-label">Attendance (%)</label>
                <input type="number" name="attendance" className="form-input" value={formFields.attendance || ''} onChange={handleInputChange} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* SECTION 3: INTERNSHIP & APTITUDE DETAILS */}
      <div style={{ display: 'flex', flexDirection: 'column', border: '1px solid var(--border-color)', borderRadius: 12, overflow: 'hidden' }}>
        <div 
          onClick={() => toggleSection('experience')}
          style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 18px', background: 'rgba(99, 102, 241, 0.05)', cursor: 'pointer' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-main)' }}>
            <Calendar size={18} style={{ color: 'var(--color-primary)' }} />
            Internships & Aptitude Tests
          </div>
          {activeSection === 'experience' ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>

        {activeSection === 'experience' && (
          <div style={{ padding: 18, display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">Internships Completed Count</label>
                <input type="number" name="internships_count" className="form-input" value={formFields.internships_count || ''} onChange={handleInputChange} />
              </div>
              <div className="form-group">
                <label className="form-label">Internship Type</label>
                <select name="internship_type" className="form-select" value={formFields.internship_type || 'None'} onChange={handleInputChange}>
                  <option value="Paid">Paid</option>
                  <option value="Unpaid">Unpaid</option>
                  <option value="None">None</option>
                </select>
              </div>
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">Internship Company Name</label>
                <input type="text" name="internship_company" className="form-input" placeholder="Most recent company name" value={formFields.internship_company || ''} onChange={handleInputChange} />
              </div>
              <div className="form-group">
                <label className="form-label">Internship Domain & Stipend</label>
                <input type="text" name="internship_stipend" className="form-input" placeholder="e.g. Web Development, stipend 15K" value={formFields.internship_stipend || ''} onChange={handleInputChange} />
              </div>
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">Appeared Standardized Aptitude Test</label>
                <select name="aptitude_appeared" className="form-select" value={formFields.aptitude_appeared || 'No'} onChange={handleInputChange}>
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Aptitude Percentile Score</label>
                <input 
                  type="number" 
                  step="0.01" 
                  name="aptitude_percentile" 
                  className="form-input" 
                  placeholder="Percentile (if Yes)" 
                  value={formFields.aptitude_percentile || ''} 
                  onChange={handleInputChange}
                  disabled={formFields.aptitude_appeared === 'No'} 
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* SECTION 4: DEMOGRAPHICS & BACKGROUND */}
      <div style={{ display: 'flex', flexDirection: 'column', border: '1px solid var(--border-color)', borderRadius: 12, overflow: 'hidden' }}>
        <div 
          onClick={() => toggleSection('background')}
          style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 18px', background: 'rgba(99, 102, 241, 0.05)', cursor: 'pointer' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-main)' }}>
            <Users size={18} style={{ color: 'var(--color-primary)' }} />
            Personal & Background Details
          </div>
          {activeSection === 'background' ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>

        {activeSection === 'background' && (
          <div style={{ padding: 18, display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">10th Percentage & Board</label>
                <input type="text" name="percentage_10th" className="form-input" placeholder="e.g. 92% CBSE" value={formFields.percentage_10th || ''} onChange={handleInputChange} />
              </div>
              <div className="form-group">
                <label className="form-label">12th Percentage & Board</label>
                <input type="text" name="percentage_12th" className="form-input" placeholder="e.g. 88% UP Board" value={formFields.percentage_12th || ''} onChange={handleInputChange} />
              </div>
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">English Medium Schooling?</label>
                <select name="english_medium" className="form-select" value={formFields.english_medium || 'Yes'} onChange={handleInputChange}>
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">City</label>
                <input type="text" name="city" className="form-input" value={formFields.city || ''} onChange={handleInputChange} />
              </div>
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">Father's Occupation</label>
                <input type="text" name="father_occupation" className="form-input" value={formFields.father_occupation || ''} onChange={handleInputChange} />
              </div>
              <div className="form-group">
                <label className="form-label">Mother's Occupation</label>
                <input type="text" name="mother_occupation" className="form-input" value={formFields.mother_occupation || ''} onChange={handleInputChange} />
              </div>
            </div>
          </div>
        )}
      </div>

      <button type="submit" className="btn-primary" disabled={submitting}>
        {submitting ? 'Executing AI Evaluation...' : 'Generate Prediction Forecast'}
      </button>
    </form>
  );
};
