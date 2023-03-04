import React, { useEffect, useState } from 'react';
import './Profile.css';
import { Button, Col, Row } from 'react-bootstrap';
import { Github, Twitter } from 'react-bootstrap-icons';
import ShareModal from '../ShareModal/ShareModal';
import Post from '../Post/Post';
import { useLocation } from 'react-router-dom';

const Profile = () => {
  // Get url location using useLocation hook
  const location = useLocation();
  const [showShareModal, setShowShareModal] = useState(false);
  const [user, setUser] = useState({
    id: 'https://www.facebook.com/100009000000000',
    host: 'https://www.facebook.com',
    displayName: 'Manpreet Kaur',
    url: 'https://www.facebook.com/100009000000000',
    github: 'https://github.com/manpreetkaur',
    twitter: 'https://twitter.com/manpreetkaur',
    profileImage: 'https://i.imgur.com/uyUFvIp.png'
  });
  const [userFollowStats, setUserFollowStats] = useState({
    following: 56,
    followers: 45,
    friends: 2
  });
  useEffect(() => {
    const fetchUser = async () => {
      const res = await fetch('http://localhost:8080/api/user');
      const data = await res.json();
      setUser(data);
    };
    fetchUser().then((r) => console.log(r));
  }, []);
  useEffect(() => {
    const fetchUserFollowStats = async () => {
      const res = await fetch('http://localhost:8080/api/user/follow-stats');
      const data = await res.json();
      setUserFollowStats(data);
    };
    fetchUserFollowStats().then((r) => console.log(r));
  }, []);
  return (
    <div className="profile">
      <ShareModal
        show={showShareModal}
        handleClose={() => setShowShareModal(false)}
        link={user.id}
      />
      <div className="profile-border">
        <div className="profile-container">
          <div className="profile-info">
            <div className="profile-image">
              <img src={user.profileImage} alt="profile" />
            </div>
            <div className="profile-name">
              <h1>{user.displayName}</h1>
            </div>
            <div className="profile-follow-stats">
              <Row className="profile-follow-stats-row" xs={3}>
                <Col className="px-4">
                  <h3>{userFollowStats.following}</h3>
                  <p>Following</p>
                </Col>
                <Col className="px-4">
                  <h3>{userFollowStats.friends}</h3>
                  <p>Friends</p>
                </Col>
                <Col className="px-4">
                  <h3>{userFollowStats.followers}</h3>
                  <p>Followers</p>
                </Col>
              </Row>
            </div>
            <div className="profile-links">
              <div
                className="profile-link github"
                onClick={() => window.open(user.github, '_blank')}
              >
                <Github />
              </div>
              <div
                className="profile-link twitter"
                onClick={() => window.open(user.twitter, '_blank')}
              >
                <Twitter />
              </div>
            </div>
          </div>
          <div className="profile-buttons">
            <Button className="profile-button follow">
              {location.pathname === '/profile' ? 'Edit' : 'Follow'}
            </Button>
            <Button
              className="profile-button share"
              onClick={() => setShowShareModal(true)}
            >
              Share
            </Button>
          </div>
        </div>
      </div>
      <div className=" profile-post-border">
        <div className=" profile-post-container">
          <div className=" profile-posts">
            <Post />
            <Post />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
