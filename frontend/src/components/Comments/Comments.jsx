import React from 'react';
import { HandThumbsUp } from 'react-bootstrap-icons';
import './Comments.css';
import Modal from 'react-bootstrap/Modal';
import { Button } from 'react-bootstrap';

function Comment(props) {
  return (
    <div className='d-flex justify-content-center py-2'>
      <div className='second py-2 px-2'><span className='text1'>
        {props.comment}
      </span>
        <div className='d-flex justify-conte    nt-between py-1 pt-2'>
          <div><img src='https://i.imgur.com/AgAC1Is.jpg' width='18' alt='pfp' />
            <span className='text2'>
              {props.author}
            </span></div>
          <div><span className='text3'>Like?</span>
            <HandThumbsUp color='#007bff' size={18} className='ml-1' />
            <span className='text4'>
              {props.likes}
            </span></div>
        </div>
      </div>
    </div>
  );
}

function Comments(props) {
  return (
    <div className='container justify-content-center mt-5 border-left border-right'>
      <div className='d-flex justify-content-center pt-3 pb-2'>
        <input type='text' name='text' placeholder='Add a comment' className='form-control addtxt' />
      </div>
      <Comment comment='Hi' author='John Doe' likes='0' />
      <Comment comment='Hi there' author='Jane Doe' likes='0' />
      <Comment comment='Hello' author='Anonymous' likes='69' />
      <Comment comment='Hello there' author='Anonymous' likes='420' />
      <Comment comment='Hi' author='John Doe' likes='0' />
      <Comment comment='Hi there' author='Jane Doe' likes='0' />
      <Comment comment='Hello' author='Anonymous' likes='69' />
      <Comment comment='Hello there' author='Anonymous' likes='420' />
      <Comment comment='Hi' author='John Doe' likes='0' />
      <Comment comment='Hi there' author='Jane Doe' likes='0' />
    </div>
  );
}

function CommentsModal(props) {
  const { comments, show, handleClose } = props;
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
          <Comments comments={comments} />
        </Modal.Body>
        <Modal.Footer>
          <Button onClick={handleClose}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
}

export default CommentsModal;
