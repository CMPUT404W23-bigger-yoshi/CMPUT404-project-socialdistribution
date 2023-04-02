import React, { useContext, useEffect, useState } from 'react';
import './Profile.css';
import { Button, Col, Row } from 'react-bootstrap';
import { Github, Twitter } from 'react-bootstrap-icons';
import ShareModal from '../ShareModal/ShareModal';
import Post from '../Post/Post';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  getFollowersCount,
  getUserDetails,
  sendFollowRequest,
  unfollowUser
} from '../../services/author';
import { getPosts } from '../../services/post';
import { AuthorContext } from '../../context/AuthorContext';
import GitHubCalendar from 'react-github-calendar';

const splitAuthorUrl = (authorUrl) => {
  if (authorUrl === undefined) {
    return '';
  } else if (authorUrl.includes('?')) {
    return authorUrl.split('?').pop(-1).split('q=')[1];
  } else {
    return authorUrl;
  }
};

const Profile = ({ authorUrl }) => {
  // Get url location using useLocation hook
  const navigate = useNavigate();
  const location = useLocation();
  const [showShareModal, setShowShareModal] = useState(false);
  const [following, setFollowing] = useState(false);
  const [posts, setPosts] = useState([]);
  const [user, setUser] = useState(null);
  const loggedInAuthor = useContext(AuthorContext).author;
  const [userFollowStats, setUserFollowStats] = useState({
    following: 0,
    followers: 0
  });
  // Fetch user data from backend
  useEffect(() => {
    const fetchUserId = async () => {
      try {
        console.log(authorUrl);
        const user = await getUserDetails(splitAuthorUrl(authorUrl));
        setUser(user.data);

        const followersCount = await getFollowersCount(
          splitAuthorUrl(authorUrl)
        );
        setUserFollowStats({
          followers: followersCount
        });

        const posts = await getPosts(splitAuthorUrl(authorUrl));
        posts.data.items.forEach((post) => {
          if (post.categories === '') {
            post.categories = [];
          }
        });
        setPosts(posts.data);
      } catch (err) {
        console.log(err);
      }
    };
    fetchUserId().catch((err) => console.log(err));
  }, [authorUrl, location]);

  if (user === null) {
    return <></>;
  }

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
              {user.profileImage ? (
                <img src={user.profileImage} alt="profile" />
              ) : (
                <img
                  src="https://i.pinimg.com/originals/f1/0f/f7/f10ff70a7155e5ab666bcdd1b45b726d.jpg"
                  alt="profile"
                />
              )}
            </div>
            <div className="profile-name">
              <h1>{user.displayName}</h1>
            </div>
            <div className="profile-follow-stats">
              <Row className="profile-follow-stats-row" xs={1}>
                <Col className="px-4">
                  <h3>{userFollowStats.followers}</h3>
                  <p>Followers</p>
                </Col>
              </Row>
            </div>
            <div className="profile-links">
              {user.github && (
                <div
                  className="profile-link github"
                  onClick={() => window.open(user.github, '_blank')}
                >
                  <Github />
                </div>
              )}
              {user.twitter && (
                <div
                  className="profile-link twitter"
                  onClick={() => window.open(user.twitter, '_blank')}
                >
                  <Twitter />
                </div>
              )}
            </div>
          </div>
          <div className="profile-buttons">
            <Button
              className="profile-button follow"
              onClick={async () => {
                if (loggedInAuthor.id === user.id) {
                  navigate('/settings');
                } else if (following) {
                  try {
                    const res = unfollowUser(loggedInAuthor.id, user.data.id);
                    console.log(res);
                  } catch (err) {
                    console.log(err);
                  }
                } else {
                  try {
                    const res = sendFollowRequest(loggedInAuthor, user);
                    console.log(res);
                  } catch (err) {
                    console.log(err);
                  }
                }
              }}
            >
              {loggedInAuthor.id === user.id
                ? 'Edit'
                : following
                ? 'Unfollow'
                : 'Follow'}
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
      <div className="profile-post-border">
        <div className="profile-post-container">
          {user.github && (
            <div className="profile-github">
              <GitHubCalendar username={user.github.split('/').pop()} />
            </div>
          )}
          <div className="profile-posts">
            {posts?.items?.length > 0 ? (
              posts.items.map((post) => (
                <Post
                  key={post.id}
                  post={post}
                  setPosts={setPosts}
                  posts={posts}
                  currentUser={loggedInAuthor.id.split('/').pop(-1)}
                />
              ))
            ) : (
              <div className="no-posts">
                <h1>No posts to show</h1>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
