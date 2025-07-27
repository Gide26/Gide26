import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Set up axios interceptor for auth
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

function App() {
  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('feed');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  const [showCreatePost, setShowCreatePost] = useState(false);

  // Auth form states
  const [authForm, setAuthForm] = useState({
    email: '',
    password: '',
    name: '',
    location: '',
    bio: ''
  });

  // Post form states
  const [postForm, setPostForm] = useState({
    content: '',
    image_base64: '',
    category: 'general'
  });

  const [comments, setComments] = useState({});
  const [showComments, setShowComments] = useState({});
  const [commentForm, setCommentForm] = useState('');
  const fileInputRef = useRef(null);

  useEffect(() => {
    checkAuth();
    fetchPosts();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const response = await axios.get(`${API}/users/me`);
        setUser(response.data);
      } catch (error) {
        localStorage.removeItem('token');
      }
    }
    setIsLoading(false);
  };

  const fetchPosts = async () => {
    try {
      const response = await axios.get(`${API}/posts`);
      setPosts(response.data);
    } catch (error) {
      console.error('Error fetching posts:', error);
    }
  };

  const handleAuth = async (e) => {
    e.preventDefault();
    try {
      let endpoint = authMode === 'login' ? '/auth/login' : '/auth/register';
      const response = await axios.post(`${API}${endpoint}`, authForm);
      
      localStorage.setItem('token', response.data.token);
      setUser(response.data.user);
      setShowAuthModal(false);
      setAuthForm({ email: '', password: '', name: '', location: '', bio: '' });
    } catch (error) {
      alert(error.response?.data?.detail || 'Authentication failed');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setActiveTab('feed');
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setPostForm(prev => ({ ...prev, image_base64: e.target.result }));
      };
      reader.readAsDataURL(file);
    }
  };

  const handleCreatePost = async (e) => {
    e.preventDefault();
    if (!postForm.content.trim()) return;

    try {
      await axios.post(`${API}/posts`, postForm);
      setPostForm({ content: '', image_base64: '', category: 'general' });
      setShowCreatePost(false);
      fetchPosts();
    } catch (error) {
      alert('Error creating post');
    }
  };

  const handleLike = async (postId) => {
    try {
      const response = await axios.post(`${API}/posts/${postId}/like`);
      setPosts(posts.map(post => 
        post.id === postId 
          ? { ...post, likes: response.data.liked 
              ? [...(post.likes || []), user.id]
              : (post.likes || []).filter(id => id !== user.id) }
          : post
      ));
    } catch (error) {
      console.error('Error liking post:', error);
    }
  };

  const fetchComments = async (postId) => {
    try {
      const response = await axios.get(`${API}/posts/${postId}/comments`);
      setComments(prev => ({ ...prev, [postId]: response.data }));
    } catch (error) {
      console.error('Error fetching comments:', error);
    }
  };

  const handleComment = async (postId) => {
    if (!commentForm.trim()) return;

    try {
      await axios.post(`${API}/comments`, {
        post_id: postId,
        content: commentForm
      });
      setCommentForm('');
      fetchComments(postId);
    } catch (error) {
      console.error('Error creating comment:', error);
    }
  };

  const toggleComments = async (postId) => {
    if (!showComments[postId]) {
      await fetchComments(postId);
    }
    setShowComments(prev => ({ ...prev, [postId]: !prev[postId] }));
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-lg border-b-4 border-green-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center">
                <span className="text-white font-bold text-xl">R</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">REAF Community</h1>
                <p className="text-sm text-gray-600">Ricky East African Foundation</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {user ? (
                <>
                  <span className="text-gray-700">Welcome, {user.name}!</span>
                  <button
                    onClick={handleLogout}
                    className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-lg transition-colors"
                >
                  Join Community
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      {!user && (
        <div className="relative bg-gradient-to-r from-green-600 to-blue-600 text-white py-16">
          <div className="absolute inset-0 bg-black opacity-40"></div>
          <div 
            className="absolute inset-0 bg-cover bg-center"
            style={{backgroundImage: 'url(https://images.unsplash.com/photo-1744972974629-daa2fdaa15ee?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwyfHx5b3V0aCUyMGVtcG93ZXJtZW50JTIwYWZyaWNhfGVufDB8fHx8MTc1MzYwMzUwNXww&ixlib=rb-4.1.0&q=85)'}}
          ></div>
          <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-5xl font-bold mb-6">Empowering Youth Across East Africa</h2>
            <p className="text-xl mb-8 max-w-3xl mx-auto">
              Join our community focused on health education, youth empowerment, entrepreneurship, and building stronger communities together.
            </p>
            <button
              onClick={() => setShowAuthModal(true)}
              className="bg-white text-green-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors text-lg"
            >
              Get Started Today
            </button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {user && (
          <div className="mb-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-semibold text-gray-800">Share with the Community</h3>
                <button
                  onClick={() => setShowCreatePost(!showCreatePost)}
                  className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  {showCreatePost ? 'Cancel' : 'Create Post'}
                </button>
              </div>

              {showCreatePost && (
                <form onSubmit={handleCreatePost} className="space-y-4">
                  <div>
                    <select
                      value={postForm.category}
                      onChange={(e) => setPostForm(prev => ({ ...prev, category: e.target.value }))}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    >
                      <option value="general">General</option>
                      <option value="health">Health & Wellness</option>
                      <option value="empowerment">Youth Empowerment</option>
                      <option value="entrepreneurship">Entrepreneurship</option>
                      <option value="sports">Sports & Recreation</option>
                    </select>
                  </div>
                  <div>
                    <textarea
                      value={postForm.content}
                      onChange={(e) => setPostForm(prev => ({ ...prev, content: e.target.value }))}
                      placeholder="Share your thoughts, experiences, or ask questions..."
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
                      rows="4"
                    ></textarea>
                  </div>
                  <div className="flex items-center space-x-4">
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleImageUpload}
                      ref={fileInputRef}
                      className="hidden"
                    />
                    <button
                      type="button"
                      onClick={() => fileInputRef.current.click()}
                      className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-lg transition-colors"
                    >
                      Add Image
                    </button>
                    <button
                      type="submit"
                      className="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-lg transition-colors"
                    >
                      Share Post
                    </button>
                  </div>
                  {postForm.image_base64 && (
                    <div className="mt-4">
                      <img src={postForm.image_base64} alt="Preview" className="max-w-xs rounded-lg" />
                    </div>
                  )}
                </form>
              )}
            </div>
          </div>
        )}

        {/* Posts Feed */}
        <div className="space-y-6">
          {posts.map((post) => (
            <div key={post.id} className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-r from-green-400 to-blue-400 rounded-full flex items-center justify-center">
                      <span className="text-white font-semibold">{post.user_name.charAt(0).toUpperCase()}</span>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900">{post.user_name}</h4>
                      <div className="flex items-center space-x-2 text-sm text-gray-500">
                        <span>{formatDate(post.created_at)}</span>
                        <span>•</span>
                        <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full capitalize">
                          {post.category}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <p className="text-gray-800 mb-4 leading-relaxed">{post.content}</p>

                {post.image_base64 && (
                  <div className="mb-4">
                    <img src={post.image_base64} alt="Post content" className="rounded-lg max-w-full h-auto" />
                  </div>
                )}

                {user && (
                  <div className="flex items-center space-x-6 pt-4 border-t border-gray-200">
                    <button
                      onClick={() => handleLike(post.id)}
                      className={`flex items-center space-x-2 ${
                        post.likes?.includes(user.id) ? 'text-red-500' : 'text-gray-600'
                      } hover:text-red-500 transition-colors`}
                    >
                      <span>{post.likes?.includes(user.id) ? '❤️' : '🤍'}</span>
                      <span>{post.likes?.length || 0}</span>
                    </button>
                    
                    <button
                      onClick={() => toggleComments(post.id)}
                      className="flex items-center space-x-2 text-gray-600 hover:text-blue-500 transition-colors"
                    >
                      <span>💬</span>
                      <span>{post.comments?.length || 0}</span>
                    </button>
                  </div>
                )}

                {/* Comments Section */}
                {showComments[post.id] && user && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="space-y-3 mb-4">
                      {comments[post.id]?.map((comment) => (
                        <div key={comment.id} className="flex space-x-3">
                          <div className="w-8 h-8 bg-gradient-to-r from-green-300 to-blue-300 rounded-full flex items-center justify-center">
                            <span className="text-white text-sm font-semibold">{comment.user_name.charAt(0).toUpperCase()}</span>
                          </div>
                          <div className="flex-1">
                            <div className="bg-gray-50 rounded-lg p-3">
                              <div className="flex items-center space-x-2 mb-1">
                                <span className="font-semibold text-gray-900 text-sm">{comment.user_name}</span>
                                <span className="text-xs text-gray-500">{formatDate(comment.created_at)}</span>
                              </div>
                              <p className="text-gray-800 text-sm">{comment.content}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                    
                    <div className="flex space-x-3">
                      <input
                        type="text"
                        value={commentForm}
                        onChange={(e) => setCommentForm(e.target.value)}
                        placeholder="Write a comment..."
                        className="flex-1 p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                        onKeyPress={(e) => e.key === 'Enter' && handleComment(post.id)}
                      />
                      <button
                        onClick={() => handleComment(post.id)}
                        className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg transition-colors"
                      >
                        Post
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {posts.length === 0 && (
            <div className="text-center py-12">
              <div className="w-24 h-24 bg-gradient-to-r from-green-200 to-blue-200 rounded-full mx-auto mb-4 flex items-center justify-center">
                <span className="text-4xl">🌟</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Welcome to REAF Community!</h3>
              <p className="text-gray-600 mb-6">Be the first to share something with the community.</p>
              {user && (
                <button
                  onClick={() => setShowCreatePost(true)}
                  className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg transition-colors"
                >
                  Create Your First Post
                </button>
              )}
            </div>
          )}
        </div>
      </main>

      {/* Auth Modal */}
      {showAuthModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">
                {authMode === 'login' ? 'Welcome Back' : 'Join Community'}
              </h2>
              <button
                onClick={() => setShowAuthModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleAuth} className="space-y-4">
              {authMode === 'register' && (
                <>
                  <input
                    type="text"
                    placeholder="Full Name"
                    value={authForm.name}
                    onChange={(e) => setAuthForm(prev => ({ ...prev, name: e.target.value }))}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    required
                  />
                  <input
                    type="text"
                    placeholder="Location (Optional)"
                    value={authForm.location}
                    onChange={(e) => setAuthForm(prev => ({ ...prev, location: e.target.value }))}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  />
                </>
              )}
              
              <input
                type="email"
                placeholder="Email"
                value={authForm.email}
                onChange={(e) => setAuthForm(prev => ({ ...prev, email: e.target.value }))}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                required
              />
              
              <input
                type="password"
                placeholder="Password"
                value={authForm.password}
                onChange={(e) => setAuthForm(prev => ({ ...prev, password: e.target.value }))}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                required
              />

              <button
                type="submit"
                className="w-full bg-green-500 hover:bg-green-600 text-white py-3 rounded-lg transition-colors font-semibold"
              >
                {authMode === 'login' ? 'Sign In' : 'Create Account'}
              </button>
            </form>

            <div className="mt-4 text-center">
              <button
                onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')}
                className="text-green-500 hover:text-green-600 transition-colors"
              >
                {authMode === 'login' ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;