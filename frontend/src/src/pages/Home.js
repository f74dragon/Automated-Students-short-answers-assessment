import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import "../styles/Home.css";

export default function Home() {
  const [collections] = useState([
    { id: 1, name: "Biology Quiz 1", description: "Cell structures and functions." },
    { id: 2, name: "Physics Exam", description: "Newtonian mechanics principles." },
    { id: 3, name: "Chemistry Test", description: "Chemical reactions and bonding." },
    { id: 4, name: "Computer Science Quiz", description: "Data structures and algorithms." }
  ]);

  const [selectedCollection, setSelectedCollection] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user is authenticated (has token)
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/");
    }
  }, [navigate]);

  return (
    <div className="home-container">
      <div className="taskbar">
        <div className="taskbar-left">
          <Link to="/home">🏠 Home</Link>
          <Link to="/collections">📚 Collections</Link>
          <Link to="/settings">⚙️ Settings</Link>
        </div>
        <div className="taskbar-right">
          <button className="create-collection-btn">➕ Create Collection</button>
          <span className="user-icon">👤</span>
        </div>
      </div>

      <div className="content-box">
        <div className="collections-container">
          <h2>Your Question Collections</h2>
          <div className="collections-list">
            {collections.map((collection) => (
              <div
                key={collection.id}
                className="collection-item"
                onClick={() => setSelectedCollection(collection)}
              >
                <h3>{collection.name}</h3>
                <p>{collection.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {selectedCollection && (
        <div className="fullscreen-modal">
          <button className="close-btn" onClick={() => setSelectedCollection(null)}>✖</button>
          <h1>{selectedCollection.name}</h1>
          <p>{selectedCollection.description}</p>
          <button className="exit-btn" onClick={() => setSelectedCollection(null)}>Exit</button>
        </div>
      )}
    </div>
  );
}