import React, { useContext, useEffect, useState } from 'react';
import './Post.css';
import {
  deletePost,
  getComments,
  getObjLikes,
  getPost,
  sendLike
} from '../../services/post';
import { Button, Col, Dropdown, Row } from 'react-bootstrap';
import ReactMarkdown from 'react-markdown';
import {
  ChatLeftTextFill,
  HeartFill,
  ShareFill,
  ThreeDots
} from 'react-bootstrap-icons';
import remarkGfm from 'remark-gfm';
import ShareModal from '../ShareModal/ShareModal';
import CreatePostModal from './CreatePostModal';
import { useLocation, useNavigate } from 'react-router-dom';
import CommentsModal from '../Comments/Comments';
import { AuthorContext } from '../../context/AuthorContext';

const Post = (props) => {
  const [post, setPost] = useState(props.post);
  const [postDetails, setPostDetails] = useState({
    postUrl: ''
  });
  // Use context to get user details
  const userDetails = useContext(AuthorContext).author;
  const location = useLocation();
  const navigate = useNavigate();
  const [showShareModal, setShowShareModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showCommentsModal, setShowCommentsModal] = useState(false);
  const [updateLikes, setUpdateLikes] = useState(false);
  const [updateComments, setUpdateComments] = useState(false);
  const [commentsSrc, setCommentsSrc] = useState({});
  const [likes, setLikes] = useState([]);

  function getIdFromUrl(url) {
    const urlParts = url.split('/');
    return urlParts[urlParts.length - 1];
  }

  useEffect(() => {
    if (post) {
      setPostDetails({
        authorId: getIdFromUrl(post.author.id),
        postId: getIdFromUrl(post.id)
      });
    } else if (
      location.pathname.split('/')[1] === 'authors' &&
      location.pathname.split('/')[3] === 'posts'
    ) {
      const authorId = location.pathname.split('/')[2];
      const postId = location.pathname.split('/')[4];
      console.log('Testing');
      try {
        getPost(authorId, postId).then((response) => {
          setPost(response.data);
        });
      } catch (error) {
        console.log(error);
      }
    } else {
      console.log('Post not found');
    }
  }, [location]);

  useEffect(() => {
    const fetchLikes = async () => {
      try {
        const response = await getObjLikes(post.id);
        if (response.status === 200) {
          setLikes(response.data.items);
        }
      } catch (err) {
        console.log(err);
      }
    };
    fetchLikes().then(() => setUpdateLikes(false));
    const fetchComments = async () => {
      try {
        const response = await getComments(post.id);
        if (response.status === 200) {
          setCommentsSrc(response.data);
        }
      } catch (err) {
        console.log(err);
      }
    };
    fetchComments().then(() => setUpdateComments(false));
  }, [updateLikes, updateComments]);

  async function handleLike() {
    try {
      const likeObject = {
        type: 'Like',
        summary: `${userDetails.displayName} liked your post`,
        author: {
          ...userDetails
        },
        object: post.id
      };
      setUpdateLikes(true);
      const res = await sendLike(likeObject);
      console.log(res);
    } catch (err) {
      console.log(err);
    }
  }

  if (!post) {
    return (
      <div>
        <h1>Post not found</h1>
      </div>
    );
  }

  function formatDate(date) {
    const now = new Date();
    const postDate = new Date(date);
    const diff = now - postDate;
    const diffInMinutes = Math.floor(diff / 60000);
    const diffInHours = Math.floor(diffInMinutes / 60);
    const diffInDays = Math.floor(diffInHours / 24);
    const diffInWeeks = Math.floor(diffInDays / 7);
    if (diffInMinutes < 60) {
      return diffInMinutes + ' min';
    } else if (diffInHours < 24) {
      return diffInHours + ' h';
    } else if (diffInDays < 7) {
      return diffInDays + ' d';
    }
    return diffInWeeks + ' w';
  }

  return (
    <>
      <CreatePostModal
        post={post}
        show={showEditModal}
        handleClose={() => setShowEditModal(false)}
      />
      <ShareModal
        show={showShareModal}
        handleClose={() => setShowShareModal(false)}
        link={post.id}
      />
      <CommentsModal
        show={showCommentsModal}
        handleClose={() => setShowCommentsModal(false)}
        comments={commentsSrc}
        postId={post.id}
        updateComments={() => setUpdateComments(true)}
      />
      <div className="post">
        <div className="post-container">
          <Row className="post-header">
            <Col md={6} xs={12}>
              <div className="post-info">
                {props.isRepost && (
                  <div className="post-repost">
                    <span>
                      <img
                        src={
                          post.author.profileImage !== ''
                            ? post.author.profileImage
                            : 'https://i.pinimg.com/originals/f1/0f/f7/f10ff70a7155e5ab666bcdd1b45b726d.jpg'
                        }
                        className="post-profile-image"
                        alt={post.author.displayName || post.author.username}
                        style={{
                          width: '25px',
                          height: '25px',
                          marginRight: '5px'
                        }}
                      />
                    </span>
                    <span className="post-repost-text">
                      Reposted from{' '}
                      {post.author.displayName || post.author.username}
                    </span>
                    {/* Draw a line */}
                    <hr className="post-repost-line" />
                  </div>
                )}
                <img
                  src={
                    post.author.profileImage !== ''
                      ? post.author.profileImage
                      : 'https://i.pinimg.com/originals/f1/0f/f7/f10ff70a7155e5ab666bcdd1b45b726d.jpg'
                  }
                  className="post-profile-image"
                  alt={post.author.displayName || post.author.username}
                  onClick={() => {
                    navigate(`/authors?q=${post.author.id}`);
                  }}
                />
                <div className="post-info-author">
                  <div
                    className="post-author-name"
                    onClick={() => {
                      navigate(`/authors?q=${post.author.id}`);
                    }}
                  >
                    {post.author.displayName || post.author.username}{' '}
                    <span className="post-date">
                      • {formatDate(post.published)}
                    </span>
                  </div>
                  <div className="post-visibility">{post.visibility}</div>
                </div>
              </div>
            </Col>
            <Col md={6} xs={12}>
              <div className="post-published">{formatDate(post.published)}</div>
            </Col>
          </Row>
          <Row className="post-content">
            {/* The post content will contain the following: */}
            {/* 1. The post's title */}
            {/* 2. The post's content */}
            {/* 3. The post's categories */}
            {/* 4. The post's image if any */}
            <div className="post-title">
              <h3>{post.title}</h3>
            </div>
            <div className="post-categories">
              {post?.categories?.length > 0 &&
                post.categories.map((category, idx) => {
                  if (category !== '') {
                    return (
                      <span key={idx} className="post-category">
                        {category}
                      </span>
                    );
                  }
                  return null;
                })}
            </div>
            <div className="post-body">
              {post.contentType === 'text/markdown' ? (
                <ReactMarkdown
                  children={post.content}
                  remarkPlugins={[remarkGfm]}
                />
              ) : post.contentType.startsWith('image/') ? (
                <img
                  src={`${post.id.replace(/[/]$/, '')}/image`}
                  className="post-image"
                  alt=""
                />
              ) : (
                post.content
              )}
            </div>
          </Row>
          <Row className="post-footer">
            {/* The post footer will contain the following: */}
            {/* 1. The number of comments */}
            {/* 2. A share button */}
            {/* 3. A three dot button that will show a dropdown menu */}
            <Col xs={3} className="post-buttons">
              <div className="post-likes-count">
                <Button variant="dark" onClick={handleLike}>
                  <HeartFill
                    fill={
                      likes?.find((like) => like.author.id === userDetails.id)
                        ? '#fb3958'
                        : 'white'
                    }
                  />{' '}
                  {likes?.length}
                </Button>
              </div>
            </Col>
            <Col xs={3} className="post-buttons">
              <div className="post-comments-count">
                <Button
                  variant="dark"
                  onClick={() => setShowCommentsModal(true)}
                >
                  <ChatLeftTextFill />
                  {commentsSrc?.comments ? commentsSrc?.comments?.length : 0}
                </Button>
              </div>
            </Col>
            <Col xs={3} className="post-buttons">
              <div className="post-share">
                <Button variant="dark" onClick={() => setShowShareModal(true)}>
                  <ShareFill /> <span className="icon-hint">Share</span>
                </Button>
              </div>
            </Col>
            <Col xs={3} className="post-buttons">
              <div className="post-more">
                <Dropdown>
                  <Dropdown.Toggle variant="dark" id="dropdown-basic">
                    <ThreeDots /> <span className="icon-hint">More</span>
                  </Dropdown.Toggle>

                  <Dropdown.Menu>
                    {props.currentUser === postDetails.authorId && (
                      <>
                        <Dropdown.Item onClick={() => setShowEditModal(true)}>
                          Edit
                        </Dropdown.Item>
                        <Dropdown.Item
                          onClick={async () => {
                            const confirmDelete = window.confirm(
                              'Are you sure you want to delete this post?'
                            );
                            if (confirmDelete) {
                              try {
                                const res = await deletePost(
                                  getIdFromUrl(post.author.id),
                                  getIdFromUrl(post.id)
                                );
                                console.log(res);
                                window.location.reload();
                              } catch (error) {
                                console.log(error);
                              }
                            }
                          }}
                        >
                          Delete
                        </Dropdown.Item>
                      </>
                    )}
                    <Dropdown.Item href="#/action-3">Source</Dropdown.Item>
                    <Dropdown.Item href="#/action-4">Origin</Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>
              </div>
            </Col>
          </Row>
        </div>
      </div>
    </>
  );
};

export default Post;
