import React, { useContext, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { getCurrentUserId, getUserById } from '../../services/author';
import './Home.css';
import Sidebar from '../Sidebar/Sidebar';
import Post from '../Post/Post';
import Profile from '../Profile/Profile';
import Notifications from '../Notifications/Notifications';
import CreatePost from '../Post/CreatePost';
import Settings from '../Settings/Settings';
import Feed from '../Feed/Feed';
import axios from 'axios';
import { AuthorContext } from '../../context/AuthorContext';

function Home() {
  const location = useLocation();
  const navigate = useNavigate();
  const [userId, setUserId] = React.useState(null);

  const { author, setAuthor } = useContext(AuthorContext);

  const updateAuthorContext = async () => {
    const authorId = (await getCurrentUserId()).data.id;
    const author = (await getUserById(authorId)).data;
    setAuthor(author);
  };

  useEffect(() => {
    // Checks if user is logged in
    const checkLogin = async () => {
      try {
        const response = await getCurrentUserId();
        if (response.status === 200) {
          axios.defaults.headers.common = {
            Authorization: 'Basic ' + response.data.auth_key
          };
          console.log('Logged in: ', response.data);
          setUserId(response.data.id);
        }
      } catch (error) {
        navigate('/login');
      }
    };
    checkLogin().then((r) => console.log(r));
    updateAuthorContext();
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
      return <Profile authorUrl={`${window.location.href}?q=${author.url}`} />;
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
      const authorUrl = window.location.href;
      return <Profile authorUrl={authorUrl} />;
    } else {
      return <h1>404</h1>;
    }
  };

  if (userId === null || !author?.id) {
    return <></>;
  }
  console.log('rendering');
  return (
    <div className="home">
      <Sidebar />
      <div className="home-content">{renderHeading()}</div>
    </div>
  );
}

export default Home;
