import axios from "axios";
import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { postData } from "../axios/fetchData";

const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  // State to hold the authentication token
  const [token, setToken] = useState(sessionStorage.getItem("access_token"));

  const login = async (username, password) => {
    const response = await postData(
      "/auth/token",
      {
        username,
        password,
      },
      { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
    );

    if (response.access_token) {
      setToken(response.access_token);
    }
    return response;
  };

  const logout = () => {
    setToken();
  };
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common["Authorization"] = "Bearer " + token;
      sessionStorage.setItem("access_token", token);
    } else {
      delete axios.defaults.headers.common["Authorization"];
      sessionStorage.removeItem("access_token");
    }
  }, [token]);

  // Memoized value of the authentication context
  const contextValue = useMemo(
    () => ({
      token,
      setToken,
      login,
      logout,
    }),
    [token]
  );

  // Provide the authentication context to the children components
  return (
    <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
  );
};

export const useAuth = () => {
  return useContext(AuthContext);
};

export default AuthProvider;
