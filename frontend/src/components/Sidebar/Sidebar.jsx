import './Sidebar.css';
import { Nav, Navbar } from 'react-bootstrap';
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

  const smallScreenClass = isSmallScreen ? 'sidebar-top' : '';
  const navbarClassList = `sidebar ${smallScreenClass}`;

  return (
    <Navbar className={navbarClassList}>
      <Navbar.Brand href="/">
        <img src={YoshiPhone} alt="BiggerYoshiLogo" className="sidelogo" />
      </Navbar.Brand>
      <Nav activeKey={location.pathname} className="nav-links">
        <Nav.Link href="/login" className="nav-link">
          <HouseDoor /> {!isSmallScreen && 'Home'}
        </Nav.Link>
        <Nav.Link href="/login" className="nav-link">
          <Person /> {!isSmallScreen && 'Profile'}
        </Nav.Link>
        <Nav.Link href="/login" className="nav-link">
          <Lock /> {!isSmallScreen && 'Private Posts'}
        </Nav.Link>
        <Nav.Link href="/login" className="nav-link">
          <Bell /> {!isSmallScreen && 'Notifications'}
        </Nav.Link>
        <Nav.Link href="/login" className="nav-link">
          <Gear /> {!isSmallScreen && 'Settings'}
        </Nav.Link>
      </Nav>
      {!isSmallScreen && (
        <button type="button" className="admin-button">
          Admin
        </button>
      )}
    </Navbar>
  );
}

export default Sidebar;
