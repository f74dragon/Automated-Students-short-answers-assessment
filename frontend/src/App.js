import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Login from "./pages/Login";
import Home from "./pages/Home";
import CollectionDetails from "./pages/CollectionDetails";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/home" element={<Home />} />
        <Route path="/collection/:id" element={<CollectionDetails />} />
      </Routes>
    </Router>
  );
}

export default App;
