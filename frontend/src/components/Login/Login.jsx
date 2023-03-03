import './Login.css';
import Logo from '../Logo/Logo';
import { Button, Col, Form, InputGroup, Row } from 'react-bootstrap';
import { KeyFill, PersonFill } from 'react-bootstrap-icons';
import React, { useState } from 'react';
import { login, register } from '../../services/auth';
import LoginModal from '../LoginModal/LoginModal';

const textContent = {
  Login: {
    title: 'Welcome back!',
    username: 'Username',
    password: 'Password',
    button: 'Login',
    accountStatus: "Don't have an account?",
    signup: 'Sign up here',
    redirect: '/register'
  },
  Register: {
    title: 'Create Account',
    username: 'Username',
    password: 'Password',
    confirmPassword: 'Confirm Password',
    button: 'Register',
    accountStatus: 'Already have an account?',
    signup: 'Login here',
    redirect: '/login'
  }
};

function Login(props) {
  const content = textContent[props.type];
  const [show, setShow] = useState(false);
  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);
  const [errorMsg, setError] = useState('Error');

  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (props.type === 'Login') {
      login(formData)
        .then((response) => {
          console.log(response);
        })
        .catch((error) => {
          setError(error.message || error.response.data);
          handleShow();
        });
    } else {
      register(formData)
        .then((response) => {
          console.log(response);
        })
        .catch((error) => {
          setError(error.message || error.response.data);
          handleShow();
        });
    }
  };

  return (
    <div className="login">
      <div className="login-container">
        <LoginModal
          title={content.button}
          error={errorMsg}
          show={show}
          handleClose={handleClose}
        />
        {/* Make the logo occupy 10% of the height of the screen */}
        <Row className="login-logo">
          <Logo size={'100px'} />
        </Row>
        <Row className="login-form-title">
          <div>
            <h1>{content.title}</h1>
          </div>
        </Row>
        <Row className="login-form-input">
          <div>
            <Form>
              <Form.Group
                controlId="formBasicUsername"
                className="formBasicUsername"
                as={Col}
              >
                <Form.Label>{content.username}</Form.Label>
                <InputGroup>
                  <InputGroup.Text>
                    <PersonFill />
                  </InputGroup.Text>
                  <Form.Control
                    type="text"
                    placeholder="Enter username"
                    onChange={(e) => {
                      setFormData({
                        ...formData,
                        username: e.target.value
                      });
                    }}
                  />
                </InputGroup>
              </Form.Group>

              <Form.Group
                controlId="formBasicPassword"
                className="formBasicPassword"
                as={Col}
              >
                <Form.Label>{content.password}</Form.Label>
                <InputGroup>
                  <InputGroup.Text>
                    <KeyFill />
                  </InputGroup.Text>
                  <Form.Control
                    type="password"
                    placeholder="Password"
                    onChange={(e) => {
                      setFormData({
                        ...formData,
                        password: e.target.value
                      });
                    }}
                  />
                </InputGroup>
              </Form.Group>

              {props.type === 'Register' && (
                <Form.Group
                  controlId="formBasicPassword"
                  className="formBasicPassword"
                  as={Col}
                >
                  <Form.Label>{content.confirmPassword}</Form.Label>
                  <InputGroup>
                    <InputGroup.Text>
                      <KeyFill />
                    </InputGroup.Text>
                    <Form.Control
                      type="password"
                      placeholder="Confirm Password"
                      onChange={(e) => {
                        setFormData({
                          ...formData,
                          confirmPassword: e.target.value
                        });
                      }}
                    />
                  </InputGroup>
                </Form.Group>
              )}
              <Button variant="primary" type="submit" onClick={handleSubmit}>
                {content.button}
              </Button>
            </Form>
          </div>
        </Row>
        <Row className="login-form-signup">
          <div>
            <Row>
              <Col className="signup-text" xs={12}>
                <p>{content.accountStatus}</p>
              </Col>
              <Col
                className="signup-link"
                xs={12}
                onClick={() => {
                  window.location.href = content.redirect;
                }}
              >
                <p>{content.signup}</p>
              </Col>
            </Row>
          </div>
        </Row>
      </div>
    </div>
  );
}

export default Login;
