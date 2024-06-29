import { Bounce, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import AuthProvider from "./hooks/useAuth";
import Routes from "./routes";

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
      <AuthProvider>
        <Routes />
      </AuthProvider>
    </>
  );
}

export default App;
