import React, { useEffect } from 'react';
import './Feed.css';
import { getInbox } from '../../services/post';
import Post from '../Post/Post';

function Feed(props) {
  const { userId, isPrivate } = props;
  const [posts, setPosts] = React.useState([]);
  useEffect(() => {
    // Fetch posts from backend
    const fetchPosts = async () => {
      try {
        const response = await getInbox(userId);
        setPosts(response.data.items);
      } catch (error) {
        console.log(error);
      }
    };
    fetchPosts().then(r => console.log(r));
  }, [userId, isPrivate]);
  return (
    <div className='feed'>
      {posts.length > 0 ? (
        posts.map((post) => <Post post={post} key={post.id} />)
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
