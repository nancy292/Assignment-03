import {
  fetchUserProfile,
  fetchUserPosts,
  createNewPost,
  fetchFollowers,
  fetchFollowing,
} from "./api-service.js";

const postsGrid = document.getElementById("posts-grid");
const postModal = document.getElementById("post-modal");
const createPostBtn = document.getElementById("create-post-btn");
const closeModalBtn = document.querySelector(".close-modal");
const newPostForm = document.getElementById("new-post-form");
const postImageInput = document.getElementById("post-image");
const imagePreview = document.getElementById("image-preview");
const postCaptionInput = document.getElementById("post-caption");

let currentUser = null;
let currentPosts = [];
let currentPage = 1;
const postsPerPage = 12;
let hasMorePosts = true;

function addLoadingIndicators() {
  const profileLoading = document.createElement("div");
  profileLoading.id = "profile-loading";
  profileLoading.className = "loading-indicator";
  profileLoading.innerHTML = "Loading profile...";
  profileLoading.style.display = "none";
  document.querySelector(".profile-header").appendChild(profileLoading);

  const postsLoading = document.createElement("div");
  postsLoading.id = "posts-loading";
  postsLoading.className = "loading-indicator";
  postsLoading.innerHTML = "Loading posts...";
  postsLoading.style.display = "none";
  document.querySelector(".posts-container").prepend(postsLoading);

  const newPostLoading = document.createElement("div");
  newPostLoading.id = "newPost-loading";
  newPostLoading.className = "loading-indicator";
  newPostLoading.innerHTML = "Creating post...";
  newPostLoading.style.display = "none";
  document.querySelector(".modal-body").appendChild(newPostLoading);

  const errorContainer = document.createElement("div");
  errorContainer.id = "error-container";
  errorContainer.className = "error-message";
  errorContainer.style.display = "none";
  document.querySelector(".container").prepend(errorContainer);
}

async function initializeApp() {
  addLoadingIndicators();

  const urlParams = new URLSearchParams(window.location.search);
  const username = urlParams.get("username") || "john_doe";

  currentUser = await fetchUserProfile(username);

  if (currentUser) {
    const postsData = await fetchUserPosts(username, currentPage, postsPerPage);
    if (postsData) {
      currentPosts = postsData.posts;
      hasMorePosts = postsData.hasMore;
      renderPosts();
    }
  }

  window.addEventListener("scroll", handleScroll);
}

function updateUserProfile(userData) {
  document.querySelector(".username").textContent = userData.username;
  document.querySelector(".full-name").textContent = userData.fullName;
  document.querySelector(".bio").textContent = userData.bio;
  document.querySelector(".profile-image img").src = userData.profileImage;
  document.getElementById("posts-count").textContent = userData.stats.posts;
  document.getElementById("followers-count").textContent =
    userData.stats.followers;
  document.getElementById("following-count").textContent =
    userData.stats.following;
}

function renderPosts() {
  if (currentPage === 1) {
    postsGrid.innerHTML = "";
  }

  currentPosts.forEach((post) => {
    const postElement = document.createElement("div");
    postElement.className = "post-card";
    postElement.innerHTML = `
        <img src="${post.imageUrl}" alt="Post" class="post-image">
        <div class="post-caption">
          <p>${post.caption}</p>
        </div>
      `;
    postsGrid.appendChild(postElement);
  });

  if (hasMorePosts) {
    const loadMoreBtn =
      document.getElementById("load-more-btn") ||
      document.createElement("button");
    loadMoreBtn.id = "load-more-btn";
    loadMoreBtn.className = "load-more-btn";
    loadMoreBtn.textContent = "Load More";
    loadMoreBtn.onclick = loadMorePosts;

    if (!document.getElementById("load-more-btn")) {
      document.querySelector(".posts-container").appendChild(loadMoreBtn);
    }
  } else {
    const loadMoreBtn = document.getElementById("load-more-btn");
    if (loadMoreBtn) {
      loadMoreBtn.remove();
    }
  }
}

function addNewPostToUI(newPost) {
  currentPosts.unshift(newPost);

  if (currentUser) {
    currentUser.stats.posts++;
    document.getElementById("posts-count").textContent =
      currentUser.stats.posts;
  }

  renderPosts();
}

async function loadMorePosts() {
  if (!hasMorePosts) return;

  currentPage++;
  const username = currentUser
    ? currentUser.username.replace("@", "")
    : "john_doe";
  const postsData = await fetchUserPosts(username, currentPage, postsPerPage);

  if (postsData) {
    currentPosts = [...currentPosts, ...postsData.posts];
    hasMorePosts = postsData.hasMore;
    renderPosts();
  }
}

function handleScroll() {
  if (!hasMorePosts) return;

  const scrollY = window.scrollY;
  const windowHeight = window.innerHeight;
  const documentHeight = document.documentElement.scrollHeight;

  if (scrollY + windowHeight >= documentHeight - 300) {
    loadMorePosts();
  }
}

createPostBtn.addEventListener("click", () => {
  postModal.style.display = "block";
  document.body.style.overflow = "hidden";
});

closeModalBtn.addEventListener("click", () => {
  postModal.style.display = "none";
  document.body.style.overflow = "";

  newPostForm.reset();
  imagePreview.innerHTML = "";
});

window.addEventListener("click", (event) => {
  if (event.target === postModal) {
    postModal.style.display = "none";
    document.body.style.overflow = "";
    newPostForm.reset();
    imagePreview.innerHTML = "";
  }
});

postImageInput.addEventListener("change", (event) => {
  const file = event.target.files[0];

  if (file) {
    const validTypes = ["image/jpeg", "image/jpg", "image/png"];
    if (!validTypes.includes(file.type)) {
      alert("Please select a PNG or JPG image file.");
      postImageInput.value = "";
      imagePreview.innerHTML = "";
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
    };
    reader.readAsDataURL(file);
  } else {
    imagePreview.innerHTML = "";
  }
});

newPostForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const file = postImageInput.files[0];
  const caption = postCaptionInput.value;

  if (!file || !caption) {
    alert("Please upload an image and write a caption.");
    return;
  }

  const postData = {
    image: file,
    caption: caption,
  };

  const newPost = await createNewPost(postData);

  if (newPost) {
    postModal.style.display = "none";
    document.body.style.overflow = "";
    newPostForm.reset();
    imagePreview.innerHTML = "";
  }
});

document.addEventListener("DOMContentLoaded", initializeApp);
