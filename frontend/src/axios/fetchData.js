import axiosInstance from "./axiosInstance";

export const fetchData = async (ENDPOINT) => {
  try {
    const response = await axiosInstance.get(ENDPOINT);
    return response.data;
  } catch (error) {
    console.error("Error fetching data", error);
  }
};

export const postData = async (ENDPOINT, Payload) => {
  try {
    const response = await axiosInstance.post(ENDPOINT, Payload);
    return response.data;
  } catch (error) {
    console.error("Error fetching data", error);
  }
};
