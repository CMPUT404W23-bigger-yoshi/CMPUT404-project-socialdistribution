import React, { useState, useEffect, useContext } from 'react';
import './Feed.css';
import { getHomeFeed, getInbox } from '../../services/post';
import Post from '../Post/Post';
import { AuthorContext } from '../../context/AuthorContext';
import CreatePost from '../Post/CreatePost';

function Feed(props) {
  const { isInbox } = props;
  const { author } = useContext(AuthorContext);
  console.log(`feed author: ${author.id}`);
  const [posts, setPosts] = useState([]);
  const [updateFeed, setUpdateFeed] = useState(false);
  useEffect(() => {
    // Fetch posts from backend
    const fetchPosts = async () => {
      try {
        let response;
        if (isInbox) {
          response = await getInbox(author.id);
        } else {
          response = await getHomeFeed();
        }
        setPosts(response.data.items);
      } catch (error) {
        console.log(error);
      }
    };
    fetchPosts().then((r) => setUpdateFeed(false));
  }, [isInbox, updateFeed]);
  return (
    <div className="feed">
      <CreatePost setUpdateFeed={setUpdateFeed} />
      {posts?.length > 0 ? (
        posts.map((post) => (
          <Post post={post} key={post.id} currentUser={author.id} />
        ))
      ) : (
        <div className="no-posts" style={{ textAlign: 'center', marginTop: '40%' }}>
          <h1>No posts to show</h1>
        </div>
      )}
    </div>
  );
}

export default Feed;
