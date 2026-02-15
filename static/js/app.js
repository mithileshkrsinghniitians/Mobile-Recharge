const mobileInput = document.getElementById("mobileNumber");
const amountInput = document.getElementById("amount");
const initiateBtn = document.getElementById("initiateBtn");
const message = document.getElementById("message");
const statusBox = document.getElementById("statusBox");

const mobileError = document.getElementById("mobileError");
const amountError = document.getElementById("amountError");

let paymentId = null;

// Regex rules (prefixed to avoid conflict with profile.js):
const rechargeMobileRegex = /^\+\d{6,15}$/;
const rechargeAmountRegex = /^(10|[1-9]\d|100)$/;

// Validate inputs with messages:
function validateInputs() {
    let mobileValid = false;
    let amountValid = false;

    if (!mobileInput.value) {
        mobileError.innerText = "";
    } else if (rechargeMobileRegex.test(mobileInput.value)) {
        mobileError.innerText = "";
        mobileValid = true;
    } else {
        mobileError.innerText =
            "Enter valid mobile number with country code (e.g. +353...)";
    }

    if (!amountInput.value) {
        amountError.innerText = "";
    } else if (rechargeAmountRegex.test(amountInput.value)) {
        amountError.innerText = "";
        amountValid = true;
    } else {
        amountError.innerText = "Amount must be between 10 and 100";
    }

    initiateBtn.disabled = !(mobileValid && amountValid);
}

mobileInput.addEventListener("input", validateInputs);
amountInput.addEventListener("input", validateInputs);
