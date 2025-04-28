import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import "../styles/Home.css";

export default function Home() {
  const [collections, setCollections] = useState([]);
  const [combinations, setCombinations] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [selectedCombination, setSelectedCombination] = useState(null);
  const [userId, setUserId] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return navigate("/");

    const fetchUserAndCollections = async () => {
      try {
        const decodedToken = JSON.parse(atob(token.split(".")[1]));
        const username = decodedToken.sub;

        const userRes = await axios.get(`/api/users/`);
        const user = userRes.data.users.find(u => u.username === username);
        if (!user) throw new Error("User not found");

        setUserId(user.id);
        const colRes = await axios.get(`/api/collections/${user.id}`);
        setCollections(colRes.data.collections);
      } catch (err) {
        console.error("Failed to fetch collections", err);
      }
    };

    fetchUserAndCollections();
  }, [navigate]);
  
  // Fetch combinations when modal is opened
  useEffect(() => {
    if (showModal) {
      const fetchCombinations = async () => {
        setLoading(true);
        try {
          const response = await axios.get("/api/combinations/");
          setCombinations(response.data);
          
          if (response.data.length > 0) {
            // Default to the first combination
            setSelectedCombination(response.data[0].id);
          }
        } catch (error) {
          console.error("Failed to fetch combinations:", error);
        } finally {
          setLoading(false);
        }
      };
      
      fetchCombinations();
    }
  }, [showModal]);

  const handleCreate = async () => {
    if (!name || !selectedCombination) {
      alert("Please provide a name and select a grading pair");
      return;
    }

    try {
      await axios.post("/api/collections/", {
        name,
        description,
        user_id: userId,
        combination_id: selectedCombination
      });
      setShowModal(false);
      setName("");
      setDescription("");
      setSelectedCombination(null);

      const res = await axios.get(`/api/collections/${userId}`);
      setCollections(res.data.collections);
    } catch (err) {
      console.error("Failed to create collection", err);
      alert("Failed to create collection: " + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="home-container">
      <div className="taskbar">
        <div className="taskbar-left">
          <Link to="/home">🏠 Home</Link>
          <Link to="/collections">📚 Collections</Link>
          <Link to="/pairs">🔗 Pairs</Link>
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
          {collections.length === 0 ? (
            <div className="empty-collections">
              <h2>No Collections</h2>
              <p>You don't have any collections yet. Create your first collection to get started!</p>
              <button className="create-collection-btn create-first" onClick={() => setShowModal(true)}>
                ➕ Create Collection
              </button>
            </div>
          ) : (
            <div className="collections-with-items">
              <h2>Your Question Collections</h2>
              <div className="collections-list">
                {collections.map((collection) => (
                  <div
                    key={collection.id}
                    className="collection-item"
                    onClick={() => navigate(`/collection/${collection.id}`)}
                  >
                    <h3>{collection.name}</h3>
                    <p>{collection.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
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
          <div className="modal-form">
            <div className="form-group">
              <label htmlFor="collection-name">Collection Name</label>
              <input
                id="collection-name"
                type="text"
                placeholder="Enter a name for your collection"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label htmlFor="collection-description">Description</label>
              <textarea
                id="collection-description"
                placeholder="Add a brief description (optional)"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="collection-combination">Grading Pair *</label>
              {loading ? (
                <p>Loading grading pairs...</p>
              ) : combinations.length > 0 ? (
                <select
                  id="collection-combination"
                  value={selectedCombination}
                  onChange={(e) => setSelectedCombination(parseInt(e.target.value))}
                  required
                >
                  {combinations.map((combination) => (
                    <option key={combination.id} value={combination.id}>
                      {combination.name} - {combination.model_name}
                    </option>
                  ))}
                </select>
              ) : (
                <p>No grading pairs available. Please create one first in the Pairs section.</p>
              )}
              <small>Select a prompt-model pair to use for grading student answers.</small>
            </div>
          </div>
          <button className="exit-btn" onClick={handleCreate}>Create Collection</button>
        </div>
      )}
    </div>
  );
}
