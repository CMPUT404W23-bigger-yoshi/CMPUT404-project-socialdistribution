import './Notification.css';
import React from 'react';
import Logo from '../Logo/Logo';
import { People } from 'react-bootstrap-icons';

function Notification() {
  return (
    <div className="notification">
      <div className="left">
        <Logo className="logo" />
        <p>
          <b>Mohammad Hammad</b> and you are now friends
        </p>
      </div>
      <div className="right">
        <People />
      </div>
    </div>
  );
}

export default Notification;
