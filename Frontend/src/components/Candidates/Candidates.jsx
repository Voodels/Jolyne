import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../Sidebar/Sidebar';
import TopBar from '../TopBar/TopBar';
import './Candidates.css';

const candidates = [
  {
    id: 1,
    initials: 'A',
    name: 'Purni Sharma',
    email: 'avg.e@rblog',
    jobTitle: 'Java Developer',
    stage: 'Applied',
    stageColor: '#e0e7ff',
    stageTextColor: '#4338ca',
    skills: 'Screening, SQL',
    lastActivity: 'Apr 04, 2024',
  },
  {
    id: 2,
    initials: 'P',
    name: 'Aman Patel',
    email: 'amit.alaman@anpr.be',
    jobTitle: 'Frontend Developer',
    stage: 'Shortlisted',
    stageColor: '#fef3c7',
    stageTextColor: '#d97706',
    skills: 'Python, SQL',
    lastActivity: 'Apr 27, 2024',
  },
  {
    id: 3,
    initials: 'R',
    name: 'Rohan Gupta',
    email: 'nsha.gngh@email.com',
    jobTitle: 'Full Stack Developer',
    stage: 'Selected',
    stageColor: '#dcfce7',
    stageTextColor: '#16a34a',
    skills: 'Node.js, Express, React',
    lastActivity: 'Apr 04, 2024',
  },
  {
    id: 4,
    initials: 'S',
    name: 'Sakshi Verma',
    email: 'sneha.vlngt@email.com',
    jobTitle: 'UI/UX Designer',
    stage: 'Shortlisted',
    stageColor: '#fef3c7',
    stageTextColor: '#d97706',
    skills: 'Figma, Adobe XD',
    lastActivity: 'Apr 26, 2024',
  },
  {
    id: 5,
    initials: 'V',
    name: 'Vikram Singh',
    email: 'vikramsingh@email.com',
    jobTitle: 'DevOps Engineer',
    stage: 'Selected',
    stageColor: '#dcfce7',
    stageTextColor: '#16a34a',
    skills: 'AWS, Docker, Python',
    lastActivity: 'Apr 25, 2024',
  },
];

function Candidates() {
  const navigate = useNavigate();

  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const toggleSidebar = () => {
    setIsSidebarOpen(prev => !prev);
  };

  return (
    <div className="app-layout">
      <Sidebar isOpen={isSidebarOpen} />
      <div className={`app-content ${isSidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
        <TopBar toggleSidebar={toggleSidebar} />
        <main className="candidates-main">
          <div className="candidates-header">
            <h2 className="candidates-title">Candidates</h2>
            <div className="candidates-header-right">
              <div className="search-box">
                <span className="search-icon">🔍</span>
                <input type="text" placeholder="Search by name, skills, or email..." />
              </div>
              <button className="btn-add-candidate">+ Add Candidate</button>
            </div>
          </div>

          <div className="candidates-filters">
            <select className="filter-select">
              <option>All Jobs</option>
              <option>Java Developer</option>
              <option>Frontend Developer</option>
            </select>
            <select className="filter-select">
              <option>All Stages</option>
              <option>Applied</option>
              <option>Shortlisted</option>
              <option>Selected</option>
            </select>
            <select className="filter-select">
              <option>Sort: Latest</option>
              <option>Sort: Oldest</option>
              <option>Sort: Name</option>
            </select>
          </div>

          <div className="candidates-table-wrap">
            <table className="candidates-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Job Title</th>
                  <th>Stage</th>
                  <th>Skills</th>
                  <th>Last Activity</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {candidates.map((c) => (
                  <tr
                    key={c.id}
                    className="candidate-row"
                    onClick={() => navigate(`/candidates/${c.id}`)}
                  >
                    <td>
                      <div className="candidate-name-cell">
                        <div className="candidate-avatar">{c.initials}</div>
                        <div>
                          <p className="candidate-name">{c.name}</p>
                          <p className="candidate-email">{c.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="candidate-job">{c.jobTitle}</td>
                    <td>
                      <span
                        className="stage-badge"
                        style={{
                          background: c.stageColor,
                          color: c.stageTextColor,
                        }}
                      >
                        {c.stage}
                      </span>
                    </td>
                    <td className="candidate-skills">{c.skills}</td>
                    <td className="candidate-activity">{c.lastActivity}</td>
                    <td>
                      <button className="more-btn">⋮</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="pagination">
            <button className="page-btn">‹</button>
            {[1, 2, 3, 4, 5].map((n) => (
              <button key={n} className={`page-btn ${n === 1 ? 'active' : ''}`}>{n}</button>
            ))}
            <button className="page-btn">›</button>
          </div>
        </main>
      </div>
    </div>
  );
}

export default Candidates;
