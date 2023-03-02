import React from 'react';
import './Home.css';
import Sidebar from '../Sidebar/Sidebar';
import { useLocation } from 'react-router-dom';

function Home() {
  const location = useLocation();

  const renderHeading = () => {
    if (location.pathname === '/') {
      return <h1>Home</h1>;
    } else if (location.pathname === '/profile') {
      return <h1>Profile</h1>;
    } else if (location.pathname === '/private') {
      return <h1>Private Posts</h1>;
    } else if (location.pathname === '/notifications') {
      return <h1>Notifications</h1>;
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