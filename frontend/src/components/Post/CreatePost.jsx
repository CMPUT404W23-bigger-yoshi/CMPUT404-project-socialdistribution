import React, { useEffect, useState } from 'react';
import './CreatePost.css';
import { Button, Col, FormSelect, Row } from 'react-bootstrap';
import remarkGfm from 'remark-gfm';
import ReactMarkdown from 'react-markdown';
import CategoryInput from '../CategoryInput/CategoryInput';
import { generatePostId, updatePost } from '../../services/post';
import { getCurrentUserId } from '../../services/author';

export default function CreatePost(props) {
  const [toggleCreatePost, setToggleCreatePost] = useState(!props.post);
  const [showPreview, setShowPreview] = useState(false);
  const [post, setPost] = useState({
    type: 'post',
    title: '',
    content: '',
    contentType: 'text/plain',
    categories: [],
    visibility: 'PUBLIC',
    unlisted: false
  });
  useEffect(() => {
    if (props.post) {
      setPost(props.post);
    }
  }, [props]);

  async function createPost() {
    try {
      const userId = await getCurrentUserId();
      const postId = await generatePostId(userId.data.id, post);
      console.log(postId);
    } catch (err) {
      console.log(err);
    }
  }

  async function editPost() {
    try {
      const res = await updatePost(post.author.id, post.id, post, props.post);
      console.log(res);
    } catch (err) {
      console.log(err);
    }
  }

  return toggleCreatePost ? (
    <div className="create-post-button">
      <Button
        variant="primary"
        onClick={() => {
          setToggleCreatePost(props.post ? true : !toggleCreatePost);
        }}
      >
        {props.post ? 'Edit Post' : 'Create Post'}
      </Button>
    </div>
  ) : (
    <div className="create-post">
      <div className="create-post-container">
        <div className="create-post-header">
          <h2>{props.post ? 'Edit Post' : 'Create Post'}</h2>
        </div>
        <div className="post-content">
          {/* This will contain: */}
          {/* A bar that displays the content type on the left */}
          {/* The bar will allow user to toggle between text/plain and
            text/markdown using a button on the right */}
          {/* If the content type is text/plain, a textarea will be displayed */}
          {/* If the content type is text/markdown, a textarea will be displayed with a preview on the bottom right */}
          <div className="post-content-type-bar">
            <Row className="post-content-type">
              <Col className="post-content-type-text" md={6} xs={12}>
                {post.contentType === 'text/plain' ? 'Plain Text' : 'Markdown'}
              </Col>
              <Col className="post-content-type-toggle" md={6} xs={12}>
                <Button
                  variant="outline-light"
                  onClick={() =>
                    setPost({
                      ...post,
                      contentType:
                        post.contentType === 'text/plain'
                          ? 'text/markdown'
                          : 'text/plain'
                    })
                  }
                >
                  Switch to{' '}
                  {post.contentType === 'text/plain' ? 'Markdown' : 'Text'}
                </Button>
              </Col>
            </Row>
          </div>
          <div className="post-content-text">
            {post.contentType === 'text/plain' ? (
              <textarea
                placeholder="Write your post here..."
                className="post-content-textarea"
                rows={10}
                onChange={(e) => setPost({ ...post, content: e.target.value })}
                value={post.content}
              />
            ) : (
              <div className="post-content-markdown">
                {showPreview ? (
                  <div className="post-content-markdown-preview">
                    <ReactMarkdown
                      children={post.content}
                      remarkPlugins={[remarkGfm]}
                    />
                  </div>
                ) : (
                  <div className="post-content-markdown-textarea">
                    <textarea
                      placeholder="Write your post here..."
                      className="post-content-textarea"
                      rows={10}
                      onChange={(e) =>
                        setPost({ ...post, content: e.target.value })
                      }
                      value={post.content}
                    />
                  </div>
                )}
                <Button
                  variant="outline-light"
                  onClick={() => setShowPreview(!showPreview)}
                >
                  {showPreview ? 'Hide' : 'Show'} Preview
                </Button>
              </div>
            )}
          </div>
          <div className="post-details">
            <Row className="post-details-bar">
              <Col className="post-details-bar-item" xs={8}>
                <CategoryInput
                  categories={post.categories}
                  setCategories={(categories) =>
                    setPost({ ...post, categories })
                  }
                />
              </Col>
              <Col className="post-details-bar-item" xs={4}>
                <FormSelect
                  className="post-details-bar visibility"
                  aria-label="Default select example"
                  onChange={(e) => {
                    if (e.target.value === 'unlisted') {
                      setPost({
                        ...post,
                        visibility: 'PUBLIC',
                        unlisted: true
                      });
                    } else {
                      setPost({
                        ...post,
                        visibility: e.target.value.toUpperCase(),
                        unlisted: false
                      });
                    }
                  }}
                  value={
                    post.unlisted ? 'unlisted' : post.visibility.toLowerCase()
                  }
                >
                  <option value="public">Public</option>
                  <option value="friends">Friends</option>
                  <option value="unlisted">Unlisted</option>
                </FormSelect>
              </Col>
            </Row>
          </div>
          <div className="post-submit">
            <Button
              variant="danger"
              onClick={() => {
                setToggleCreatePost(props.post ? false : !toggleCreatePost);
                setPost({
                  type: 'post',
                  title: '',
                  content: '',
                  contentType: 'text/plain',
                  categories: [],
                  visibility: 'PUBLIC',
                  unlisted: false
                });
              }}
            >
              Cancel
            </Button>
            <Button
              variant="success"
              onClick={() => {
                if (post.id) {
                  editPost();
                } else {
                  createPost();
                }
              }}
            >
              Submit
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
