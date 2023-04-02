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
import { useNavigate } from 'react-router-dom';

function Notification(props) {
  const navigate = useNavigate();
  return (
    <div className="notification">
      <div className="left">
        <img
          width={70}
          height={70}
          className="notification-logo"
          src={
            props.person.profileImage !== ''
              ? props.person.profileImage
              : 'https://i.pinimg.com/originals/f1/0f/f7/f10ff70a7155e5ab666bcdd1b45b726d.jpg'
          }
          alt="profile"
        />
        <p>
          {props.type === 'friend' ? (
            `${props.person} is now your friend!`
          ) : props.type === 'like' ? (
            `${props.person} liked your post!`
          ) : props.type === 'comment' ? (
            `${props.person} commented on your post!`
          ) : props.type === 'follow' ? (
            <div
              className="follow"
              onClick={() => navigate(`/authors?q=${props.person.id}`)}
            >
              <span className="user-name">{props.person.displayName}</span>
              <span> wants to follow you!</span>
            </div>
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
                ).then((res) => {
                  console.log(res);
                });
                props.setNotificationsUpdated(true);
              }}
            />{' '}
          </div>
        ) : (
          <div></div>
        )}
      </div>
    </div>
  );
}

export default Notification;
