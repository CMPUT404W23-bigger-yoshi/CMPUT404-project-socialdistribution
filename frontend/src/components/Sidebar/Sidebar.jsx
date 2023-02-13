import './Sidebar.css';
import { Nav, Navbar } from 'react-bootstrap';
import { useLocation } from 'react-router-dom';
import { Gear, Bell, Person, Lock, HouseDoor } from 'react-bootstrap-icons';
import React from 'react';
import YoshiPhone from '../../static/Yoshi-phone.png';

function Searchbar() {
  return (
<div className="input-group">
  <input type="search" className="form-control rounded" placeholder="Search" aria-label="Search" aria-describedby="search-addon" />
  <button type="button" className="btn btn-outline-primary">search</button>
</div>
  )
}

function Sidebar() {
  const location = useLocation(); // Need this for highlighting current location

  return (
    <Navbar expand="md" className="sidebar">
      <Navbar.Brand href="/">
        <img src={YoshiPhone} alt="BiggerYoshiLogo" className="sidelogo" />
      </Navbar.Brand>
      <Navbar.Toggle aria-controls="basic-navbar-nav" />
      <Searchbar/>
      <Navbar.Collapse id="basic-navbar-nav">
        <Nav activeKey={location.pathname} className="flex-column">
          <Nav.Link href="/login" className="nav-link">
            <HouseDoor /> Home
          </Nav.Link>
          <Nav.Link href="/login">
            <Person /> Profile
          </Nav.Link>
          <Nav.Link href="/login">
            <Lock /> Private Posts
          </Nav.Link>
          <Nav.Link href="/login">
            <Bell /> Notifications
          </Nav.Link>
          <Nav.Link href="/login">
            <Gear /> Settings
          </Nav.Link>
        </Nav>
      </Navbar.Collapse>
      <button type="button" className="admin-button">
        Admin
      </button>
    </Navbar>
  );
}

export default Sidebar;
