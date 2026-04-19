import './TopBar.css';

function TopBar({ toggleSidebar }) {
  return (
    <header className="topbar">
      <div className="topbar-hamburger" onClick={toggleSidebar}>
        <span></span>
        <span></span>
        <span></span>
      </div>

      <div className="topbar-actions">
        <button className="topbar-icon-btn notification-btn">
          🔔
          <span className="notif-badge">2</span>
        </button>
        <button className="topbar-icon-btn profile-btn">👤</button>
      </div>
    </header>
  );
}

export default TopBar;