import React, { useState } from 'react';
import './Post.css';
import { deletePost } from '../../services/post';
import { Button, Col, Dropdown, Row } from 'react-bootstrap';
import ReactMarkdown from 'react-markdown';
import { ChatLeftTextFill, ShareFill, ThreeDots } from 'react-bootstrap-icons';
import remarkGfm from 'remark-gfm';
import ShareModal from '../ShareModal/ShareModal';
import CreatePostModal from './CreatePostModal';

const Post = (props) => {
  const { post } = props;
  const [showShareModal, setShowShareModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);

  function getIdFromUrl(url) {
    const urlParts = url.split('/');
    return urlParts[urlParts.length - 1];
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
      <div className="post">
        <div className="post-container">
          <Row className="post-header">
            {/* The post header will contain the following: */}
            {/* 1. The author's profile image on the left */}
            {/* 2. The author's display name on the right of the image */}
            {/* 3. The post's visibility right below the display name */}
            {/* 4. The post's published date on the rightmost side of the header */}
            <Col md={6} xs={12}>
              <div className="post-info">
                <img
                  src={post.author.profileImage}
                  className="post-profile-image"
                  alt={post.author.displayName}
                />
                <div className="post-info-author">
                  <div className="post-author-name">
                    {post.author.displayName}{' '}
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
              {post.categories.length > 0 &&
                post.categories.map((category, idx) => (
                  <div key={idx} className="post-category">
                    {category}
                  </div>
                ))}
            </div>
            <div className="post-body">
              {post.contentType === 'text/markdown' ? (
                <ReactMarkdown
                  children={post.content}
                  remarkPlugins={[remarkGfm]}
                />
              ) : (
                post.content
              )}
            </div>
            {post.image && (
              <div className="post-image">
                <img src={post.image} />
              </div>
            )}
          </Row>
          <Row className="post-footer">
            {/* The post footer will contain the following: */}
            {/* 1. The number of comments */}
            {/* 2. A share button */}
            {/* 3. A three dot button that will show a dropdown menu */}
            <Col xs={4} className="post-buttons">
              <div className="post-comments-count">
                <Button variant="dark">
                  <ChatLeftTextFill /> {post.count}{' '}
                  <span className="icon-hint">Comments</span>
                </Button>
              </div>
            </Col>
            <Col xs={4} className="post-buttons">
              <div className="post-share">
                <Button variant="dark" onClick={() => setShowShareModal(true)}>
                  <ShareFill /> <span className="icon-hint">Share</span>
                </Button>
              </div>
            </Col>
            <Col xs={4} className="post-buttons">
              <div className="post-more">
                <Dropdown>
                  <Dropdown.Toggle variant="dark" id="dropdown-basic">
                    <ThreeDots /> <span className="icon-hint">More</span>
                  </Dropdown.Toggle>

                  <Dropdown.Menu>
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
