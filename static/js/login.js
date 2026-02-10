document.getElementById("loginForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const errorMsg = document.getElementById("error-message");
    const loginBtn = document.querySelector(".login-btn");

    errorMsg.textContent = "";

    if (!username || !password) {
        errorMsg.textContent = "Please enter both username and password.";
        return;
    }

    loginBtn.disabled = true;
    loginBtn.textContent = "Authenticating...";

    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok && data.status === "success") {
            window.location.href = "/admin/dashboard";
        } else {
            errorMsg.textContent = data.error || "Login failed. Please try again.";
            loginBtn.disabled = false;
            loginBtn.textContent = "Login";
        }
    } catch (err) {
        errorMsg.textContent = "Network error. Please try again.";
        loginBtn.disabled = false;
        loginBtn.textContent = "Login";
    }
});
