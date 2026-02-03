// API configuration
// In production, set VITE_API_URL environment variable or use staticwebapp.config.json proxy
const API_BASE = window.FITAPP_API_URL || "/api";

// Map raw validation errors to user-friendly messages
const ERROR_MESSAGES = {
  // Date errors
  'Activity date cannot be in the future': 'Date cannot be in the future.',
  'Activity date cannot be more than one year in the past': 'Date cannot be more than one year in the past.',
  'date must be ISO format YYYY-MM-DD': 'Please enter a valid date.',
  
  // Type errors
  'type must be one of Running, Rowing, Rucking': 'Please select a valid activity type.',
  
  // Distance errors
  'Distance is required for Running and Rucking': 'Distance is required for this activity type.',
  'Distance must be omitted/null for Rowing': 'Distance should not be entered for Rowing activities.',
  'Input should be greater than 0': 'Value must be greater than zero.',
  
  // Duration errors
  'duration': 'Duration must be greater than zero.',
  
  // Heart rate errors
  'Input should be greater than or equal to 20': 'Heart rate must be at least 20 BPM.',
  'Input should be less than or equal to 240': 'Heart rate cannot exceed 240 BPM.',
  
  // Comments errors
  'Comments cannot exceed 1000 characters': 'Comments are too long (max 1000 characters).',
  'Comments cannot contain HTML tags': 'Comments cannot contain special characters like < or >.',
  
  // Generic errors
  'Invalid JSON': 'There was a problem with the data. Please try again.',
  'Not found': 'The activity could not be found.',
  'Missing id in route': 'Activity ID is missing.',
};

function parseErrorMessage(text) {
  // Try to parse as JSON first
  try {
    const json = JSON.parse(text);
    if (json.error) {
      text = json.error;
    }
  } catch {
    // Not JSON, use as-is
  }
  
  // Check for known error patterns and return friendly message
  for (const [pattern, friendly] of Object.entries(ERROR_MESSAGES)) {
    if (text.includes(pattern)) {
      return friendly;
    }
  }
  
  // Extract meaningful part from Pydantic validation errors
  // Format: "1 validation error for ActivityCreate\nfield\n  error message [type=..., ...]"
  const validationMatch = text.match(/validation error[s]? for \w+\n(\w+)\n\s*(.+?)(?:\s*\[|$)/);
  if (validationMatch) {
    const field = validationMatch[1];
    const message = validationMatch[2].trim();
    
    // Map field names to friendly names
    const fieldNames = {
      'type': 'Activity type',
      'duration': 'Duration',
      'distance': 'Distance',
      'avgBpm': 'Heart rate',
      'date': 'Date',
      'comments': 'Comments',
    };
    
    const friendlyField = fieldNames[field] || field;
    return `${friendlyField}: ${message}`;
  }
  
  // Default fallback
  return 'Something went wrong. Please check your input and try again.';
}

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    const friendlyMessage = parseErrorMessage(text);
    throw new Error(friendlyMessage);
  }
  return res.status === 204 ? null : res.json();
}

export async function listActivities(type, limit = 50) {
  const q = new URLSearchParams();
  if (type) q.set('type', type);
  if (limit) q.set('limit', String(limit));
  return request(`/activities?${q.toString()}`);
}

export async function createActivity(payload) {
  return request(`/activities`, { method: 'POST', body: JSON.stringify(payload) });
}

export async function updateActivity(id, payload) {
  return request(`/activities/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
}

export async function deleteActivity(id) {
  return request(`/activities/${id}`, { method: 'DELETE' });
}

/**
 * Fetch today's AI-generated workout recommendation.
 * 
 * @returns {Promise<Object>} DailyRecommendation object with date, goal, title, workout, rationale, confidence, fallback
 */
export async function fetchRecommendation() {
  // Add cache-busting parameter to ensure fresh data after activity logging
  const timestamp = Date.now();
  return request(`/coach/today?_t=${timestamp}`);
}

