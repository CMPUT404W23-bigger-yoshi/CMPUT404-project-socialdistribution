import './Notifications.css';
import Notification from './Notification';
import React from 'react';
import Sidebar from '../Sidebar/Sidebar';

function Notifications() {
  return (
    <div className="page">
      <Sidebar />
      <div className="notifications">
        <div className="notificationsbox">
          <div className="header">
            <a>All</a>
            <a>Posts</a>
            <a>Following</a>
          </div>
          <Notification />
          <Notification />
          <Notification />
          <Notification />
          <Notification />
          <Notification />
          <Notification />
        </div>
      </div>
    </div>
  );
}

export default Notifications;
