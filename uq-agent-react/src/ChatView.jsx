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
import './styles.css';

export default function ChatView() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [activeChat, setActiveChat] = useState(null);
  const [username, setUsername] = useState('');
  const [authInitialized, setAuthInitialized] = useState(false);
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
  // 1. Validate basic requirements
  if (!inputValue?.trim()) {
    console.log("Message cannot be empty");
    return;
  }

  if (!username) {
    console.log("Username not set");
    return;
  }

  // 2. Ensure database connection
  if (!db) {
    console.error("Firestore not initialized");
    return;
  }

  try {
    // 3. Get or create chat ID with verification
    let targetChatId = activeChat;
    if (!targetChatId) {
      console.log("Creating new chat session...");
      targetChatId = await startNewChat(username);
      if (!targetChatId) throw new Error("Failed to create new chat");
      
      setActiveChat(targetChatId);
      await new Promise(resolve => setTimeout(resolve, 50)); // Allow state update
    }

    // 4. Verify ID format (critical for Firestore)
    if (typeof targetChatId !== 'string' || targetChatId.length < 1) {
      throw new Error(`Invalid chat ID: ${targetChatId}`);
    }

    // 5. Create document reference with validation
    const chatRef = doc(db, 'users', username, 'chats', targetChatId);
    console.log("Document reference created for:", chatRef.path);

    // 6. Get current messages with empty array fallback
    const chatSnap = await getDoc(chatRef);
    const currentMessages = chatSnap.exists() ? chatSnap.data().messages || [] : [];

    // 7. Add user message
    const userMessage = {
      text: inputValue.trim(),
      role: 'User',
    };

    await updateDoc(chatRef, {
      messages: [...currentMessages, userMessage],
      lastUpdated: serverTimestamp()
    });

    setInputValue('');

    // 8. Generate model response
    setTimeout(async () => {
      try {
        const responseText = inputValue.toLowerCase().includes('book') && 
                            inputValue.toLowerCase().includes('library room')
          ? "I can help you book a library room. Please wait while I navigate to the booking system..."
          : "I can help with various UQ tasks. Currently I support:\n- Booking library rooms\n\nTry saying 'book a library room'";

        const modelMessage = {
          text: responseText,
          role: 'Model',
        };

        // Get fresh messages to include user message
        const updatedSnap = await getDoc(chatRef);
        const updatedMessages = updatedSnap.data()?.messages || [];
        
        await updateDoc(chatRef, {
          messages: [...updatedMessages, modelMessage],
          lastUpdated: serverTimestamp()
        });

        if (responseText.includes('book a library room')) {
          bookLibraryRoom();
        }
      } catch (modelError) {
        console.error("Model response failed:", {
          error: modelError.message,
          chatId: targetChatId,
          username
        });
      }
    }, 1000);

  } catch (error) {
    console.error("Message sending failed - full diagnostics:", {
      error: error.message,
      stack: error.stack,
      activeChat,
      username,
      dbInitialized: !!db,
      authState: auth.currentUser?.uid,
      timestamp: new Date().toISOString()
    });
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
        <button onClick={startNewChat} className="new-chat-btn">
          + New Chat
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
              <h2>UQ Assistant</h2>
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
            key={index} 
            text={message.text} 
            role={message.role}  // Changed from sender to role
          />
        ))}
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
            placeholder="Message UQ Assistant..."
          />
          <button onClick={handleSendMessage} className="send-btn">
            Send
          </button>
        </div>
      </div>
    </div>
  );
}