import React from 'react';
import './Home.css';
import Sidebar from '../Sidebar/Sidebar';
import { useLocation } from 'react-router-dom';
import Profile from '../Profile/Profile';
import Notifications from '../Notifications/Notifications';

function Home() {
  const location = useLocation();

  const renderHeading = () => {
    if (location.pathname === '/') {
      return <h1>Home</h1>;
    } else if (location.pathname === '/profile') {
      return <Profile />;
    } else if (location.pathname === '/private') {
      return <h1>Private Posts</h1>;
    } else if (location.pathname === '/notifications') {
      return <Notifications />;
    } else if (location.pathname === '/settings') {
      return <h1>Settings</h1>;
    } else {
      return <h1>404</h1>;
    }
  };

  return (
    <div className="home">
      <Sidebar />
      <div className="home-content">{renderHeading()}</div>
    </div>
  );
}

export default Home;
