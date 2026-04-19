import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../Sidebar/Sidebar';
import TopBar from '../TopBar/TopBar';
import './CandidateProfile.css';

const tabs = ['Overview', 'Resume', 'AI Analysis', 'Notes'];

function CandidateProfile() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('Overview');


  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const toggleSidebar = () => {
    setIsSidebarOpen(prev => !prev);
  };

  return (
    <div className="app-layout">
      <Sidebar isOpen={isSidebarOpen} />

      <div className={`app-content ${isSidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
        <TopBar toggleSidebar={toggleSidebar} />
        <main className="profile-main">
          <div className="profile-breadcrumb">
            <button className="back-btn" onClick={() => navigate('/candidates')}>
              ‹ Back to Candidates
            </button>
            <h2 className="profile-page-title">Candidate Profile</h2>
            <div className="profile-actions">
              <button className="btn-more-stage">More Stage ▾</button>
              <button className="more-btn">⋮</button>
            </div>
          </div>

          <div className="profile-hero">
            <div className="profile-hero-left">
              <div className="profile-big-avatar">AS</div>
              <div className="profile-hero-info">
                <h2 className="profile-name">Amit Sharma</h2>
                <p className="profile-contact">amit.sharma@email.com · +91 98765 43210</p>
                <p className="profile-role-tag">Java Developer</p>
              </div>
            </div>
            <div className="profile-ai-score">
              <p className="ai-score-label">AI Match Score</p>
              <p className="ai-score-value">86<span>/100</span></p>
            </div>
          </div>

          <div className="profile-meta">
            <div className="meta-item">
              <p className="meta-label">Current Stage</p>
              <span className="stage-badge-screened">Screened</span>
            </div>
            <div className="meta-item">
              <p className="meta-label">Applied On</p>
              <p className="meta-value">Apr 01, 2024</p>
            </div>
            <div className="meta-item">
              <p className="meta-label">Location</p>
              <p className="meta-value">Bangalore, India</p>
            </div>
          </div>

          <div className="profile-tabs">
            {tabs.map((tab) => (
              <button
                key={tab}
                className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
                onClick={() => setActiveTab(tab)}
              >
                {tab}
              </button>
            ))}
          </div>

          {activeTab === 'Overview' && (
            <div className="profile-content-grid">
              <div className="profile-section-card">
                <h4>Skills</h4>
                <div className="skills-wrap">
                  {['Java', 'Spring Boot', 'SQL', 'REST APIs', 'Microservices', 'Git', 'Docker'].map((s) => (
                    <span key={s} className="skill-tag">{s}</span>
                  ))}
                </div>
                <h4 className="section-subtitle">Experience Summary</h4>
                <p className="exp-text">
                  3.6 years of experience in Java development, building scalable web applications using Spring Boot and Microservices.
                </p>
              </div>

              <div className="profile-section-card">
                <h4>AI Analysis</h4>
                <ul className="ai-analysis-list">
                  <li>Strong match for required Java and Spring Boot skills</li>
                  <li>Has microservices and Hibernate experience</li>
                  <li>Good hands-on experience with Docker and Git</li>
                </ul>
                <div className="ai-recommendation">
                  <span>⭐</span>
                  <span>Recommendation: Move to Technical Interview</span>
                </div>
              </div>

              <div className="profile-section-card resume-card">
                <h4>Resume Preview</h4>
                <div className="resume-preview">
                  <span className="pdf-icon">📄</span>
                  <p className="resume-name">Amit_Sharma_Resume.pdf</p>
                  <p className="resume-size">245 KB</p>
                  <button className="btn-download">⬇ Download</button>
                </div>
              </div>
            </div>
          )}

          {activeTab !== 'Overview' && (
            <div className="tab-placeholder">
              <p>Content for <strong>{activeTab}</strong> tab coming soon.</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default CandidateProfile;
