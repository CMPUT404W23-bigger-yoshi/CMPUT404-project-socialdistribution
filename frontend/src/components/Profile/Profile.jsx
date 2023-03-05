import React, { useEffect, useState } from 'react';
import './Profile.css';
import { Button, Col, Row } from 'react-bootstrap';
import { Github, Twitter } from 'react-bootstrap-icons';
import ShareModal from '../ShareModal/ShareModal';
import Post from '../Post/Post';
import { useLocation } from 'react-router-dom';
import { getCurrentUserDetails, getCurrentUserId } from '../../services/author';

const Profile = () => {
  // Get url location using useLocation hook
  const location = useLocation();
  const [showShareModal, setShowShareModal] = useState(false);
  const [user, setUser] = useState({
    id: 'https://www.facebook.com/100009000000000',
    host: 'https://www.facebook.com',
    displayName: 'Username',
    url: 'https://www.facebook.com/100009000000000',
    github: 'https://github.com/manpreetkaur',
    twitter: 'https://twitter.com/manpreetkaur',
    profileImage: 'https://i.pinimg.com/originals/f1/0f/f7/f10ff70a7155e5ab666bcdd1b45b726d.jpg'
  });
  const [userFollowStats, setUserFollowStats] = useState({
    following: 56,
    followers: 45,
    friends: 2
  });
  // Fetch user data from backend
  useEffect(() => {
    const fetchUserId = async () => {
      try {
        const userId = await getCurrentUserId();
        const user = await getCurrentUserDetails(userId.data.id);
        console.log(user.data);
        setUser(user.data);
        setUserFollowStats({ ...userFollowStats });
      } catch (err) {
        console.log(err);
      }
    };
    fetchUserId().catch((err) => console.log(err));
  }, []);

  return (
    <div className='profile'>
      <ShareModal
        show={showShareModal}
        handleClose={() => setShowShareModal(false)}
        link={user.id}
      />
      <div className='profile-border'>
        <div className='profile-container'>
          <div className='profile-info'>
            <div className='profile-image'>
              {(user.profileImage ? (
              <img src={user.profileImage} alt='profile' />
              ) : (
              <img src='https://i.pinimg.com/originals/f1/0f/f7/f10ff70a7155e5ab666bcdd1b45b726d.jpg' alt='profile' />
              ))}
            </div>
            <div className='profile-name'>
              <h1>{user.displayName}</h1>
            </div>
            <div className='profile-follow-stats'>
              <Row className='profile-follow-stats-row' xs={3}>
                <Col className='px-4'>
                  <h3>{userFollowStats.following}</h3>
                  <p>Following</p>
                </Col>
                <Col className='px-4'>
                  <h3>{userFollowStats.friends}</h3>
                  <p>Friends</p>
                </Col>
                <Col className='px-4'>
                  <h3>{userFollowStats.followers}</h3>
                  <p>Followers</p>
                </Col>
              </Row>
            </div>
            <div className='profile-links'>
              {user.github && (
                <div
                  className='profile-link github'
                  onClick={() => window.open(user.github, '_blank')}
                >
                  <Github />
                </div>)}
              {user.twitter && (
                <div
                  className='profile-link twitter'
                  onClick={() => window.open(user.twitter, '_blank')}
                >
                  <Twitter />
                </div>
              )}
            </div>
          </div>
          <div className='profile-buttons'>
            <Button className='profile-button follow'>
              {location.pathname === '/profile' ? 'Edit' : 'Follow'}
            </Button>
            <Button
              className='profile-button share'
              onClick={() => setShowShareModal(true)}
            >
              Share
            </Button>
          </div>
        </div>
      </div>
      <div className='profile-post-border'>
        <div className='profile-post-container'>
          <div className='profile-posts'>
            <Post />
            <Post />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
