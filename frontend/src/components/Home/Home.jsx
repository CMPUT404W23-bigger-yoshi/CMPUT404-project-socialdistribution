import React, { useEffect } from 'react';
import './Home.css';
import Sidebar from '../Sidebar/Sidebar';
import { useLocation, useNavigate } from 'react-router-dom';
import Post from '../Post/Post';
import Profile from '../Profile/Profile';
import CreatePost from '../Post/CreatePost';
import { getCurrentUserId } from '../../services/author';

function Home() {
  const location = useLocation();
  const navigate = useNavigate();
  useEffect(() => {
    // Checks if user is logged in
    const checkLogin = async () => {
      try {
        const response = await getCurrentUserId();
        if (response.status === 200) {
          console.log('Logged in: ', response.data);
        }
      } catch (error) {
        navigate('/login');
      }
    };
    checkLogin().then((r) => console.log(r));
  }, []);

  const renderHeading = () => {
    if (location.pathname === '/') {
      return (
        <>
          <CreatePost />
          <Post />
        </>
      );
    } else if (location.pathname === '/profile') {
      return <Profile />;
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
