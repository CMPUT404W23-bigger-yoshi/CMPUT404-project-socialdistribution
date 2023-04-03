import React, { useContext, useEffect, useState } from 'react';
import './CreatePost.css';
import { Button, Col, Form, FormSelect, Row } from 'react-bootstrap';
import remarkGfm from 'remark-gfm';
import ReactMarkdown from 'react-markdown';
import CategoryInput from '../CategoryInput/CategoryInput';
import { generatePostId, sendtoInbox, updatePost } from '../../services/post';
import { AuthorContext } from '../../context/AuthorContext';
import MessageModal from '../MessageModal/MessageModal';
import { FileUploader } from 'react-drag-drop-files';
import { Typeahead } from 'react-bootstrap-typeahead';
import { searchMultipleUsers } from '../../services/author';
import ShareModal from '../ShareModal/ShareModal';

export default function CreatePost(props) {
  const [toggleCreatePost, setToggleCreatePost] = useState(!props.post);
  const [show, setShow] = useState(false);
  const [errorMsg, setError] = useState('Error');
  const [shareShow, setShareShow] = useState(false);
  const [shareError, setShareError] = useState('Error');
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
    unlisted: false,
    sentTo: '',
    author
  });

  const [postImage, setPostImage] = useState({
    type: 'post',
    title: '',
    content: '',
    contentType: 'image/*',
    categories: [],
    visibility: 'PUBLIC',
    unlisted: true
  });
  const [usernames, setUsernames] = useState([]);

  useEffect(() => {
    if (props.post) {
      setPost(props.post);
    }
  }, [props]);

  async function createPost() {
    try {
      const postId = await generatePostId(author, post);
      setError('Post created successfully!');
      setShow(true);
      setPost({
        type: 'post',
        title: '',
        content: '',
        contentType: 'text/plain',
        categories: [],
        visibility: 'PUBLIC',
        unlisted: false
      });
    } catch (err) {
      setError('Error creating post');
      setShow(true);
    }
  }

  async function createPrivatePost() {
    try {
      let postVal = post;
      if (!post.sendTo.id.match(window.location.host)) {
        postVal = (await generatePostId(author, post)).data.post;
      }

      const res = await sendtoInbox(post.sendTo.id, {
        ...postVal,
        published: new Date().toISOString(),
        description: post.content
      });
      setError('Post created successfully!');
      setShow(true);
    } catch (err) {
      setError('Error creating post');
      setShow(true);
    }
  }

  async function editPost() {
    try {
      const res = await updatePost(post.author.id, post.id, post, props.post);
      setError('Post updated successfully!');
      setShow(true);
    } catch (err) {
      setError('Error updating post');
      setShow(true);
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

  const handleImageLinkUpload = (e) => {
    const file = e.target.files[0];
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result;
      generatePostId(author, { ...postImage, content: dataUrl }).then((res) => {
        setShareError(res.data.post.id + '/image');
        setShareShow(true);
      });
    };
    reader.readAsDataURL(file);
  };

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
      <ShareModal
        show={shareShow}
        link={shareError}
        handleClose={() => {
          setShareShow(false);
        }}
      />
      <MessageModal
        title={'Post'}
        show={show}
        error={errorMsg}
        handleClose={() => {
          setShow(false);
          setToggleCreatePost(true);
        }}
      />
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
                    style={{ marginRight: '10px' }}
                    variant="outline-light"
                    onClick={() => {
                      setImage(null); // Clear previous image when switching back to text
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
                      label="Upload or drop an image right here"
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
                    <option value="private">Private</option>
                    <option value="unlisted">Unlisted</option>
                  </FormSelect>
                </Col>
              </Row>
            </div>
            <div className="post-submit">
              {post.visibility === 'PRIVATE' && !post.sendTo && (
                <div className="search-user">
                  <Form className="d-flex search-bar">
                    <Typeahead
                      id="search-bar"
                      labelKey="displayName"
                      onChange={(selected) => {
                        if (selected.length > 0) {
                          // Get the last part of the URL (that is the id)
                          setUsernames([]);
                          const user = selected[0];
                          setPost({
                            ...post,
                            visibility: 'PRIVATE',
                            unlisted: false,
                            sendTo: user
                          });
                        }
                      }}
                      onInputChange={(username) => {
                        if (username.length === 0) {
                          setUsernames([]);
                          return;
                        }
                        searchMultipleUsers(username).then((response) => {
                          setUsernames(response.data.items);
                        });
                      }}
                      options={usernames}
                      placeholder="Search for users..."
                      selected={[]}
                    />
                  </Form>
                </div>
              )}
              {post.visibility === 'PRIVATE' && post.sendTo && (
                <div className="search-user">
                  <h6>
                    <span className="post-submit-recipient">
                      Send to:{' '}
                      <span className="post-submit-recipient-name">
                        {post.sendTo.displayName}
                      </span>
                    </span>
                  </h6>
                </div>
              )}
              {post.contentType === 'text/markdown' && !post.image && (
                <div className="upload-image">
                  {/* Button that uploads an empty image to the server */}
                  <Form.Group
                    className="post-content-image-upload"
                    style={{ width: '100%', margin: '20px 0' }}
                  >
                    <Form.Control
                      type="file"
                      onChange={handleImageLinkUpload}
                      accept="image/*"
                      placeholder="Upload Image"
                    />
                  </Form.Group>
                </div>
              )}
              <Button
                variant="danger"
                onClick={() => {
                  setImage(); // Clear image when cancelling
                  setPost({
                    type: 'post',
                    title: '',
                    content: '',
                    contentType: 'text/plain',
                    categories: [],
                    visibility: 'PUBLIC',
                    unlisted: false,
                    sendTo: null,
                    author
                  });
                }}
              >
                Cancel
              </Button>
              <Button
                variant="success"
                onClick={() => {
                  setImage(); // Clear image when you submit
                  if (post.visibility === 'PRIVATE' && post.sendTo) {
                    createPrivatePost();
                    props.setUpdateFeed(true);
                  } else if (post.visibility === 'PRIVATE' && !post.sendTo) {
                    setError('Please select a recipient');
                  } else if (post.id) {
                    editPost();
                  } else {
                    createPost();
                    props.setUpdateFeed(true);
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
