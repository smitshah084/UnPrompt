import Login from "./pages/login/login";
import Register from "./pages/register/register";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import { Bounce, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import Home from "./pages/home/home";


function App() {
  return (
    <>
      <ToastContainer
        position="top-center"
        autoClose={2000}
        closeOnClick={true}
        pauseOnHover={true}
        draggable={true}
        theme="light"
        transition={Bounce}
      />
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />

          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Routes>
      </Router>
    </>
  );
}

export default App;
