import React, { useState } from 'react';
import './ShareModal.css';
import { Button, Modal } from 'react-bootstrap';

export default function ShareModal(props) {
  /* The share modal will contain the following: */
  /* A title saying "Share" */
  /* A text field that will contain the link to the post */
  /* A button that will copy the link to the clipboard */
  /* A button that will close the modal */
  const [copy, setCopy] = useState(false);
  const { link, show, handleClose } = props;
  return (
    <div className='share-modal'>
      <Modal show={show} onHide={handleClose} backdrop='static' keyboard={false}>
        <Modal.Header closeButton>
          <Modal.Title>Share</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <div className='share-modal-body'>
            <input
              className='form-control'
              id='formControlReadonly'
              type='text'
              value={link}
              aria-label='readonly input example'
              readOnly
            />
          </div>
        </Modal.Body>
        <Modal.Footer>
          <Button variant='secondary' onClick={handleClose}>
            Close
          </Button>
          <Button
            variant={
              copy ? 'success' : 'primary'
            }
            onClick={() => {
              navigator.clipboard.writeText(link);
              // Change the button text to "Copied!"
              // Then change it back to "Copy" after 2 seconds
              setCopy(true);
              setTimeout(() => {
                setCopy(false);
              }, 1000);
            }}>
            {copy ? 'Copied!' : 'Copy'}
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
}
