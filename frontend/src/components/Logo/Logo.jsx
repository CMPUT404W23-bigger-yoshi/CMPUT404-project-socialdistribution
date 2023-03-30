import React from 'react';
import YoshiPhone from '../../static/Yoshi-phone.png';

function Logo(props) {
  return (
    <div className={props.className + ' logo'}>
      <img
        src={props.src || YoshiPhone}
        alt="Yoshi Phone"
        height={props.size}
        width={props.size}
      />
    </div>
  );
}

export default Logo;
