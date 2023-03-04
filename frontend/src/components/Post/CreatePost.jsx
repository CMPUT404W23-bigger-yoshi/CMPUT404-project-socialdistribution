import React, { useState } from 'react';
import './CreatePost.css';
import { Button, Col, Row } from 'react-bootstrap';
import remarkGfm from 'remark-gfm';
import ReactMarkdown from 'react-markdown';

export default function CreatePost() {
  const [post, setPost] = useState({
    title: 'Test',
    content: '',
    contentType: 'text/plain',
    categories: [],
    visibility: 'public',
    unlisted: false
  });
  const [showPreview, setShowPreview] = useState(false);
  return (
    <div className="create-post">
      <div className="create-post-container">
        <div className="create-post-header">
          <h2>Create Post</h2>
        </div>
        <div className="create-post-body">
          <div className="post-title">
            <div className="input-group">
              <input
                required=""
                type="text"
                name="text"
                autoComplete="off"
                className="input"
                onChange={(e) => setPost({ ...post, title: e.target.value })}
              />
              <label className="user-label">Post Title</label>
            </div>
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
                  {post.contentType === 'text/plain'
                    ? 'Plain Text'
                    : 'Markdown'}
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
                  className="post-content-textarea"
                  onChange={(e) =>
                    setPost({ ...post, content: e.target.value })
                  }
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
                        className="post-content-textarea"
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
                    Preview
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
