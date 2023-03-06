import React, { useEffect, useState } from 'react';
import './Settings.css';
import { Button, Form } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { getCurrentUserDetails, getCurrentUserId, updateCurrentUserDetails } from '../../services/author';

function Settings() {
  const navigate = useNavigate();
  const [userDetails, setUserDetails] = useState({
    id: '',
    displayName: '',
    github: '',
    profileImage: ''
  });
  useEffect(() => {
    const getUserDetails = async () => {
      try {
        const response = await getCurrentUserId();
        const id = response.data.id;
        const user = await getCurrentUserDetails(id);
        setUserDetails({ ...user.data, id });
      } catch (error) {
        console.log(error);
      }
    };
    getUserDetails().then(r => console.log(r));
  }, []);
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await updateCurrentUserDetails(userDetails.id, userDetails);
      console.log(res);
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div className='settings'>
      <div className='settings-border'>
        <div className='settings-container'>
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
                <Form.Control type='text'
                              placeholder='Enter username'
                              value={userDetails.displayName}
                              onChange={(e) => setUserDetails({ ...userDetails, displayName: e.target.value })}
                />
              </Form.Group>
              <Form.Group className='settings-form-group'>
                <Form.Label>Github Link</Form.Label>
                <Form.Control type='link'
                              placeholder='Enter github link'
                              value={userDetails.github}
                              onChange={(e) => setUserDetails({ ...userDetails, github: e.target.value })}
                />
              </Form.Group>
              <Form.Group className='settings-form-group'>
                <Form.Label>Profile Picture</Form.Label>
                <Form.Control type='file'
                              accept='image/*'
                              placeholder='Enter profile picture'
                />
              </Form.Group>
              <Button variant='primary'
                      type='submit'
                      className='settings-submit'
                      onClick={handleSubmit}
              >
                Submit
              </Button>
            </Form>
            <div className='settings-admin'>
              <Button variant='success' onClick={() => navigate('/admin')}>
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
