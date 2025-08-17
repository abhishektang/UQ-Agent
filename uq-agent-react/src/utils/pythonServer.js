export async function executePythonScript(prompt) {
  try {
    const response = await fetch('http://localhost:3001', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        prompt,
        currentUrl: window.location.href  // Send context if needed
      }),
    });
    
    const data = await response.json();
    
    if (data.status === "error") {
      throw new Error(data.message);
    }
    
    return data;
  } catch (error) {
    console.error('Python server error:', error);
    return {
      status: "error",
      message: "Sorry, I couldn't process that request. The automation service might be unavailable."
    };
  }
}