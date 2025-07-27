#!/usr/bin/env python3
"""
Backend API Testing for Ricky East African Foundation Social Media App
Tests all high-priority backend features including authentication, posts, and social interactions.
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = "https://c8d8b0f5-0656-4ac4-b266-9d63f544d487.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_data = None
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        
    def log_result(self, test_name, success, message="", response=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        if response and not success:
            print(f"   Response: {response.status_code} - {response.text[:200]}")
        
        if success:
            self.test_results["passed"] += 1
        else:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {message}")
        print()

    def test_user_registration(self):
        """Test user registration endpoint"""
        print("🔐 Testing User Registration...")
        
        user_data = {
            "email": "amara.kiprotich@gmail.com",
            "password": "SecurePass123!",
            "name": "Amara Kiprotich",
            "location": "Nairobi, Kenya",
            "bio": "Youth advocate passionate about community development and health education"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/auth/register", json=user_data)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.auth_token = data["token"]
                    self.user_data = data["user"]
                    self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                    self.log_result("User Registration", True, f"User {data['user']['name']} registered successfully")
                    return True
                else:
                    self.log_result("User Registration", False, "Missing token or user in response", response)
            else:
                self.log_result("User Registration", False, f"Registration failed with status {response.status_code}", response)
                
        except Exception as e:
            self.log_result("User Registration", False, f"Exception: {str(e)}")
            
        return False

    def test_user_login(self):
        """Test user login endpoint"""
        print("🔑 Testing User Login...")
        
        # First register a user for login test
        login_user = {
            "email": "kwame.asante@gmail.com", 
            "password": "LoginTest456!",
            "name": "Kwame Asante",
            "location": "Accra, Ghana",
            "bio": "Entrepreneur focused on youth empowerment and sustainable development"
        }
        
        try:
            # Register user first
            reg_response = self.session.post(f"{self.base_url}/auth/register", json=login_user)
            if reg_response.status_code != 200:
                self.log_result("User Login (Setup)", False, "Failed to register test user for login", reg_response)
                return False
                
            # Now test login
            login_data = {
                "email": login_user["email"],
                "password": login_user["password"]
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "token" in data and "user" in data:
                    self.log_result("User Login", True, f"User {data['user']['name']} logged in successfully")
                    return True
                else:
                    self.log_result("User Login", False, "Missing token or user in response", response)
            else:
                self.log_result("User Login", False, f"Login failed with status {response.status_code}", response)
                
        except Exception as e:
            self.log_result("User Login", False, f"Exception: {str(e)}")
            
        return False

    def test_get_user_profile(self):
        """Test getting current user profile"""
        print("👤 Testing Get User Profile...")
        
        if not self.auth_token:
            self.log_result("Get User Profile", False, "No auth token available")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/users/me")
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "email" in data and "name" in data:
                    self.log_result("Get User Profile", True, f"Retrieved profile for {data['name']}")
                    return True
                else:
                    self.log_result("Get User Profile", False, "Missing required fields in profile", response)
            else:
                self.log_result("Get User Profile", False, f"Failed with status {response.status_code}", response)
                
        except Exception as e:
            self.log_result("Get User Profile", False, f"Exception: {str(e)}")
            
        return False

    def test_update_user_profile(self):
        """Test updating user profile"""
        print("✏️ Testing Update User Profile...")
        
        if not self.auth_token:
            self.log_result("Update User Profile", False, "No auth token available")
            return False
            
        update_data = {
            "bio": "Updated: Community health advocate and youth mentor in East Africa",
            "skills": ["Community Outreach", "Health Education", "Youth Mentoring"],
            "interests": ["Public Health", "Youth Development", "Community Building"]
        }
        
        try:
            response = self.session.put(f"{self.base_url}/users/me", json=update_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("bio") == update_data["bio"]:
                    self.log_result("Update User Profile", True, "Profile updated successfully")
                    return True
                else:
                    self.log_result("Update User Profile", False, "Profile not updated correctly", response)
            else:
                self.log_result("Update User Profile", False, f"Failed with status {response.status_code}", response)
                
        except Exception as e:
            self.log_result("Update User Profile", False, f"Exception: {str(e)}")
            
        return False

    def test_create_post(self):
        """Test creating posts with different categories"""
        print("📝 Testing Post Creation...")
        
        if not self.auth_token:
            self.log_result("Create Post", False, "No auth token available")
            return False
            
        test_posts = [
            {
                "content": "Excited to share our latest health education workshop in Kampala! We reached over 200 young people with vital information about nutrition and wellness. #HealthEducation #YouthEmpowerment",
                "category": "health"
            },
            {
                "content": "Congratulations to our entrepreneurship program graduates! 15 young entrepreneurs just launched their businesses with our support. The future of East Africa is bright! 🌟",
                "category": "entrepreneurship"
            },
            {
                "content": "Join us this Saturday for our community sports day! Football, netball, and athletics for all ages. Building stronger communities through sports! ⚽🏃‍♀️",
                "category": "sports"
            }
        ]
        
        created_posts = []
        
        for i, post_data in enumerate(test_posts):
            try:
                response = self.session.post(f"{self.base_url}/posts", json=post_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if "id" in data and data.get("category") == post_data["category"]:
                        created_posts.append(data)
                        self.log_result(f"Create Post ({post_data['category']})", True, f"Post created with ID: {data['id']}")
                    else:
                        self.log_result(f"Create Post ({post_data['category']})", False, "Invalid post data returned", response)
                else:
                    self.log_result(f"Create Post ({post_data['category']})", False, f"Failed with status {response.status_code}", response)
                    
            except Exception as e:
                self.log_result(f"Create Post ({post_data['category']})", False, f"Exception: {str(e)}")
        
        self.created_posts = created_posts
        return len(created_posts) > 0

    def test_get_posts(self):
        """Test retrieving posts"""
        print("📋 Testing Get Posts...")
        
        try:
            response = self.session.get(f"{self.base_url}/posts")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get Posts", True, f"Retrieved {len(data)} posts")
                    return True
                else:
                    self.log_result("Get Posts", False, "Response is not a list", response)
            else:
                self.log_result("Get Posts", False, f"Failed with status {response.status_code}", response)
                
        except Exception as e:
            self.log_result("Get Posts", False, f"Exception: {str(e)}")
            
        return False

    def test_like_post(self):
        """Test liking and unliking posts"""
        print("❤️ Testing Post Likes...")
        
        if not self.auth_token:
            self.log_result("Like Post", False, "No auth token available")
            return False
            
        if not hasattr(self, 'created_posts') or not self.created_posts:
            self.log_result("Like Post", False, "No posts available to like")
            return False
            
        post_id = self.created_posts[0]["id"]
        
        try:
            # Test liking a post
            response = self.session.post(f"{self.base_url}/posts/{post_id}/like")
            
            if response.status_code == 200:
                data = response.json()
                if "liked" in data and "count" in data:
                    liked_status = data["liked"]
                    like_count = data["count"]
                    
                    # Test unliking the same post
                    response2 = self.session.post(f"{self.base_url}/posts/{post_id}/like")
                    if response2.status_code == 200:
                        data2 = response2.json()
                        if data2["liked"] != liked_status:
                            self.log_result("Like/Unlike Post", True, f"Like toggle working correctly")
                            return True
                        else:
                            self.log_result("Like/Unlike Post", False, "Like toggle not working", response2)
                    else:
                        self.log_result("Like/Unlike Post", False, f"Unlike failed with status {response2.status_code}", response2)
                else:
                    self.log_result("Like Post", False, "Missing liked/count in response", response)
            else:
                self.log_result("Like Post", False, f"Failed with status {response.status_code}", response)
                
        except Exception as e:
            self.log_result("Like Post", False, f"Exception: {str(e)}")
            
        return False

    def test_create_comment(self):
        """Test creating comments on posts"""
        print("💬 Testing Comment Creation...")
        
        if not self.auth_token:
            self.log_result("Create Comment", False, "No auth token available")
            return False
            
        if not hasattr(self, 'created_posts') or not self.created_posts:
            self.log_result("Create Comment", False, "No posts available to comment on")
            return False
            
        post_id = self.created_posts[0]["id"]
        comment_data = {
            "post_id": post_id,
            "content": "This is such an inspiring initiative! Keep up the great work in empowering our youth. 👏"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/comments", json=comment_data)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data.get("post_id") == post_id:
                    self.comment_id = data["id"]
                    self.log_result("Create Comment", True, f"Comment created with ID: {data['id']}")
                    return True
                else:
                    self.log_result("Create Comment", False, "Invalid comment data returned", response)
            else:
                self.log_result("Create Comment", False, f"Failed with status {response.status_code}", response)
                
        except Exception as e:
            self.log_result("Create Comment", False, f"Exception: {str(e)}")
            
        return False

    def test_get_post_comments(self):
        """Test retrieving comments for a post"""
        print("📖 Testing Get Post Comments...")
        
        if not hasattr(self, 'created_posts') or not self.created_posts:
            self.log_result("Get Post Comments", False, "No posts available")
            return False
            
        post_id = self.created_posts[0]["id"]
        
        try:
            response = self.session.get(f"{self.base_url}/posts/{post_id}/comments")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get Post Comments", True, f"Retrieved {len(data)} comments for post")
                    return True
                else:
                    self.log_result("Get Post Comments", False, "Response is not a list", response)
            else:
                self.log_result("Get Post Comments", False, f"Failed with status {response.status_code}", response)
                
        except Exception as e:
            self.log_result("Get Post Comments", False, f"Exception: {str(e)}")
            
        return False

    def run_all_tests(self):
        """Run all backend tests in sequence"""
        print("🚀 Starting Backend API Tests for Ricky East African Foundation Social Media App")
        print("=" * 80)
        
        # Test authentication system
        self.test_user_registration()
        self.test_user_login()
        
        # Test user profile management
        self.test_get_user_profile()
        self.test_update_user_profile()
        
        # Test posts CRUD system
        self.test_create_post()
        self.test_get_posts()
        
        # Test social interactions
        self.test_like_post()
        self.test_create_comment()
        self.test_get_post_comments()
        
        # Print summary
        print("=" * 80)
        print("🏁 TEST SUMMARY")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📊 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            print("\n🚨 FAILED TESTS:")
            for error in self.test_results['errors']:
                print(f"   • {error}")
        
        return self.test_results['failed'] == 0

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)