import './Notifications.css'
import Notification from './Notification'
import React from 'react'

function Notifications() {
  return (
    <div className="container">
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
  )
}

export default Notifications
