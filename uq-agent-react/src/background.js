// Background script for future functionality
chrome.runtime.onInstalled.addListener(() => {
  console.log('UQ Agent extension installed')
})

let pythonProcess = null;

chrome.runtime.onStartup.addListener(() => {
  startPythonServer();
});

chrome.runtime.onInstalled.addListener(() => {
  startPythonServer();
});

function startPythonServer() {
  // This would require Native Messaging
  // For actual implementation, you'll need a companion app
  console.log('Python server should be started here');
}

// Fallback - check server status periodically
setInterval(() => {
  fetch('http://localhost:3001/health')
    .catch(() => console.warn('Python server not responding'));
}, 30000);