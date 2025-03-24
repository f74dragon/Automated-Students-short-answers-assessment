import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import "../styles/Home.css";

export default function Home() {
  const [collections, setCollections] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [userId, setUserId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return navigate("/");

    const fetchUserAndCollections = async () => {
      try {
        const decodedToken = JSON.parse(atob(token.split(".")[1]));
        const username = decodedToken.sub;

        const userRes = await axios.get(`http://localhost:8001/api/users/`);
        const user = userRes.data.users.find(u => u.username === username);
        if (!user) throw new Error("User not found");

        setUserId(user.id);
        const colRes = await axios.get(`http://localhost:8001/api/collections/${user.id}`);
        setCollections(colRes.data.collections);
      } catch (err) {
        console.error("Failed to fetch collections", err);
      }
    };

    fetchUserAndCollections();
  }, [navigate]);

  const handleCreate = async () => {
    try {
      await axios.post("http://localhost:8001/api/collections/", {
        name,
        description,
        user_id: userId
      });
      setShowModal(false);
      setName("");
      setDescription("");

      const res = await axios.get(`http://localhost:8001/api/collections/${userId}`);
      setCollections(res.data.collections);
    } catch (err) {
      console.error("Failed to create collection", err);
    }
  };

  return (
    <div className="home-container">
      <div className="taskbar">
        <div className="taskbar-left">
          <Link to="/home">🏠 Home</Link>
          <Link to="/collections">📚 Collections</Link>
          <Link to="/settings">⚙️ Settings</Link>
        </div>
        <div className="taskbar-right">
          <button className="create-collection-btn" onClick={() => setShowModal(true)}>
            ➕ Create Collection
          </button>
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

      {showModal && (
        <div className="fullscreen-modal">
          <button className="close-btn" onClick={() => setShowModal(false)}>✖</button>
          <h2>Create New Collection</h2>
          <input
            type="text"
            placeholder="Collection Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <textarea
            placeholder="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          <button className="exit-btn" onClick={handleCreate}>Create</button>
        </div>
      )}
    </div>
  );
}
