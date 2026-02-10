const modal = document.getElementById("profileModal");
const errorMsg = document.getElementById("profileError");

const mobileStep = document.getElementById("mobileStep");
const profileStep = document.getElementById("profileStep");

const continueBtn = document.getElementById("continueBtn");
const createBtn = document.getElementById("createProfileBtn");

const modalTitle = document.getElementById("modalTitle");

const profileMobileInput = document.getElementById("profileMobile");
const firstNameInput = document.getElementById("firstName");
const lastNameInput = document.getElementById("lastName");
const emailInput = document.getElementById("email");

const nameRegex = /^[A-Za-z]{1,100}$/;
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const mobileRegex = /^\+[0-9]{10,15}$|^[0-9]{10,15}$/;

// Show modal on load
document.addEventListener("DOMContentLoaded", () => {
  modal.style.display = "block";
});

// STEP 1: Check mobile
continueBtn.addEventListener("click", async () => {
  const mobile = profileMobileInput.value.trim();
  errorMsg.textContent = "";

  if (!mobileRegex.test(mobile)) {
    errorMsg.textContent = "Enter a valid mobile number";
    return;
  }

  const res = await fetch(`/check-mobile?mobile=${mobile}`);
  const data = await res.json();

  if (data.exists) {
    // ✅ Existing user → skip profile
    modal.style.display = "none";
  } else {
    // ❗ New user → show profile form
    modalTitle.innerText = "Create Profile";
    mobileStep.style.display = "none";
    profileStep.style.display = "block";
    continueBtn.style.display = "none";
    createBtn.style.display = "block";
  }
});

// STEP 2: Create profile
createBtn.addEventListener("click", async () => {
  const firstName = firstNameInput.value.trim();
  const lastName = lastNameInput.value.trim();
  const email = emailInput.value.trim();
  const mobile = profileMobileInput.value.trim();

  errorMsg.textContent = "";

  if (!firstName || !lastName || !email) {
    errorMsg.textContent = "All fields are required";
    return;
  }

  if (!nameRegex.test(firstName)) {
    errorMsg.textContent = "Invalid first name";
    return;
  }

  if (!nameRegex.test(lastName)) {
    errorMsg.textContent = "Invalid last name";
    return;
  }

  if (!emailRegex.test(email)) {
    errorMsg.textContent = "Invalid email address";
    return;
  }

  const res = await fetch("/create-profile", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      firstName,
      lastName,
      email,
      mobile
    })
  });

  const data = await res.json();

  if (data.status === "success") {
    modal.style.display = "none";
  } else {
    errorMsg.textContent = "Profile creation failed";
  }
});
