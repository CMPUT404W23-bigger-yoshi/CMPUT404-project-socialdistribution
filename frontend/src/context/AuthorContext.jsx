import React, { useState } from 'react';

const AuthorContext = React.createContext({});
function AuthorProvider({ children }) {
  const [author, setAuthor] = useState({});

  return (
    <AuthorContext.Provider value={{ author, setAuthor }}>
      {children}
    </AuthorContext.Provider>
  );
}

export { AuthorContext, AuthorProvider };
