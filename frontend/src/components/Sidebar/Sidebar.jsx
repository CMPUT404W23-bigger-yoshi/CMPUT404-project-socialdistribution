import './Sidebar.css';
import { Nav, Navbar, Container } from 'react-bootstrap';
import { useLocation } from 'react-router-dom';
import { Gear, Bell, Person, Lock, HouseDoor } from 'react-bootstrap-icons';
import React, { useEffect, useState } from 'react';
import YoshiPhone from '../../static/Yoshi-phone.png';

function Sidebar() {
  const location = useLocation(); // Need this for highlighting current location
  const [isSmallScreen, setIsSmallScreen] = useState(window.innerWidth <= 768);

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
      <Nav activeKey={location.pathname} className="nav-links">
        <Nav.Link href="/login" className="nav-link">
          <HouseDoor /> Home
        </Nav.Link>
        <Nav.Link href="/login" className="nav-link">
          <Person /> Profile
        </Nav.Link>
        <Nav.Link href="/login" className="nav-link">
          <Lock /> Private Posts
        </Nav.Link>
        <Nav.Link href="/login" className="nav-link">
          <Bell /> Notifications
        </Nav.Link>
        <Nav.Link href="/login" className="nav-link">
          <Gear /> Settings
        </Nav.Link>
      </Nav>
      <button type="button" className="admin-button">
        Admin
      </button>
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
            <Nav.Link href="/login" className="nav-link">
              <HouseDoor className="icon" /> Home
            </Nav.Link>
            <Nav.Link href="/login" className="nav-link">
              <Person className="icon" /> Profile
            </Nav.Link>
            <Nav.Link href="/login" className="nav-link">
              <Lock className="icon" /> Private Posts
            </Nav.Link>
            <Nav.Link href="/login" className="nav-link">
              <Bell className="icon" /> Notifications
            </Nav.Link>
            <Nav.Link href="/login" className="nav-link">
              <Gear className="icon" /> Settings
            </Nav.Link>
          </Nav>
          <button type="button" className="admin-button">
            Admin
          </button>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}

export default Sidebar;
