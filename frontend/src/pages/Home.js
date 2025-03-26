import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { getUsers, getCollections, createCollection } from "../services/api";
import CollectionDetail from "../components/CollectionDetail";
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

        const userRes = await getUsers();
        const user = userRes.users.find(u => u.username === username);
        if (!user) throw new Error("User not found");

        setUserId(user.id);
        const colRes = await getCollections(user.id);
        setCollections(colRes.collections);
      } catch (err) {
        console.error("Failed to fetch collections", err);
      }
    };

    fetchUserAndCollections();
  }, [navigate]);
  
  const fetchCollections = async () => {
    if (!userId) return;
    try {
      const response = await getCollections(userId);
      setCollections(response.collections);
    } catch (err) {
      console.error("Failed to fetch collections", err);
    }
  };

  const handleCreate = async () => {
    try {
      await createCollection({
        name,
        description,
        user_id: userId
      });
      setShowModal(false);
      setName("");
      setDescription("");
      fetchCollections();
    } catch (err) {
      console.error("Failed to create collection", err);
    }
  };

  return (
    <div className="home-container">
      <div className="taskbar">
        <div className="taskbar-left">
          <Link to="/home" className="active">🏠 Home</Link>
          <Link to="/students">👨‍🎓 Students</Link>
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
          <h2>Your Exam Collections</h2>
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
        <div className="modal-overlay">
          <div className="modal-content">
            <CollectionDetail 
              collection={selectedCollection} 
              onClose={() => setSelectedCollection(null)}
              onRefresh={fetchCollections}
            />
          </div>
        </div>
      )}

      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content creation-form">
            <h2>Create New Collection</h2>
            <div className="form-group">
              <input
                type="text"
                placeholder="Collection Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <div className="form-group">
              <textarea
                placeholder="Description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
            <div className="form-actions">
              <button className="cancel-btn" onClick={() => setShowModal(false)}>Cancel</button>
              <button className="submit-btn" onClick={handleCreate}>Create</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
