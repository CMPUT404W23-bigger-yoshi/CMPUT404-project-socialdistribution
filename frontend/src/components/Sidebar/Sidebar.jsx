import './Sidebar.css';
import { Button, Container, Form, Nav, Navbar } from 'react-bootstrap';
import { useLocation, useNavigate } from 'react-router-dom';
import { Bell, Gear, House, Inbox, Lock, Person } from 'react-bootstrap-icons';
import React, { useEffect, useState } from 'react';
import YoshiPhone from '../../static/Yoshi-phone.png';
import { searchMultipleUsers } from '../../services/author';
import { Typeahead } from 'react-bootstrap-typeahead';

function Sidebar() {
  const location = useLocation(); // Need this for highlighting current location
  const navigate = useNavigate(); // Need this for redirecting to login page
  const [isSmallScreen, setIsSmallScreen] = useState(window.innerWidth <= 768);
  const [usernames, setUsernames] = useState([]);

  useEffect(() => {
    function handleResize() {
      setIsSmallScreen(window.innerWidth <= 768);
    }

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return !isSmallScreen ? (
    <Navbar className="sidebar">
      <Navbar.Brand href="/">
        <img src={YoshiPhone} alt="BiggerYoshiLogo" className="sidelogo" />
      </Navbar.Brand>
      {/* Include search bar here */}
      <Form className="d-flex search-bar">
        <Typeahead
          id="search-bar"
          labelKey="displayName"
          onChange={(selected) => {
            if (selected.length > 0) {
              // Get the last part of the URL (that is the id)
              setUsernames([]);
              const id = selected[0].id.split('/').pop();
              navigate(`/authors/${id}`);
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
      <Nav activeKey={location.pathname} className="nav-links">
        <Nav.Link onClick={() => navigate('/')} className="nav-link">
          <House /> Home
        </Nav.Link>
        <Nav.Link onClick={() => navigate('/inbox')} className="nav-link">
          <Inbox /> Inbox
        </Nav.Link>
        <Nav.Link onClick={() => navigate('/profile')} className="nav-link">
          <Person /> Profile
        </Nav.Link>
        <Nav.Link
          onClick={() => navigate('/notifications')}
          className="nav-link"
        >
          <Bell /> Notifications
        </Nav.Link>
        <Nav.Link onClick={() => navigate('/settings')} className="nav-link">
          <Gear /> Settings
        </Nav.Link>
      </Nav>
      <Button
        variant="success"
        className="admin-button"
        onClick={() => navigate('/logout')}
      >
        Logout
      </Button>
    </Navbar>
  ) : (
    <Navbar expand="lg" variant="dark" className="top-navbar">
      <Container>
        <Navbar.Brand href="/">
          <img src={YoshiPhone} alt="BiggerYoshiLogo" className="sidelogo" />
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link className="nav-link" onClick={() => navigate('/')}>
              <Inbox className="icon" /> Inbox
            </Nav.Link>
            <Nav.Link onClick={() => navigate('/profile')} className="nav-link">
              <Person className="icon" /> Profile
            </Nav.Link>
            <Nav.Link onClick={() => navigate('/private')} className="nav-link">
              <Lock className="icon" /> Private Posts
            </Nav.Link>
            <Nav.Link
              onClick={() => navigate('/notifications')}
              className="nav-link"
            >
              <Bell className="icon" /> Notifications
            </Nav.Link>
            <Nav.Link
              onClick={() => navigate('/settings')}
              className="nav-link"
            >
              <Gear className="icon" /> Settings
            </Nav.Link>
          </Nav>
          <Button
            variant="success"
            className="admin-button"
            onClick={() => navigate('/logout')}
          >
            Logout
          </Button>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}

export default Sidebar;
