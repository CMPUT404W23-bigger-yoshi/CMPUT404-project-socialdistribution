import React, { useContext, useState } from 'react';
import './Settings.css';
import { Button, Form, InputGroup } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { updateCurrentUserDetails } from '../../services/author';
import MessageModal from '../MessageModal/MessageModal';
import { AuthorContext } from '../../context/AuthorContext';

function Settings() {
  const navigate = useNavigate();
  const [userDetails, setUserDetails] = useState(useContext(AuthorContext).author);
  const [errorMsg, setError] = useState('Error');
  const [show, setShow] = useState(false);
  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await updateCurrentUserDetails(userDetails.id, userDetails);
      console.log(res);
      setError('Settings updated successfully');
      handleShow();
    } catch (error) {
      if (error.response.status === 409) {
        setError(error.response.data.message);
        handleShow();
      } else {
        setError('Error updating settings');
        handleShow();
      }
      console.log(error);
    }
  };
  // added function to handle file selection and convert to base64 encoded string
  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result;
      setUserDetails({ ...userDetails, profileImage: dataUrl }); // updated userDetails state variable
    };
    reader.readAsDataURL(file);
  };
  return (
    <div className='settings'>
      <div className='settings-border'>
        <div className='settings-container'>
          <MessageModal
            title={'Settings'}
            show={show}
            error={errorMsg}C
            handleClose={handleClose}
          />
          <div className='settings-title'>
            <h1>Settings</h1>
            <hr />
          </div>
          <div className='settings-content'>
            <img src={userDetails.profileImage} alt='profile' />
            {/* The settings will contain option to change user's: */}
            {/* - username */}
            {/* github link */}
            {/* profile picture */}
            {/* button to admin page if user is admin */}
            <Form className='settings-form'>
              <Form.Group className='settings-form-group'>
                <Form.Label>Username</Form.Label>
                <Form.Control
                  type='text'
                  placeholder='Enter username'
                  value={userDetails.displayName}
                  onChange={(e) =>
                    setUserDetails({
                      ...userDetails,
                      displayName: e.target.value
                    })
                  }
                  disabled={window.location.origin !== userDetails.host}
                />
              </Form.Group>
              <Form.Group className='settings-form-group'>
                <Form.Label>Github Link</Form.Label>
                <InputGroup className='mb-3'>
                  <InputGroup.Text id='basic-addon3'>
                    https://github.com/
                  </InputGroup.Text>
                  <Form.Control id='basic-url' aria-describedby='basic-addon3'
                                onChange={(e) =>
                                  setUserDetails({
                                    ...userDetails,
                                    github: 'https://github.com/' + e.target.value
                                  })
                                }
                                disabled={window.location.origin !== userDetails.host}
                  />
                </InputGroup>
              </Form.Group>
              <Form.Group className='settings-form-group'>
                <Form.Label>Profile Picture</Form.Label>
                <Form.Control
                  type='file'
                  accept='image/*'
                  placeholder='Enter profile picture'
                  onChange={handleImageSelect} // added onChange handler to handle file selection
                  disabled={window.location.origin !== userDetails.host}
                />
              </Form.Group>
              <Button
                variant='primary'
                type='submit'
                className='settings-submit'
                onClick={handleSubmit}
                disabled={window.location.origin !== userDetails.host}
              >
                {window.location.origin === userDetails.host
                  ? 'Save Changes'
                  : 'Cannot edit settings on other hosts'
                }
              </Button>
            </Form>
            <div className='settings-admin'>
              <Button variant='success' onClick={() => window.open('/admin/', '_self')}>
                Admin Page
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Settings;
