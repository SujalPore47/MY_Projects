// src/utils/api.js

// --- Configuration ---
// Determine the base URL for the API.
// Use the environment variable if available, otherwise default to localhost.
// Remove any trailing slash from the base URL to prevent double slashes.
const API_BASE_URL = (process.env.REACT_APP_API_URL || 'http://localhost:8000').replace(/\/$/, '');

// Construct the full URLs for the endpoints
const ANALYZE_FOOD_URL = `${API_BASE_URL}/analyze-food`;
const CHAT_BOT_URL = `${API_BASE_URL}/chat-bot`;

// --- API Functions ---

/**
 * Sends an image file to the backend for food analysis.
 * @param {File} file - The image file object to upload.
 * @returns {Promise<object>} A promise that resolves with the JSON analysis results from the backend.
 * @throws {Error} Throws an error if the fetch request fails, the server response is not OK,
 *                 or the response body cannot be parsed as JSON.
 */
export const analyzeImage = async (file) => {
  const formData = new FormData();
  formData.append('image', file); // Ensure the key 'image' matches the backend expectation

  console.log(`Sending image analysis request to: ${ANALYZE_FOOD_URL}`); // Optional: for debugging

  try {
    const response = await fetch(ANALYZE_FOOD_URL, {
      method: 'POST',
      body: formData,
      // Note: 'Content-Type' for FormData is set automatically by the browser
    });

    // Check if the HTTP response status code indicates success (e.g., 2xx)
    if (!response.ok) {
      let errorData = { detail: `Image analysis failed with status: ${response.status}` };
      try {
        // Try to get more specific error details from the response body
        errorData = await response.json();
      } catch (parseError) {
        // If the error response isn't valid JSON, log it but use the status text
        console.error("Could not parse error response JSON:", parseError);
        errorData.detail = response.statusText || errorData.detail;
      }
      // Throw an error using the detail from the backend if available
      throw new Error(errorData.detail || 'Image analysis upload failed');
    }

    // If the response is OK, parse the JSON body
    try {
      const data = await response.json();
      return data;
    } catch (jsonError) {
      console.error("Failed to parse successful JSON response from /analyze-food:", jsonError);
      throw new Error("Received invalid JSON data from image analysis endpoint.");
    }

  } catch (networkError) {
    // Catch network errors (e.g., server down, DNS issues) or errors thrown above
    console.error('Error during analyzeImage fetch:', networkError);
    // Re-throw the error so the calling component can handle it
    // Ensure it's an Error object
    throw networkError instanceof Error ? networkError : new Error('A network error occurred during image analysis.');
  }
};

/**
 * Sends a user query and optional chat history to the chat bot endpoint.
 * @param {string} query - The user's current question or message.
 * @param {string} [chatHistory=""] - A string representing the recent conversation history.
 * @returns {Promise<object>} A promise that resolves with the JSON response from the chat bot (expected format: { response: "..." }).
 * @throws {Error} Throws an error if the fetch request fails, the server response is not OK,
 *                 or the response body cannot be parsed as JSON.
 */
export const sendQuery = async (query, chatHistory = "") => {
  const payload = {
    query,
    chat_history: chatHistory,
  };

  console.log(`Sending chat query to: ${CHAT_BOT_URL} with payload:`, payload); // Optional: for debugging

  try {
    const response = await fetch(CHAT_BOT_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // You can add other headers like 'Accept' or 'Authorization' if needed
        "Accept": "application/json",
      },
      body: JSON.stringify(payload),
    });

    // Check if the HTTP response status code indicates success
    if (!response.ok) {
       let errorData = { detail: `Chat query failed with status: ${response.status}` };
       try {
         // Try to get more specific error details from the response body
         errorData = await response.json();
       } catch (parseError) {
          // If the error response isn't valid JSON, log it but use the status text
         console.error("Could not parse error response JSON:", parseError);
         errorData.detail = response.statusText || errorData.detail;
       }
       // Throw an error using the detail from the backend if available
       throw new Error(errorData.detail || 'Chat query failed');
    }

    // If the response is OK, parse the JSON body
    try {
      const data = await response.json();
      // Optionally, validate the structure of the successful response
      // if (typeof data?.response !== 'string') {
      //    throw new Error("Received unexpected data structure from chat bot.");
      // }
      return data; // Expected format { response: "..." }
    } catch (jsonError) {
      console.error("Failed to parse successful JSON response from /chat-bot:", jsonError);
      throw new Error("Received invalid JSON data from chat bot endpoint.");
    }

  } catch (networkError) {
     // Catch network errors or errors thrown above
    console.error('Error during sendQuery fetch:', networkError);
     // Re-throw the error
    throw networkError instanceof Error ? networkError : new Error('A network error occurred during the chat request.');
  }
};