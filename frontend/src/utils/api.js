import axios from 'axios';

// API base URL - will use proxy in development, or direct URL in production
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout for math problems
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging (can be extended for auth tokens)
apiClient.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error);
    
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      if (status === 400) {
        // Handle structured error responses
        if (data.detail && typeof data.detail === 'object') {
          const errorDetail = data.detail;
          if (errorDetail.error === 'Non-mathematical question') {
            // Create a structured error for non-math questions
            const structuredError = new Error(errorDetail.message);
            structuredError.status = status;
            structuredError.data = errorDetail;
            throw structuredError;
          }
        }
        throw new Error(data.detail || 'Bad request - please check your input');
      } else if (status === 500) {
        throw new Error(data.detail || 'Server error - please try again later');
      } else if (status === 503) {
        throw new Error('Service temporarily unavailable - please try again');
      } else {
        throw new Error(data.detail || `HTTP ${status} error`);
      }
    } else if (error.request) {
      // Request made but no response
      throw new Error('Network error - please check your connection');
    } else {
      // Something else happened
      throw new Error(error.message || 'An unexpected error occurred');
    }
  }
);

/**
 * Submit a math query to the backend
 * @param {string} question - The mathematical question
 * @param {string|null} context - Optional context for the question
 * @param {string|null} userId - Optional user identifier
 * @returns {Promise<Object>} Query result with answer, confidence, sources, etc.
 */
export const submitQuery = async (question, context = null, userId = null) => {
  try {
    const payload = {
      question: question.trim(),
    };
    
    if (context) {
      payload.context = context.trim();
    }
    
    if (userId) {
      payload.user_id = userId;
    }
    
    const response = await apiClient.post('/query', payload);
    return response.data;
  } catch (error) {
    console.error('Error submitting query:', error);
    throw error;
  }
};

/**
 * Submit user feedback for a query
 * @param {Object} feedbackData - Feedback data
 * @param {string} feedbackData.query_id - ID of the query being rated
 * @param {string} feedbackData.feedback_type - Type of feedback (positive, negative, correction, clarification)
 * @param {string|null} feedbackData.feedback_text - Optional feedback text
 * @param {string|null} feedbackData.corrected_answer - Optional corrected answer
 * @param {string|null} feedbackData.user_id - Optional user identifier
 * @returns {Promise<Object>} Feedback submission result
 */
export const submitFeedback = async (feedbackData) => {
  try {
    const payload = {
      query_id: feedbackData.query_id,
      feedback_type: feedbackData.feedback_type,
    };
    
    if (feedbackData.feedback_text) {
      payload.feedback_text = feedbackData.feedback_text.trim();
    }
    
    if (feedbackData.corrected_answer) {
      payload.corrected_answer = feedbackData.corrected_answer.trim();
    }
    
    if (feedbackData.user_id) {
      payload.user_id = feedbackData.user_id;
    }
    
    const response = await apiClient.post('/feedback', payload);
    return response.data;
  } catch (error) {
    console.error('Error submitting feedback:', error);
    throw error;
  }
};

/**
 * Get feedback history for a specific query
 * @param {string} queryId - Query ID to get feedback for
 * @returns {Promise<Object>} Feedback history
 */
export const getQueryFeedback = async (queryId) => {
  try {
    const response = await apiClient.get(`/query/${queryId}/feedback`);
    return response.data;
  } catch (error) {
    console.error('Error getting query feedback:', error);
    throw error;
  }
};

/**
 * Health check for the API
 * @returns {Promise<Object>} API health status
 */
export const checkApiHealth = async () => {
  try {
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    console.error('Error checking API health:', error);
    throw error;
  }
};

/**
 * Get API status and version info
 * @returns {Promise<Object>} API status
 */
export const getApiStatus = async () => {
  try {
    // Use the root endpoint for basic status
    const response = await axios.get('/');
    return response.data;
  } catch (error) {
    console.error('Error getting API status:', error);
    throw error;
  }
};

// Export the configured axios instance for direct use if needed
export { apiClient };

// Default export with all API functions
export default {
  submitQuery,
  submitFeedback,
  getQueryFeedback,
  checkApiHealth,
  getApiStatus,
  client: apiClient,
};