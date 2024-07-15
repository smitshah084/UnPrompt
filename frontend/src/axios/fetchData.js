import axiosInstance from "./axiosInstance";

export const fetchData = async (ENDPOINT, customHeaders) => {
  try {
    const response = await axiosInstance.get(ENDPOINT, customHeaders);
    return response.data;
  } catch (error) {
    console.error("Error fetching data", error);
  }
};

export const postData = async (ENDPOINT, Payload, customHeaders) => {
  try {
    const response = await axiosInstance.post(ENDPOINT, Payload, customHeaders);
    return response.data;
  } catch (error) {
    console.error("Error fetching data", error);
  }
};

export const returnMock = async (value) => {
  return new Promise((resolve)=>{
    setTimeout(() => {
       resolve(value);
    }, 2000);
  })
};
