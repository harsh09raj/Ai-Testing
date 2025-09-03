const express = require('express');
const path = require('path');
const axios = require('axios');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(bodyParser.json());

// Middleware for parsing JSON
app.use(express.json());

// Serve static files from the 'frontend' directory
app.use(express.static(path.join(__dirname, 'frontend')));

// POST /generate API endpoint - forwards to Python FastAPI service
app.post('/generate', async (req, res) => {
    try {
        const { repo_url } = req.body;
        
        if (!repo_url) {
            return res.status(400).json({
                success: false,
                error: 'repo_url is required'
            });
        }
        
        // Forward request to Python FastAPI service
        const pythonResponse = await axios.post('http://localhost:8000/api/generate-release-notes', {
            repo_url: repo_url
        });
        
        // Return the release_notes from Python service
        res.json({
            success: true,
            release_notes: pythonResponse.data.release_notes
        });
        
    } catch (error) {
        console.error('Error forwarding to Python API:', error.message);
        res.status(500).json({
            success: false,
            error: error.response?.data?.detail || error.message
        });
    }
});

// Serve the main HTML file for any route not handled by API
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'frontend', 'index.html'));
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
    console.log(`Frontend available at http://localhost:${PORT}`);
    console.log(`API endpoint available at http://localhost:${PORT}/generate`);
});
