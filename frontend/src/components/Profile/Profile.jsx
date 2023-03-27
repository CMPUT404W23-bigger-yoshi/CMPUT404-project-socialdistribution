import React, { useEffect, useState } from 'react';
import './Profile.css';
import { Button, Col, Row } from 'react-bootstrap';
import { Github, Twitter } from 'react-bootstrap-icons';
import ShareModal from '../ShareModal/ShareModal';
import Post from '../Post/Post';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  checkIfFollowing,
  followUser,
  getCurrentUserDetails,
  getCurrentUserId,
  getFollowersCount,
  getFollowingCount,
  unfollowUser
} from '../../services/author';
import { getPosts } from '../../services/post';

const Profile = (props) => {
  // Get url location using useLocation hook
  const navigate = useNavigate();
  const location = useLocation();
  const [showShareModal, setShowShareModal] = useState(false);
  const [following, setFollowing] = useState(false);
  const [posts, setPosts] = useState([]);
  const [user, setUser] = useState({
    id: 'https://www.facebook.com/100009000000000',
    host: 'https://www.facebook.com',
    displayName: 'Username',
    url: 'https://www.facebook.com/100009000000000',
    github: 'https://github.com/manpreetkaur',
    twitter: 'https://twitter.com/manpreetkaur',
    profileImage:
      'https://i.pinimg.com/originals/f1/0f/f7/f10ff70a7155e5ab666bcdd1b45b726d.jpg'
  });
  const [userFollowStats, setUserFollowStats] = useState({
    following: 0,
    followers: 0
  });
  // Fetch user data from backend
  useEffect(() => {
    const fetchUserId = async () => {
      try {
        let userId;
        if (!props?.authorId) {
          userId = await getCurrentUserId();
        } else {
          userId = { data: { id: props.authorId } };
        }
        const user = await getCurrentUserDetails(userId.data.id);
        const posts = await getPosts(userId.data.id);
        if (props?.authorId) {
          try {
            const check = await checkIfFollowing(
              props.currentUser,
              userId.data.id
            );
            setFollowing(check.data.found);
          } catch (err) {
            setFollowing(false);
          }
        }
        const followersCount = await getFollowersCount(userId.data.id);
        const followingCount = await getFollowingCount(userId.data.id);
        setUserFollowStats({
          followers: followersCount.data.count,
          following: followingCount.data.count
        });
        setUser(user.data);

        // In all posts in posts.data.items array, replace the categories with an empty array if categories == ''
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
  }, [location.pathname, props]);
  const getAuthorIdFromUrl = (url) => {
    const urlParts = url.split('/');
    return urlParts[urlParts.length - 1];
  };

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
              {user.profileImage ? (
                <img src={user.profileImage} alt='profile' />
              ) : (
                <img
                  src='https://i.pinimg.com/originals/f1/0f/f7/f10ff70a7155e5ab666bcdd1b45b726d.jpg'
                  alt='profile'
                />
              )}
            </div>
            <div className='profile-name'>
              <h1>{user.displayName}</h1>
            </div>
            <div className='profile-follow-stats'>
              <Row className='profile-follow-stats-row' xs={2}>
                <Col className='px-4'>
                  <h3>{userFollowStats.followers}</h3>
                  <p>Following</p>
                </Col>
                <Col className='px-4'>
                  <h3>{userFollowStats.following}</h3>
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
                </div>
              )}
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
            <Button
              className='profile-button follow'
              onClick={() => {
                if (props.currentUser === getAuthorIdFromUrl(user.id)) {
                  navigate('/settings');
                } else if (following) {
                  try {
                    const res = unfollowUser(props.currentUser, user.data.id);
                    console.log(res);
                  } catch (err) {
                    console.log(err);
                  }
                } else {
                  try {
                    const res = followUser(props.currentUser, props.authorId);
                    console.log(res);
                  } catch (err) {
                    console.log(err);
                  }
                }
              }}
            >
              {props.currentUser === getAuthorIdFromUrl(user.id)
                ? 'Edit'
                : following
                  ? 'Unfollow'
                  : 'Follow'}
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
            {posts?.items?.length > 0 ? (
              posts.items.map((post) => (
                <Post
                  key={post.id}
                  post={post}
                  setPosts={setPosts}
                  posts={posts}
                  currentUser={props.currentUser}
                />
              ))
            ) : (
              <div className='no-posts'>
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
