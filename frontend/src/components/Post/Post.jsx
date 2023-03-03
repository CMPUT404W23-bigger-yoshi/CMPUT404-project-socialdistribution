import React, { useEffect, useState } from 'react';
import './Post.css';
import { getPost } from '../../services/post';
import { Button, Col, Dropdown, Row } from 'react-bootstrap';
import ReactMarkdown from 'react-markdown';
import { ChatLeftTextFill, ShareFill, ThreeDots } from 'react-bootstrap-icons';
import remarkGfm from 'remark-gfm';

const Post = (props) => {
  const { postId, authorId } = props;
  const [post, setPost] = useState({
    type: 'post',
    title: 'A post title about a post about web dev',
    id: 'http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/764efa883dda1e11db47671c4a3bbd9e',
    source: 'http://lastplaceigotthisfrom.com/posts/yyyyy',
    origin: 'http://whereitcamefrom.com/posts/zzzzz',
    description: 'This post discusses stuff -- brief',
    contentType: 'text/markdown',
    content:
      '# A post title about a post about web dev\n### AP is kinda OP ngl',
    author: {
      type: 'author',
      id: 'http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e',
      host: 'http://127.0.0.1:5454/',
      displayName: 'Lara Croft',
      url: 'http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e',
      github: 'http://github.com/laracroft',
      profileImage: 'https://i.imgur.com/k7XVwpB.jpeg'
    },
    categories: ['web', 'tutorial'],
    count: 1023,
    comments:
      'http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments',
    commentsSrc: {
      type: 'comments',
      page: 1,
      size: 5,
      post: 'http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/764efa883dda1e11db47671c4a3bbd9e',
      id: 'http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments',
      comments: [
        {
          type: 'comment',
          author: {
            type: 'author',
            id: 'http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471',
            url: 'http://127.0.0.1:5454/authors/1d698d25ff008f7538453c120f581471',
            host: 'http://127.0.0.1:5454/',
            displayName: 'Greg Johnson',
            github: 'http://github.com/gjohnson',
            profileImage: 'https://i.imgur.com/k7XVwpB.jpeg'
          },
          comment: 'Sick Olde English',
          contentType: 'text/markdown',
          published: '2015-03-09T13:07:04+00:00',
          id: 'http://127.0.0.1:5454/authors/9de17f29c12e8f97bcbbd34cc908f1baba40658e/posts/de305d54-75b4-431b-adb2-eb6b9e546013/comments/f6255bb01c648fe967714d52a89e8e9c'
        }
      ]
    },
    image: 'https://i.imgur.com/k7XVwpB.jpeg',
    published: '2015-03-09T13:07:04+00:00',
    visibility: 'PUBLIC',
    unlisted: false
  });

  function formatDate(date) {
    // Format it to show how long ago the post was published
    // For example, if the post was published 5 minutes ago, it should show "5 minutes ago"
    // If the post was published 1 hour ago, it should show "1 hour ago"
    // If the post was published 1 day ago, it should show "1 day ago"
    // Etcetera
    const now = new Date();
    const postDate = new Date(date);
    const diff = now - postDate;
    const diffInMinutes = Math.floor(diff / 60000);
    const diffInHours = Math.floor(diffInMinutes / 60);
    const diffInDays = Math.floor(diffInHours / 24);
    const diffInWeeks = Math.floor(diffInDays / 7);
    if (diffInMinutes < 60) {
      return diffInMinutes + ' min';
    } else if (diffInHours < 24) {
      return diffInHours + ' h';
    } else if (diffInDays < 7) {
      return diffInDays + ' d';
    }
    return diffInWeeks + ' w';
  }

  useEffect(() => {
    getPost(authorId, postId)
      .then((response) => {
        setPost(response.data);
      })
      .catch((error) => {
        console.log(error);
      });
  }, [authorId, postId]);
  return (
    <>
      <div className="post">
        <div className="post-container">
          <Row className="post-header">
            {/* The post header will contain the following: */}
            {/* 1. The author's profile image on the left */}
            {/* 2. The author's display name on the right of the image */}
            {/* 3. The post's visibility right below the display name */}
            {/* 4. The post's published date on the rightmost side of the header */}
            <Col md={6} xs={12}>
              <div className="post-info">
                <img
                  src={post.author.profileImage}
                  className="post-profile-image"
                />
                <div className="post-info-author">
                  <div className="post-author-name">
                    {post.author.displayName}{' '}
                    <span className="post-date">
                      • {formatDate(post.published)}
                    </span>
                  </div>
                  <div className="post-visibility">{post.visibility}</div>
                </div>
              </div>
            </Col>
            <Col md={6} xs={12}>
              <div className="post-published">{formatDate(post.published)}</div>
            </Col>
          </Row>
          <Row className="post-content">
            {/* The post content will contain the following: */}
            {/* 1. The post's title */}
            {/* 2. The post's content */}
            {/* 3. The post's categories */}
            {/* 4. The post's image if any */}
            <div className="post-title">
              <h3>{post.title}</h3>
            </div>
            <div className="post-categories">
              {post.categories.map((category, idx) => (
                <div key={idx} className="post-category">
                  {category}
                </div>
              ))}
            </div>
            <div className="post-body">
              {post.contentType === 'text/markdown' ? (
                <ReactMarkdown
                  children={post.content}
                  remarkPlugins={[remarkGfm]}
                />
              ) : (
                post.content
              )}
            </div>
            {post.image && (
              <div className="post-image">
                <img src={post.image} />
              </div>
            )}
          </Row>
          <Row className="post-footer">
            {/* The post footer will contain the following: */}
            {/* 1. The number of comments */}
            {/* 2. A share button */}
            {/* 3. A three dot button that will show a dropdown menu */}
            <Col xs={4} className="post-buttons">
              <div className="post-comments-count">
                <Button variant="dark">
                  <ChatLeftTextFill /> {post.count} Comments
                </Button>
              </div>
            </Col>
            <Col xs={4} className="post-buttons">
              <div className="post-share">
                <Button variant="dark">
                  <ShareFill /> Share
                </Button>
              </div>
            </Col>
            <Col xs={4} className="post-buttons">
              <div className="post-more">
                <Dropdown>
                  <Dropdown.Toggle variant="dark" id="dropdown-basic">
                    <ThreeDots /> More
                  </Dropdown.Toggle>

                  <Dropdown.Menu>
                    <Dropdown.Item href="#/action-1">Edit</Dropdown.Item>
                    <Dropdown.Item href="#/action-2">Delete</Dropdown.Item>
                    <Dropdown.Item href="#/action-3">Source</Dropdown.Item>
                    <Dropdown.Item href="#/action-4">Origin</Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>
              </div>
            </Col>
          </Row>
        </div>
      </div>
    </>
  );
};

export default Post;
