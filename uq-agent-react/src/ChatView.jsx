import { useState, useRef, useEffect } from 'react';
import { db, auth, initAuth } from '../FirebaseConfig';
import { 
  collection, 
  addDoc, 
  serverTimestamp, 
  query, 
  where, 
  onSnapshot, 
  doc, 
  setDoc, 
  getDoc,
  updateDoc,
  orderBy  // Add this import
} from 'firebase/firestore';
import Message from './Message';
import { executePythonScript } from '../src/utils/pythonServer';
import './ChatViewstyle.css';

export default function ChatView() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [activeChat, setActiveChat] = useState(null);
  const [username, setUsername] = useState('');
  const [authInitialized, setAuthInitialized] = useState(false);
  const [creatingChat, setCreatingChat] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef(null);

  // Get username from dashboard
  // Initialize authentication and user data
  useEffect(() => {
    const initialize = async () => {
      try {
        // 1. Initialize Firebase Auth
        await initAuth();
        setAuthInitialized(true);

        // 2. Get username from dashboard
        chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
          const currentTab = tabs[0];
          if (currentTab?.url?.includes('portal.my.uq.edu.au')) {
            chrome.scripting.executeScript({
              target: { tabId: currentTab.id },
              func: () => {
                const userElement = document.querySelector('.page__header-user-name');
                return userElement?.textContent?.trim() || 'Anonymous';
              },
            }, async (results) => {
              if (!chrome.runtime.lastError && results?.[0]?.result) {
                const username = results[0].result;
                setUsername(username);
                
                // 3. Initialize user chats after auth and username are ready
                await initializeUserChats(username);
              }
            });
          }
        });
      } catch (error) {
        console.error("Initialization error:", error);
      }
    };

    initialize();
  }, []);

  useEffect(() => {
  let unsubscribe = () => {};

  if (activeChat && username) {
    const chatRef = doc(db, 'users', username, 'chats', activeChat);
    
    unsubscribe = onSnapshot(chatRef, (doc) => {
      if (doc.exists()) {
        setMessages(doc.data().messages || []);
        // Auto-scroll to bottom when new messages arrive
        setTimeout(() => {
          messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        }, 100);
      }
    });
  }

  return () => unsubscribe();
}, [activeChat, username]);

  // Initialize user's chat structure
  const initializeUserChats = async (username) => {
    if (!auth.currentUser) {
      console.error("User not authenticated - retrying...");
      await initAuth(); // Retry authentication
      if (!auth.currentUser) throw new Error("Authentication failed");
    }

    const userDocRef = doc(db, 'users', username);
    
    try {
      const docSnap = await getDoc(userDocRef);
      if (!docSnap.exists()) {
        await setDoc(userDocRef, {
          createdAt: serverTimestamp(),
          lastActive: serverTimestamp(),
          uid: auth.currentUser.uid // Store the Firebase UID
        });
      }
      loadChatHistory(username);
    } catch (error) {
      console.error("Error initializing user:", error);
    }
  };

  // Create a new chat session
  const startNewChat = async (username) => {
  try {
    const newChatRef = doc(collection(db, 'users', username, 'chats'));
    await setDoc(newChatRef, {
      createdAt: serverTimestamp(),
      lastUpdated: serverTimestamp(),
      messages: []
    });
    console.log("Created new chat with ID:", newChatRef.id);
    return newChatRef.id; // THIS IS CRUCIAL
  } catch (error) {
    console.error("Failed to create new chat:", error);
    throw error; // Re-throw to handle in calling function
  }
};

  // Load a specific chat
  const loadChat = async (chatId) => {
    if (!username) return;
    
    try {
      const chatDocRef = doc(db, 'users', username, 'chats', chatId);
      const chatSnap = await getDoc(chatDocRef);
      
      if (chatSnap.exists()) {
        setMessages(chatSnap.data().messages || []);
        setActiveChat(chatId);
      }
    } catch (error) {
      console.error("Error loading chat:", error);
    }
  };

   const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  // Send a new message
  const handleSendMessage = async () => {
   if (!inputValue.trim() || !username) return;

  setIsSending(true);
  try {
    // Optimistic UI update - show message immediately
    const userMessage = {
      text: inputValue.trim(),
      role: 'User',
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    
    // Scroll to bottom after optimistically adding message
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 50);

    let targetChatId = activeChat;
    if (!targetChatId) {
      targetChatId = await startNewChat(username);
      setActiveChat(targetChatId);
    }

    const chatRef = doc(db, 'users', username, 'chats', targetChatId);
    const chatSnap = await getDoc(chatRef);
    const currentMessages = chatSnap.exists() ? chatSnap.data().messages || [] : [];

    // Update Firestore with user message
    await updateDoc(chatRef, {
      messages: [...currentMessages, userMessage],
      lastUpdated: serverTimestamp()
    });

    // Generate and add model response
    let responseText;
    try {
      // Show a temporary "processing" message
      setMessages(prev => [...prev, {
        text: "Processing your request...",
        role: 'Model'
      }]);
      
      // Send the entire prompt to Python backend
      const response = await executePythonScript(inputValue.trim());
      console.log("Python response:", response.message);
      responseText = response.message || "I've processed your request";
      
      // Remove the temporary message
      setMessages(prev => prev.filter(msg => msg.text !== "Processing your request..."));
    } catch (error) {
      responseText = "Sorry, I couldn't process that request. Please try again.";
      console.error("Processing error:", error);
    }

    const modelMessage = {
      text: responseText,
      role: 'Model',
    };

    // Add model response optimistically
    setMessages(prev => [...prev, modelMessage]);
    
    // Update Firestore with model response
    await updateDoc(chatRef, {
      messages: [...currentMessages, userMessage, modelMessage],
      lastUpdated: serverTimestamp()
    });

    // Scroll to bottom after model response
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  } catch (error) {
    console.error("Error sending message:", error);
    // Rollback optimistic update if there's an error
    setMessages(prev => prev.filter(msg => msg.text !== inputValue.trim()));
  }
  finally {
  setIsSending(false);
}
};

const handleNewChat = async () => {
  try {
    // 1. Show loading state
    setCreatingChat(true);
    
    // 2. Verify user is authenticated
    if (!auth.currentUser) {
      await initAuth();
    }

    // 3. Ensure username exists
    if (!username) {
      const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
      const currentTab = tabs[0];
      if (currentTab?.url?.includes('portal.my.uq.edu.au')) {
        const results = await chrome.scripting.executeScript({
          target: { tabId: currentTab.id },
          func: () => document.querySelector('.page__header-user-name')?.textContent?.trim() || 'Anonymous'
        });
        setUsername(results[0]?.result || 'Anonymous');
      }
    }

    // 4. Create new chat
    const newChatId = await startNewChat(username || 'Anonymous');
    setActiveChat(newChatId);
    setMessages([]);

  } catch (error) {
    console.error('Failed to create new chat:', {
      error: error.message,
      username,
      authState: auth.currentUser?.uid
    });
    // Show error to user
    alert('Failed to create new chat. Please try again.');
  } finally {
    setCreatingChat(false);
  }
};

  // Load chat history for the user
  const loadChatHistory = (username) => {
    const chatsCollectionRef = collection(db, 'users', username, 'chats');
    const q = query(chatsCollectionRef, orderBy('lastUpdated', 'desc'));
    
    const unsubscribe = onSnapshot(q, (querySnapshot) => {
      const chats = [];
      querySnapshot.forEach((doc) => {
        chats.push({ 
          id: doc.id, 
          ...doc.data(),
          // Get first message as preview
          preview: doc.data().messages?.[0]?.text || 'New chat'
        });
      });
      setChatHistory(chats);
    });

    return unsubscribe;
  };


  return (
    <div className="chat-interface">
      {/* Sidebar */}
      <div className="chat-sidebar">
        <button 
  onClick={handleNewChat}
  disabled={creatingChat}
  className="new-chat-btn"
>
  {creatingChat ? (
    <>
      <span className="spinner"></span> Creating...
    </>
  ) : (
    '+ New Chat'
  )}
</button>
        <div className="chat-history">
          <h3>Chat History</h3>
          {chatHistory.map((chat) => (
            <div 
              key={chat.id}
              className={`history-item ${activeChat === chat.id ? 'active' : ''}`}
              onClick={() => loadChat(chat.id)}
            >
              {chat.preview.substring(0, 30)}...
              <span className="chat-date">
                {chat.lastUpdated?.toDate().toLocaleString()}
              </span>
            </div>
          ))}
        </div>
        <div className="user-info">
          <span>{username || 'Loading...'}</span>
        </div>
      </div>

            {/* Main Chat Area */}
      <div className="main-chat-area">
        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="welcome-message">
              <h2>UQ Agent</h2>
              <p>How can I help you today?</p>
              <div className="suggestions">
                <button onClick={() => setInputValue('How do I book a library room?')}>
                  Book a library room
                </button>
                <button onClick={() => setInputValue('Where is my next class?')}>
                  Find my next class
                </button>
              </div>
            </div>
          ) : (
            <div className="messages-container">
            {messages.map((message, index) => (
                <Message 
                key={`${message.role}-${index}-${message.text.substring(0, 5)}`} 
                text={message.text} 
                role={message.role}
                />
            ))}
            <div ref={messagesEndRef} />
            </div>
    )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-container">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Message UQ Agent..."
          />
          <button 
            onClick={handleSendMessage} 
            className="send-btn"
            disabled={isSending}
            >
            {isSending ? 'Sending...' : 'Send'}
            </button>
        </div>
      </div>
    </div>
  );
}