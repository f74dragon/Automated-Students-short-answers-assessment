import axios from 'axios';

const API_URL = 'http://localhost:8001/api';

// Collection API calls
export const getCollections = async (userId) => {
  try {
    const response = await axios.get(`${API_URL}/collections/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching collections:', error);
    throw error;
  }
};

export const createCollection = async (collectionData) => {
  try {
    const response = await axios.post(`${API_URL}/collections/`, collectionData);
    return response.data;
  } catch (error) {
    console.error('Error creating collection:', error);
    throw error;
  }
};

// Question API calls
export const getQuestions = async (collectionId) => {
  try {
    const response = await axios.get(`${API_URL}/collections/${collectionId}/questions/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching questions:', error);
    throw error;
  }
};

export const createQuestion = async (collectionId, questionData) => {
  try {
    const response = await axios.post(`${API_URL}/collections/${collectionId}/questions/`, questionData);
    return response.data;
  } catch (error) {
    console.error('Error creating question:', error);
    throw error;
  }
};

export const updateQuestion = async (collectionId, questionId, questionData) => {
  try {
    const response = await axios.patch(`${API_URL}/collections/${collectionId}/questions/${questionId}`, questionData);
    return response.data;
  } catch (error) {
    console.error('Error updating question:', error);
    throw error;
  }
};

export const deleteQuestion = async (collectionId, questionId) => {
  try {
    const response = await axios.delete(`${API_URL}/collections/${collectionId}/questions/${questionId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting question:', error);
    throw error;
  }
};

// User API calls
export const getUsers = async () => {
  try {
    const response = await axios.get(`${API_URL}/users/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching users:', error);
    throw error;
  }
};
