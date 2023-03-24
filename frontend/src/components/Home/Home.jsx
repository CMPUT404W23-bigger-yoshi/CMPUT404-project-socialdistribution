import React, { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { getCurrentUserId } from '../../services/author';
import './Home.css';
import Sidebar from '../Sidebar/Sidebar';
import Post from '../Post/Post';
import Profile from '../Profile/Profile';
import Notifications from '../Notifications/Notifications';
import CreatePost from '../Post/CreatePost';
import Settings from '../Settings/Settings';
import Feed from '../Feed/Feed';

function Home() {
  const location = useLocation();
  const navigate = useNavigate();
  const [userId, setUserId] = React.useState(null);
  useEffect(() => {
    // Checks if user is logged in
    const checkLogin = async () => {
      try {
        const response = await getCurrentUserId();
        if (response.status === 200) {
          setUserId(response.data.id);
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
          <Feed userId={userId} isInbox={false} />
        </>
      );
    } else if (location.pathname === '/inbox') {
      return (
        <>
          <CreatePost />
          <Feed userId={userId} isInbox={true} />
        </>
      );
    } else if (location.pathname === '/profile') {
      return <Profile currentUser={userId} />;
    } else if (location.pathname === '/notifications') {
      return <Notifications />;
    } else if (location.pathname === '/settings') {
      return <Settings />;
    } else if (
      location.pathname.split('/')[1] === 'authors' &&
      location.pathname.split('/')[3] === 'posts'
    ) {
      return <Post />;
    } else if (location.pathname.split('/')[1] === 'authors') {
      const authorId = location.pathname.split('/')[2];
      return <Profile currentUser={userId} authorId={authorId} />;
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
