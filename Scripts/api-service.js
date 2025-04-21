const API_BASE_URL = "https://api.example.com/v1";

const ENDPOINTS = {
  userProfile: "/users/profile",
  userPosts: "/users/posts",
  followers: "/users/followers",
  following: "/users/following",
  createPost: "/posts/create",
};

import {
  updateUserProfile,
  updatePostsGrid,
  addNewPostToUI,
} from "./ui-updates";

async function fetchUserProfile(username) {
  try {
    updateUILoadingState(true, "profile");
    console.log("inside fetch user username ", username);
    const response = await fetch(
      `${API_BASE_URL}${ENDPOINTS.userProfile}?username=${username}`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${getAuthToken()}`,
          "Content-Type": "application/json",
        },
      }
    );

    if (!response.ok) {
      throw new Error(
        `Failed to fetch profile: ${response.status} ${response.statusText}`
      );
    }

    const userData = await response.json();

    updateUserProfile(userData);

    return userData;
  } catch (error) {
    console.error("Error fetching user profile:", error);
    showErrorMessage("Failed to load profile data. Please try again later.");
    return null;
  } finally {
    updateUILoadingState(false, "profile");
  }
}

async function fetchUserPosts(username, page = 1, limit = 12) {
  try {
    updateUILoadingState(true, "posts");

    const response = await fetch(
      `${API_BASE_URL}${ENDPOINTS.userPosts}?username=${username}&page=${page}&limit=${limit}`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${getAuthToken()}`,
          "Content-Type": "application/json",
        },
      }
    );

    if (!response.ok) {
      throw new Error(
        `Failed to fetch posts: ${response.status} ${response.statusText}`
      );
    }

    const postsData = await response.json();

    updatePostsGrid(postsData.posts);

    return postsData;
  } catch (error) {
    console.error("Error fetching user posts:", error);
    showErrorMessage("Failed to load posts. Please try again later.");
    return { posts: [], totalPosts: 0, hasMore: false };
  } finally {
    updateUILoadingState(false, "posts");
  }
}

async function createNewPost(postData) {
  try {
    updateUILoadingState(true, "newPost");

    const formData = new FormData();
    formData.append("image", postData.image);
    formData.append("caption", postData.caption);

    const response = await fetch(`${API_BASE_URL}${ENDPOINTS.createPost}`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${getAuthToken()}`,
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error(
        `Failed to create post: ${response.status} ${response.statusText}`
      );
    }

    const newPostData = await response.json();

    addNewPostToUI(newPostData);

    return newPostData;
  } catch (error) {
    console.error("Error creating new post:", error);
    showErrorMessage("Failed to create post. Please try again later.");
    return null;
  } finally {
    updateUILoadingState(false, "newPost");
  }
}

async function fetchFollowers(username, page = 1, limit = 20) {
  try {
    const response = await fetch(
      `${API_BASE_URL}${ENDPOINTS.followers}?username=${username}&page=${page}&limit=${limit}`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${getAuthToken()}`,
          "Content-Type": "application/json",
        },
      }
    );

    if (!response.ok) {
      throw new Error(
        `Failed to fetch followers: ${response.status} ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    console.error("Error fetching followers:", error);
    showErrorMessage("Failed to load followers. Please try again later.");
    return { followers: [], totalFollowers: 0, hasMore: false };
  }
}

async function fetchFollowing(username, page = 1, limit = 20) {
  try {
    const response = await fetch(
      `${API_BASE_URL}${ENDPOINTS.following}?username=${username}&page=${page}&limit=${limit}`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${getAuthToken()}`,
          "Content-Type": "application/json",
        },
      }
    );

    if (!response.ok) {
      throw new Error(
        `Failed to fetch following: ${response.status} ${response.statusText}`
      );
    }

    return await response.json();
  } catch (error) {
    console.error("Error fetching following:", error);
    showErrorMessage("Failed to load following. Please try again later.");
    return { following: [], totalFollowing: 0, hasMore: false };
  }
}

function getAuthToken() {
  return localStorage.getItem("authToken") || "";
}

function updateUILoadingState(isLoading, section) {
  const loadingElement = document.getElementById(`${section}-loading`);
  if (loadingElement) {
    loadingElement.style.display = isLoading ? "block" : "none";
  }
}

function showErrorMessage(message) {
  const errorContainer = document.getElementById("error-container");
  if (errorContainer) {
    errorContainer.textContent = message;
    errorContainer.style.display = "block";

    setTimeout(() => {
      errorContainer.style.display = "none";
    }, 5000);
  } else {
    alert(message);
  }
}

export {
  fetchUserProfile,
  fetchUserPosts,
  createNewPost,
  fetchFollowers,
  fetchFollowing,
};
