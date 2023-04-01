import React from 'react';
import './Comments.css';
import Modal from 'react-bootstrap/Modal';
import { Button, Col, Row } from 'react-bootstrap';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { getUserDetails } from '../../services/author';
import { makeComment } from '../../services/post';

const timeSince = (date) => {
  const seconds = Math.floor((new Date() - date) / 1000);
  let interval = seconds / 31536000;
  if (interval > 1) {
    return Math.floor(interval) + ' years';
  }
  interval = seconds / 2592000;
  if (interval > 1) {
    return Math.floor(interval) + ' months';
  }
  interval = seconds / 86400;
  if (interval > 1) {
    return Math.floor(interval) + ' days';
  }
  interval = seconds / 3600;
  if (interval > 1) {
    return Math.floor(interval) + ' hours';
  }
  interval = seconds / 60;
  if (interval > 1) {
    return Math.floor(interval) + ' minutes';
  }
  return Math.floor(seconds) + ' seconds';
};

function Comment(props) {
  const { author, profileImage, comment, published, contentType } = props;

  return (
    <div className="comment">
      <div className="d-flex">
        <img
          src={profileImage !== '' ? profileImage : 'https://i.pinimg.com/originals/f1/0f/f7/f10ff70a7155e5ab666bcdd1b45b726d.jpg'}
          alt="profile"
          className="rounded-circle"
        />
        <div className=" ml-2">
          <span className="author">{author}</span>
          <span className="time">{timeSince(new Date(published))}</span>
          {contentType === 'text' ? (
            <div className="comment-content">{comment}</div>
          ) : (
            <div className="comment-content">
              <ReactMarkdown children={comment} remarkPlugins={[remarkGfm]} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function Comments(props) {
  const { comments, authorId, postId } = props;
  const [comment, setComment] = React.useState({
    comment: '',
    contentType: 'text/plain'
  });
  const [showPreview, setShowPreview] = React.useState(false);

  return (
    <div className="container mt-5 border-left border-right">
      <div className="d-flex justify-content-center pt-3 pb-2">
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
                {comment.contentType === 'text/plain'
                  ? 'Plain Text'
                  : 'Markdown'}
              </Col>
              <Col className="post-content-type-toggle" md={6} xs={12}>
                <Button
                  variant="outline-light"
                  onClick={() =>
                    setComment({
                      ...comment,
                      contentType:
                        comment.contentType === 'text/plain'
                          ? 'text/markdown'
                          : 'text/plain'
                    })
                  }
                >
                  Switch to{' '}
                  {comment.contentType === 'text/plain' ? 'Markdown' : 'Text'}
                </Button>
              </Col>
            </Row>
          </div>
          <div className="post-content-text">
            {comment.contentType === 'text/plain' ? (
              <textarea
                placeholder="Write your post here..."
                className="post-content-textarea"
                rows={10}
                onChange={(e) =>
                  setComment({ ...comment, comment: e.target.value })
                }
                value={comment.comment}
              />
            ) : (
              <div className="post-content-markdown">
                {showPreview ? (
                  <div className="post-content-markdown-preview">
                    <ReactMarkdown
                      children={comment.comment}
                      remarkPlugins={[remarkGfm]}
                    />
                  </div>
                ) : (
                  <div className="post-content-markdown-textarea">
                    <textarea
                      placeholder="Write your comment here..."
                      className="post-content-textarea"
                      rows={10}
                      onChange={(e) =>
                        setComment({ ...comment, comment: e.target.value })
                      }
                      value={comment.comment}
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
        </div>
      </div>
      <div className="post-actions justify-content-center">
        <Button
          variant="success"
          className="actions-button"
          onClick={async () => {
            try {
              const author = await getUserDetails(authorId);
              const newComment = {
                ...comment,
                type: 'comment',
                published: new Date().toISOString(),
                author: {
                  ...author.data
                },
                id:
                  window.location.origin +
                  `/authors/${authorId}/posts/${postId}/comments/`
              };
              const res = await makeComment(authorId, newComment);
              console.log(res);
            } catch (e) {
              console.log(e);
            }
            setComment({ comment: '', contentType: 'text/plain' });
          }}
        >
          Comment
        </Button>
      </div>
      <div className="comments">
        {comments?.map((comment) => (
          <Comment
            key={comment.id}
            author={comment.author.displayName}
            comment={comment.comment}
            published={comment.published}
            contentType={comment.contentType}
            profileImage={comment.author.profileImage}
          />
        ))}
      </div>
    </div>
  );
}

function CommentsModal(props) {
  const { comments, authorId, postId, show, handleClose } = props;
  return (
    <div className="comments-modal">
      <Modal
        show={show}
        onHide={handleClose}
        size="lg"
        aria-labelledby="contained-modal-title-vcenter"
        centered
      >
        <Modal.Body>
          <Comments
            comments={comments?.comments}
            authorId={authorId}
            postId={postId}
          />
        </Modal.Body>
        <Modal.Footer>
          <Button onClick={handleClose}>Close</Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
}

export default CommentsModal;
