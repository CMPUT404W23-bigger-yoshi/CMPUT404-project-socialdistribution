import './Notifications.css';
import Notification from './Notification';
import React, { useContext, useEffect, useState } from 'react';
import { AuthorContext } from '../../context/AuthorContext';
import { getFollowRequests } from '../../services/author';

function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const author = useContext(AuthorContext).author;
  const [notificationsUpdated, setNotificationsUpdated] = useState(false);

  const updateNotifications = async () => {
    const data = (await getFollowRequests(author.id.split('/').pop(-1))).data
      .follow_requests;
    setNotifications(data);
    setNotificationsUpdated(false);
    console.log(data);
  };

  useEffect(() => {
    updateNotifications();
  }, [notificationsUpdated]);

  return (
    <div className='notifications'>
      <div className='notificationsbox'>
        {notifications.length > 0 ? (
            notifications.map((notification, idx) => (
              <Notification
                key={idx}
                type={notification.type}
                person={notification.author}
                localAuthor={author}
                setNotificationsUpdated={setNotificationsUpdated}
              />
            ))
          ) : (
            <div className='no-notifications'
                 style={{ textAlign: 'center', marginTop: '40%' }}>
              <br />
              <h1>No notifications to show</h1>
            </div>
          )}
      </div>
    </div>
  );
}

export default Notifications;
