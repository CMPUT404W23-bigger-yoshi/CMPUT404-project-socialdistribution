import './Notifications.css';
import Notification from './Notification';
import React, { useContext, useEffect, useState } from 'react';
import { AuthorContext } from '../../context/AuthorContext';
import { getFollowRequests } from '../../services/author';

function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const author = useContext(AuthorContext).author;

  const updateNotifications = async () => {
    const data = (await getFollowRequests(author.id.split('/').pop(-1))).data
      .follow_requests;
    setNotifications(data);
    console.log(data);
  };

  useEffect(() => {
    updateNotifications();
  }, []);

  return (
    <div className="notifications">
      <div className="notificationsbox">
        <div className="header">
          <a>All</a>
          <a>Posts</a>
          <a>Following</a>
        </div>
        {notifications.map((notification, idx) => (
          <Notification
            key={idx}
            type={notification.type}
            person={notification.author}
          />
        ))}
      </div>
    </div>
  );
}

export default Notifications;
