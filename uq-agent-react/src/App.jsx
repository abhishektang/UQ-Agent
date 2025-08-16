import { useState, useEffect } from 'react';
import LoginView from './LoginView';
import ChatView from './ChatView';
import './Appstyle.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isOnUQPage, setIsOnUQPage] = useState(false);

  useEffect(() => {
    if (!chrome?.tabs || !chrome?.storage) {
      console.error('Chrome API not available');
      setIsLoading(false);
      return;
    }

    // Check current tab and auth status
    checkCurrentTabStatus();

    // Set up storage listener for auth updates
    const storageListener = (changes) => {
      if (changes.uqAuthStatus) {
        setIsLoggedIn(changes.uqAuthStatus.newValue);
      }
    };
    chrome.storage.onChanged.addListener(storageListener);

    return () => {
      chrome.storage.onChanged.removeListener(storageListener);
    };
  }, []);

  const checkCurrentTabStatus = () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const currentTab = tabs[0];
      const onUQPage = currentTab?.url?.includes('portal.my.uq.edu.au') || 
                      currentTab?.url?.includes('my.uq.edu.au');
      
      setIsOnUQPage(onUQPage);

      if (onUQPage) {
        // Get auth status from storage first for quick response
        chrome.storage.local.get(['uqAuthStatus'], (result) => {
          setIsLoggedIn(result.uqAuthStatus ?? false);
          setIsLoading(false);
        });

        // Verify with current tab
        chrome.tabs.sendMessage(
          currentTab.id, 
          { action: 'checkAuthStatus' },
          (response) => {
            if (!chrome.runtime.lastError && response) {
              const authStatus = response.isLoggedIn;
              setIsLoggedIn(authStatus);
              chrome.storage.local.set({ uqAuthStatus: authStatus });
            }
          }
        );
      } else {
        setIsLoading(false);
      }
    });
  };

  const handleLogin = () => {
    window.close();
    chrome.tabs.create({ url: 'https://auth.uq.edu.au' });
  };

  const goToDashboard = () => {
    window.close();
    chrome.tabs.create({ url: 'https://portal.my.uq.edu.au/#/dashboard' });
  };

  if (isLoading) {
    return <div className="loading">Loading UQ Agent...</div>;
  }

  return (
    <div className="app">
      {isLoggedIn ? (
        <div className="view-container">
          <ChatView />
          {!isOnUQPage && (
            <button onClick={goToDashboard} className="btn dashboard-btn">
              Go to Dashboard
            </button>
          )}
        </div>
      ) : (
        <div className="view-container">
          <LoginView onLogin={handleLogin} />
          {!isOnUQPage && (
            <button onClick={goToDashboard} className="btn dashboard-btn">
              Go to Dashboard
            </button>
          )}
        </div>
      )}
    </div>
  );
}

export default App;