import './Notifications.css';
import Notification from './Notification';
import React from 'react';

function Notifications() {
  return (
    <div className="notifications">
      <div className="notificationsbox">
        <div className="header">
          <a>All</a>
          <a>Posts</a>
          <a>Following</a>
        </div>
        <Notification type="friend" person="Akshat" />
        <Notification type="like" person="Manpreet" />
        <Notification type="comment" person="Matty" />
        <Notification type="follow" person="Your mom" />
      </div>
    </div>
  );
}

export default Notifications;
