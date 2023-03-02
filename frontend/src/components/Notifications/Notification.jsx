import './Notification.css'
import React from 'react'
import Logo from '../Logo/Logo'
import { Gear } from 'react-bootstrap-icons'

function Notification() {
  return (
    <div className="notification">
      <div className="left">
        <Logo className="logo" />
        <p>Lorem ipsum dolor, sit amet consectetur adipisicing elit.</p>
      </div>
      <div className="right">
        <Gear />
      </div>
    </div>
  )
}

export default Notification
