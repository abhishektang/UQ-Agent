// contentScript.js


function clickLoginButton() {
  const loginButton = document.querySelector('[aria-label="Log in?"]');
  if (loginButton) {
    loginButton.click();
    return true;
  }
  return false;
}

function checkAuthByAriaLabel() {
  // Check for logout button first (more reliable)
  const logoutButton = document.querySelector('[aria-label="Log out"]');
  if (logoutButton) return true;
  
  // Fallback to check for login button
  const loginButton = document.querySelector('[aria-label="Log in"]');
  return !loginButton; // If login button exists, user is logged out
}

// Update storage with current auth status
function updateAuthStatus() {
  const isLoggedIn = checkAuthByAriaLabel();
  chrome.storage.local.set({ uqAuthStatus: isLoggedIn });
}

// Initial check
updateAuthStatus();

// Watch for DOM changes
const observer = new MutationObserver(updateAuthStatus);
observer.observe(document.body, {
  childList: true,
  subtree: true,
  attributes: true,
  attributeFilter: ['aria-label']
});

// Optional: Listen for manual status checks
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "checkAuthStatus") {
    sendResponse({ isLoggedIn: checkAuthByAriaLabel() });
  }
  if (request.action === "clickLoginButton") {
    const success = clickLoginButton();
    sendResponse({ success });
  }
});