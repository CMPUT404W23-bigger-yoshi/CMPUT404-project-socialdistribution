import React, { useContext, useEffect, useState } from 'react';
import './CreatePost.css';
import { Button, Col, FormSelect, Row } from 'react-bootstrap';
import remarkGfm from 'remark-gfm';
import ReactMarkdown from 'react-markdown';
import CategoryInput from '../CategoryInput/CategoryInput';
import { generatePostId, updatePost } from '../../services/post';
import { getCurrentUserId } from '../../services/author';
import { AuthorContext } from '../../context/AuthorContext';
import { FileUploader } from 'react-drag-drop-files';

export default function CreatePost(props) {
  const [toggleCreatePost, setToggleCreatePost] = useState(!props.post);
  const [showPreview, setShowPreview] = useState(false);
  const [image, setImage] = useState(null);
  const { author } = useContext(AuthorContext);
  const acceptedMediaTypes = ['JPG', 'PNG', 'GIF'];
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
      console.log(post.contentType);
      const postId = await generatePostId(author, post);
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

  function handleImageUpload(file) {
    if (file) {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      console.log(file.type);
      reader.onload = () => {
        const base64Image = reader.result;
        setImage(base64Image);
        setPost({
          ...post,
          contentType: file.type,
          content: base64Image
        });
      };
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
        <div className="create-post-body">
          <div className="post-title-text">
            <div className="input-group">
              <input
                required={true}
                type="text"
                name="text"
                autoComplete="off"
                className="input"
                onChange={(e) => setPost({ ...post, title: e.target.value })}
                value={post.title}
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
                    : post.contentType === 'text/markdown'
                    ? 'Markdown text'
                    : 'Image'}
                </Col>
                <Col className="post-content-type-toggle" md={6} xs={12}>
                  <Button
                    variant="outline-light"
                    onClick={() => {
                      setImage(); // Clear previous image when switching back to text
                      setPost({
                        ...post,
                        content: post.contentType.startsWith('image')
                          ? null
                          : post.content,
                        contentType:
                          post.contentType === 'text/plain'
                            ? 'text/markdown'
                            : 'text/plain'
                      });
                    }}
                  >
                    Switch to{' '}
                    {post.contentType === 'text/plain' ? 'Markdown' : 'Text'}
                  </Button>
                  <Button
                    variant="outline-light"
                    onClick={() =>
                      setPost({
                        ...post,
                        content: null,
                        contentType: 'image/*'
                      })
                    }
                  >
                    Switch to Image
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
                  onChange={(e) =>
                    setPost({ ...post, content: e.target.value })
                  }
                  value={post.content}
                />
              ) : post.contentType === 'text/markdown' ? (
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
              ) : (
                <div className="post-content-image">
                  {image ? (
                    <img
                      src={post.content}
                      alt="uploaded image"
                      className="post-content-image-preview"
                    />
                  ) : (
                    <FileUploader
                      handleChange={handleImageUpload}
                      name="file"
                      types={acceptedMediaTypes}
                    />
                  )}
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
                  setImage(); // Clear image when cancelling
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
    </div>
  );
}
