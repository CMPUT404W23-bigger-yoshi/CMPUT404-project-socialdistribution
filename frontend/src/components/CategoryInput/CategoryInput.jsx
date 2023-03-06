import React, { useState } from 'react';
import './CategoryInput.css';

function CategoryInput(props) {
  const { categories, setCategories } = props;
  const [currentRecipient, setCurrentRecipient] = useState('');

  function handleInputChange(event) {
    setCurrentRecipient(event.target.value);
  }

  function handleInputKeyDown(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      addRecipient(currentRecipient);
    } else if (event.key === 'Backspace' && currentRecipient === '') {
      removeRecipient(categories.length - 1);
    }
  }

  function addRecipient(recipient) {
    if (recipient !== '' && !categories.includes(recipient)) {
      setCategories([...categories, recipient]);
      setCurrentRecipient('');
    }
  }

  function removeRecipient(index) {
    setCategories([
      ...categories.slice(0, index),
      ...categories.slice(index + 1)
    ]);
  }

  return (
    <div style={{ display: 'flex' }} className="category-input">
      {categories?.map((recipient, index) => (
        <span key={index} className="recipient" style={{ marginRight: '5px' }}>
          {
            recipient.length > 7
              ? recipient.substring(0, 7) + '...'
              : recipient
          }
          <button className="remove" onClick={() => removeRecipient(index)}>
            x
          </button>
        </span>
      ))}
      <input
        className="category-input-field"
        type="text"
        placeholder={categories.length === 0 ? 'Add a category' : ''}
        value={currentRecipient}
        onChange={handleInputChange}
        onKeyDown={handleInputKeyDown}
        disabled={categories.length >= 3}
        style={{ flex: 1 }}
      />
    </div>
  );
}

export default CategoryInput;
