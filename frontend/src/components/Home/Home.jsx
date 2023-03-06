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
          console.log('Logged in: ', response.data);
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
          <Feed userId={userId} isPrivate={false} />
        </>
      );
    } else if (location.pathname === '/profile') {
      return <Profile />;
    } else if (location.pathname === '/private') {
      return (
        <>
          <CreatePost />
          <Feed userId={userId} isPrivate={true} />
        </>
      )
    } else if (location.pathname === '/notifications') {
      return <Notifications />;
    } else if (location.pathname === '/settings') {
      return <Settings />;
    } else if (
      location.pathname.split('/').length === 5 &&
      location.pathname.split('/')[1] === 'author' &&
      location.pathname.split('/')[3] === 'posts'
    ) {
      const authorId = location.pathname.split('/')[2];
      const postId = location.pathname.split('/')[4];
      return <Post authorId={authorId} postId={postId} />;
    } else if (
      location.pathname.split('/').length === 3 &&
      location.pathname.split('/')[1] === 'author'
    ) {
      const authorId = location.pathname.split('/')[2];
      return <Profile authorId={authorId} />;
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
