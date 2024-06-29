import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

const NAV_ITEMS = [
  { path: "/service", text: "Service" },
  { path: "/about-us", text: "About Us" },
  { path: "/login", text: "Login", condition: (token) => !token },
  { path: "/register", text: "Register", condition: (token) => !token },
  { path: "/profile", text: "Profile", condition: (token) => !!token },
  {
    path: "/",
    text: "Logout",
    action: "logout",
    condition: (token) => !!token,
  },
];

const NavBar = () => {
  const { token, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(true);

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  return (
    <nav className="bg-primary-600 p-4">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <div className="flex items-center">
          <NavLink to="/" className="text-white text-xl font-bold">
            Unprompt
          </NavLink>
        </div>
        <div className="md:hidden">
          <button
            onClick={toggleMenu}
            className="focus:outline-none text-white"
          >
            {isOpen ? (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            ) : (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16m-7 6h7"
                />
              </svg>
            )}
          </button>
        </div>
        <div
          className={`md:flex md:items-center space-x-4 ${
            isOpen ? "block" : "hidden"
          }`}
        >
          <ul className="md:flex space-x-4">
            {NAV_ITEMS.map((item, index) => (
              <React.Fragment key={item.path + index}>
                {(!item.condition || item.condition(token)) && (
                  <li>
                    <NavLink
                      to={item.path}
                      className="text-white hover:text-gray-300"
                      onClick={item.action === "logout" ? logout : toggleMenu}
                    >
                      {item.text}
                    </NavLink>
                  </li>
                )}
              </React.Fragment>
            ))}
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default NavBar;
