import './Notification.css';
import React from 'react';
import Logo from '../Logo/Logo';
import {
  ChatLeftFill,
  CheckCircleFill,
  HeartFill,
  PeopleFill,
  XCircleFill
} from 'react-bootstrap-icons';

function Notification(props) {
  return (
    <div className="notification">
      <div className="left">
        <Logo size={70} className="notification-logo" />
        <p>
          {props.type === 'friend' ? (
            `${props.person} is now your friend!`
          ) : props.type === 'like' ? (
            `${props.person} liked your post!`
          ) : props.type === 'comment' ? (
            `${props.person} commented on your post!`
          ) : props.type === 'follow' ? (
            `${props.person} wants to follow you!`
          ) : (
            <div></div>
          )}
        </p>
      </div>
      <div className="right">
        {props.type === 'friend' ? (
          <PeopleFill size={30} />
        ) : props.type === 'like' ? (
          <HeartFill size={30} />
        ) : props.type === 'comment' ? (
          <ChatLeftFill size={30} />
        ) : props.type === 'follow' ? (
          /* Two icons one is checkmark and other is x */
          <div className="follow-icons">
            <CheckCircleFill size={40} /> <XCircleFill size={40} />
          </div>
        ) : (
          <div></div>
        )}
      </div>
    </div>
  );
}

export default Notification;
