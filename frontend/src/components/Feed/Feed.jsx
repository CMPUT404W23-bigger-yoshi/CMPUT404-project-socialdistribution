import React, { useState, useEffect, useContext } from 'react';
import './Feed.css';
import { getInbox } from '../../services/post';
import Post from '../Post/Post';
import { AuthorContext } from '../../context/AuthorContext';

function Feed(props) {
  const { userId, isInbox } = props;
  const { author } = useContext(AuthorContext);
  console.log(`feed author: ${author.id}`);
  const [posts, setPosts] = useState([]);
  useEffect(() => {
    // Fetch posts from backend
    const fetchPosts = async () => {
      try {
        const response = await getInbox(author.id);
        setPosts(response.data.items);
      } catch (error) {
        console.log(error);
      }
    };
    fetchPosts().then((r) => console.log(r));
  }, [userId, isInbox]);
  return (
    <div className="feed">
      {posts.length > 0 ? (
        posts.map((post) => (
          <Post post={post} key={post.id} currentUser={userId} />
        ))
      ) : (
        <>
          <br />
          <h1>No posts to show</h1>
        </>
      )}
    </div>
  );
}

export default Feed;
