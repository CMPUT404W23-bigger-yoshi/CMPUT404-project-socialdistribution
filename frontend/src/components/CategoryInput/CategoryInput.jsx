import React, { useState } from 'react';
import './CategoryInput.css';

function CategoryInput() {
  const [recipients, setRecipients] = useState([]);
  const [currentRecipient, setCurrentRecipient] = useState('');

  function handleInputChange(event) {
    setCurrentRecipient(event.target.value);
  }

  function handleInputKeyDown(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      addRecipient(currentRecipient);
    } else if (event.key === 'Backspace' && currentRecipient === '') {
      removeRecipient(recipients.length - 1);
    }
  }

  function addRecipient(recipient) {
    if (recipient !== '' && !recipients.includes(recipient)) {
      setRecipients([...recipients, recipient]);
      setCurrentRecipient('');
    }
  }

  function removeRecipient(index) {
    setRecipients([...recipients.slice(0, index), ...recipients.slice(index + 1)]);
  }

  return (
    <div style={{ display: 'flex' }} className='category-input'>
      {recipients.map((recipient, index) => (
        <span key={index} className='recipient' style={{ marginRight: '5px' }}>
          {recipient}
          <button className='remove' onClick={() => removeRecipient(index)}>x</button>
        </span>
      ))}
      <input
        className='category-input-field'
        type='text'
        placeholder={recipients.length === 0 ? 'Add a category' : ''}
        value={currentRecipient}
        onChange={handleInputChange}
        onKeyDown={handleInputKeyDown}
        disabled={recipients.length >= 3}
        style={{ flex: 1 }}
      />
    </div>
  );
}

export default CategoryInput;
