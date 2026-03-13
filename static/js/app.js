const mobileInput = document.getElementById("mobileNumber");
const amountInput = document.getElementById("amount");
const message = document.getElementById("message");
const statusBox = document.getElementById("statusBox");

const mobileError = document.getElementById("mobileError");
const amountError = document.getElementById("amountError");

let paymentId = null;

const rechargeMobileRegex = /^\+\d{6,15}$/;
const rechargeAmountRegex = /^([1-9]\d(\.\d{1,2})?|100(\.0{1,2})?)$/;

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

    const cardSection = document.getElementById("cardSection");
    if (mobileValid && amountValid) {
        cardSection.style.display = "block";
    } else {
        cardSection.style.display = "none";
        if (typeof resetCaptchaState === "function") resetCaptchaState();
    }
}

mobileInput.addEventListener("input", validateInputs);
amountInput.addEventListener("input", validateInputs);
