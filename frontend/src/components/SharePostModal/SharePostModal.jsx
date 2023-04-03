import React, { useContext, useEffect, useState } from 'react';
import './SharePostModal.css';
import { AuthorContext } from '../../context/AuthorContext';
import { generatePostId, sendtoInbox } from '../../services/post';
import ShareModal from '../ShareModal/ShareModal';
import MessageModal from '../MessageModal/MessageModal';
import { Button, Col, Form, FormSelect, Row } from 'react-bootstrap';
import { Typeahead } from 'react-bootstrap-typeahead';
import { searchMultipleUsers } from '../../services/author';
import Modal from 'react-bootstrap/Modal';

export default function SharePostModal({ post, showVal, handleClose }) {
  const [show, setShow] = useState(false);
  const [errorMsg, setError] = useState('Error');
  const [shareShow, setShareShow] = useState(false);
  const [shareError, setShareError] = useState('Error');
  const { author } = useContext(AuthorContext);
  const [postDetails, setPostDetails] = useState({});

  useEffect(() => {
    if (post) {
      setPostDetails({
        ...post,
        source: post.id,
        visibility: 'PUBLIC',
        author
      });
    }
  }, [post]);

  async function sendPost() {
    try {
      const postVal = await generatePostId(author, postDetails);
      if (postVal.data.post.unlisted) {
        setShareError(postVal.data.post.id);
        setShareShow(true);
      } else {
        setError('Post created successfully!');
        setShow(true);
      }
      setPostDetails({
        visibility: 'PUBLIC',
        unlisted: false
      });
    } catch (err) {
      setError('Error creating post');
      setShow(true);
    }
  }

  return (
    <Modal show={showVal} onHide={handleClose} backdrop="static">
      <div className="create-post">
        <ShareModal
          show={shareShow}
          link={shareError}
          handleClose={() => {
            setShareShow(false);
            handleClose();
          }}
        />
        <MessageModal
          title={'Post'}
          show={show}
          error={errorMsg}
          handleClose={() => {
            setShow(false);
            handleClose();
          }}
        />
        <div className="create-post-container">
          <div className="create-post-header">
            <h2>Share Post</h2>
          </div>
          <div className="create-post-body">
            <div className="post-details">
              <Row className="post-details-bar">
                <Col className="post-details-bar-item" xs={8}></Col>
                <Col className="post-details-bar-item" xs={4}>
                  <FormSelect
                    className="post-details-bar visibility"
                    aria-label="Default select example"
                    onChange={(e) => {
                      if (e.target.value === 'unlisted') {
                        setPostDetails({
                          ...postDetails,
                          visibility: 'PUBLIC',
                          unlisted: true
                        });
                      } else {
                        setPostDetails({
                          ...postDetails,
                          visibility: e.target.value.toUpperCase(),
                          unlisted: false
                        });
                      }
                    }}
                    value={
                      postDetails.unlisted
                        ? 'unlisted'
                        : postDetails?.visibility?.toLowerCase()
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
                  handleClose();
                }}
              >
                Cancel
              </Button>
              <Button
                variant="success"
                onClick={() => {
                  sendPost().then(() => {});
                }}
              >
                Submit
              </Button>
            </div>
          </div>
        </div>
      </div>
    </Modal>
  );
}
