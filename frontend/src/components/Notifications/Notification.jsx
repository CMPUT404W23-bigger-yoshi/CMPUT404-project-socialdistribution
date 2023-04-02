import './Notification.css';
import React from 'react';
import {
  ChatLeftFill,
  CheckCircleFill,
  HeartFill,
  PeopleFill,
  XCircleFill
} from 'react-bootstrap-icons';
import { acceptFollowRequest } from '../../services/author';

function Notification(props) {
  return (
    <div className="notification">
      <div className="left">
        <img
          width={70}
          height={70}
          className="notification-logo"
          src={props.person.profileImage}
        />
        <p>
          {props.type === 'friend' ? (
            `${props.person} is now your friend!`
          ) : props.type === 'like' ? (
            `${props.person} liked your post!`
          ) : props.type === 'comment' ? (
            `${props.person} commented on your post!`
          ) : props.type === 'follow' ? (
            `${props.person.displayName} wants to follow you!`
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
            <CheckCircleFill
              size={40}
              className="follow-icon accept"
              onClick={() => {
                acceptFollowRequest(
                  props.localAuthor.id.split('/').pop(-1),
                  props.person.url
                );
              }}
            />{' '}
            <XCircleFill size={40} className="follow-icon reject" />
          </div>
        ) : (
          <div></div>
        )}
      </div>
    </div>
  );
}

export default Notification;
