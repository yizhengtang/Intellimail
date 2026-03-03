import axios from 'axios';

// Create a pre-configured Axios instance.
const api = axios.create({
  baseURL: 'http://localhost:8000',
});

//This response interceptor unwraps the Axios response envelope. Axios wraps every response in an object that includes data, status, headers and config.
//Since I only need the acutal data which is the json from fastapi, this interceptor extracts the response.data.
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    //Log the error for debugging
    const message = error.response?.data?.detail || error.message || 'An error occurred';
    console.error('API Error:', message);
    return Promise.reject(error);
  }
);

export default api;
