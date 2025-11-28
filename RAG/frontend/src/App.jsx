import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE = 'http://localhost:8000'

function App() {
    const [messages, setMessages] = useState([])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [currentPage, setCurrentPage] = useState('home')
    const [dashboard, setDashboard] = useState(null)
    const [documents, setDocuments] = useState([])
    const [uploading, setUploading] = useState(false)
    const messagesEndRef = useRef(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    useEffect(() => {
        if (currentPage === 'dashboard') {
            fetchDashboard()
        } else if (currentPage === 'documents') {
            fetchDocuments()
        }
    }, [currentPage])

    const fetchDashboard = async () => {
        try {
            const response = await axios.get(`${API_BASE}/api/dashboard`)
            setDashboard(response.data)
        } catch (error) {
            console.error('Dashboard error:', error)
        }
    }

    const fetchDocuments = async () => {
        try {
            const response = await axios.get(`${API_BASE}/api/documents`)
            setDocuments(response.data.documents || [])
        } catch (error) {
            console.error('Documents error:', error)
        }
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        if (!input.trim() || loading) return

        const userMessage = { role: 'user', content: input }
        setMessages(prev => [...prev, userMessage])
        setInput('')
        setLoading(true)

        try {
            const response = await axios.post(`${API_BASE}/api/query`, {
                query: input,
                n_results: 5
            })

            const assistantMessage = {
                role: 'assistant',
                content: response.data.answer,
                sources: response.data.sources,
                confidence: response.data.confidence,
                risk_score: response.data.risk_score,
                risk_level: response.data.risk_level,
                risk_flags: response.data.risk_flags,
                query_time: response.data.query_time
            }

            setMessages(prev => [...prev, assistantMessage])
        } catch (error) {
            console.error('Query error:', error)
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'Error: ' + (error.response?.data?.detail || error.message)
            }])
        } finally {
            setLoading(false)
        }
    }

    const handleFileUpload = async (e) => {
        const file = e.target.files[0]
        if (!file) return

        setUploading(true)
        const formData = new FormData()
        formData.append('file', file)

        try {
            const response = await axios.post(`${API_BASE}/api/upload`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })
            alert(`✅ Uploaded: ${response.data.filename} (${response.data.chunks} chunks)`)
            // Refresh documents list
            if (currentPage === 'documents') {
                fetchDocuments()
            }
        } catch (error) {
            alert('❌ Upload failed: ' + (error.response?.data?.detail || error.message))
        } finally {
            setUploading(false)
        }
    }

    const getRiskColor = (level) => {
        switch (level) {
            case 'HIGH': return '#ef4444'
            case 'MEDIUM': return '#f59e0b'
            case 'LOW': return '#10b981'
            default: return '#6b7280'
        }
    }

    return (
        <div className="app">
            {/* Top Navbar */}
            <nav className="navbar">
                <div className="navbar-brand" onClick={() => setCurrentPage('home')}>
                    <span className="logo">🔐</span>
                    <span className="brand-name">KYC/AML Assistant</span>
                </div>

                <div className="navbar-menu">
                    <button
                        className={`nav-link ${currentPage === 'home' ? 'active' : ''}`}
                        onClick={() => setCurrentPage('home')}
                    >
                        Home
                    </button>
                    <button
                        className={`nav-link ${currentPage === 'chat' ? 'active' : ''}`}
                        onClick={() => setCurrentPage('chat')}
                    >
                        Chat
                    </button>
                    <button
                        className={`nav-link ${currentPage === 'dashboard' ? 'active' : ''}`}
                        onClick={() => setCurrentPage('dashboard')}
                    >
                        Dashboard
                    </button>
                    <button
                        className={`nav-link ${currentPage === 'documents' ? 'active' : ''}`}
                        onClick={() => setCurrentPage('documents')}
                    >
                        Documents
                    </button>
                </div>
            </nav>

            {/* Main Content */}
            <div className="main-container">
                {/* Landing Page */}
                {currentPage === 'home' && (
                    <div className="landing-page">
                        <div className="hero-section">
                            <h1 className="hero-title">KYC/AML Compliance Assistant</h1>
                            <p className="hero-subtitle">
                                AI-Powered RAG System for Regulatory Compliance
                            </p>
                            <p className="hero-description">
                                Upload regulatory documents and get instant, accurate answers to your compliance questions.
                                Powered by advanced AI and local embeddings for maximum security.
                            </p>

                            <div className="hero-buttons">
                                <button
                                    className="btn-primary"
                                    onClick={() => setCurrentPage('chat')}
                                >
                                    Get Started →
                                </button>
                                <button className="btn-secondary">
                                    Learn More
                                </button>
                            </div>
                        </div>

                        <div className="features-grid">
                            <div className="feature-card glass-card">
                                <div className="feature-icon">🔍</div>
                                <h3>Smart Search</h3>
                                <p>Query across multiple regulatory documents instantly</p>
                            </div>

                            <div className="feature-card glass-card">
                                <div className="feature-icon">🚨</div>
                                <h3>Risk Scoring</h3>
                                <p>Automatic risk analysis for compliance queries</p>
                            </div>

                            <div className="feature-card glass-card">
                                <div className="feature-icon">📊</div>
                                <h3>Dashboard</h3>
                                <p>Monitor compliance metrics in real-time</p>
                            </div>

                            <div className="feature-card glass-card">
                                <div className="feature-icon">🔐</div>
                                <h3>Secure</h3>
                                <p>All processing happens locally - your data stays private</p>
                            </div>
                        </div>
                    </div>
                )}

                {/* Chat Page */}
                {currentPage === 'chat' && (
                    <div className="chat-page">
                        <div className="page-header">
                            <h2>Compliance Chat</h2>
                            <p>Ask questions about KYC/AML regulations</p>
                        </div>

                        <div className="glass-card chat-container">
                            <div className="messages">
                                {messages.length === 0 && (
                                    <div className="welcome">
                                        <h2>Start a Conversation</h2>
                                        <p>Ask me anything about KYC/AML compliance</p>
                                        <div className="example-queries">
                                            <button onClick={() => setInput("What documents are required for merchant KYC?")}>
                                                What documents are required for merchant KYC?
                                            </button>
                                            <button onClick={() => setInput("What are PEP screening requirements?")}>
                                                What are PEP screening requirements?
                                            </button>
                                        </div>
                                    </div>
                                )}

                                {messages.map((msg, idx) => (
                                    <div key={idx} className={`message ${msg.role}`}>
                                        <div className="message-header">
                                            <strong>{msg.role === 'user' ? '🧑 You' : '🤖 Assistant'}</strong>
                                            {msg.query_time && (
                                                <span className="query-time">⏱️ {msg.query_time.toFixed(2)}s</span>
                                            )}
                                        </div>

                                        {msg.risk_score !== undefined && (
                                            <div
                                                className="risk-badge"
                                                style={{ backgroundColor: getRiskColor(msg.risk_level) }}
                                            >
                                                {msg.risk_level === 'HIGH' ? '🚨' : msg.risk_level === 'MEDIUM' ? '⚠️' : '✅'}
                                                Risk: {msg.risk_score}/100 ({msg.risk_level})
                                            </div>
                                        )}

                                        {msg.risk_flags && msg.risk_flags.length > 0 && (
                                            <div className="risk-flags">
                                                {msg.risk_flags.map((flag, i) => (
                                                    <div key={i}>⚠️ {flag}</div>
                                                ))}
                                            </div>
                                        )}

                                        <div className="message-content">
                                            {msg.content.split('\n').map((line, i) => (
                                                <p key={i}>{line}</p>
                                            ))}
                                        </div>

                                        {msg.confidence !== undefined && (
                                            <div className="confidence">
                                                🔍 Confidence: {(msg.confidence * 100).toFixed(0)}%
                                            </div>
                                        )}

                                        {msg.sources && msg.sources.length > 0 && (
                                            <details className="sources">
                                                <summary>📚 Sources ({msg.sources.length})</summary>
                                                {msg.sources.map((src, i) => (
                                                    <div key={i} className="source">
                                                        <strong>📄 {src.filename}</strong>
                                                        <p>{src.snippet}</p>
                                                        <small>Similarity: {(src.similarity * 100).toFixed(1)}%</small>
                                                    </div>
                                                ))}
                                            </details>
                                        )}
                                    </div>
                                ))}

                                {loading && (
                                    <div className="message assistant loading">
                                        <div className="message-header"><strong>🤖 Assistant</strong></div>
                                        <div className="message-content">
                                            <div className="typing-indicator">
                                                <span></span><span></span><span></span>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                <div ref={messagesEndRef} />
                            </div>

                            <form onSubmit={handleSubmit} className="input-form">
                                <label className="upload-btn-inline">
                                    <input
                                        type="file"
                                        onChange={handleFileUpload}
                                        disabled={uploading}
                                        accept=".pdf,.txt,.docx,.doc,.csv,.json,.html,.htm,.xlsx,.xls,.xml"
                                        style={{ display: 'none' }}
                                    />
                                    <span className="upload-icon">
                                        {uploading ? '⏳' : '📎'}
                                    </span>
                                </label>

                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    placeholder="Ask about KYC/AML compliance..."
                                    disabled={loading}
                                />
                                <button type="submit" disabled={loading || !input.trim()}>
                                    {loading ? '⏳' : '📤'} Send
                                </button>
                            </form>
                        </div>
                    </div>
                )}

                {/* Documents Page */}
                {currentPage === 'documents' && (
                    <div className="documents-page">
                        <div className="page-header">
                            <h2>Loaded Documents</h2>
                            <p>All regulatory documents in the system</p>
                        </div>

                        <div className="documents-grid">
                            {documents.length > 0 ? (
                                documents.map((doc, idx) => (
                                    <div key={idx} className="glass-card document-card">
                                        <div className="document-icon">📄</div>
                                        <h3 className="document-name">{doc.filename}</h3>
                                        <div className="document-meta">
                                            <span className="chunk-count">{doc.chunks} chunks</span>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="glass-card no-documents">
                                    <p>No documents loaded yet</p>
                                    <p className="hint">Upload documents using the 📎 button in the chat</p>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Dashboard Page */}
                {currentPage === 'dashboard' && (
                    <div className="dashboard-page">
                        <div className="page-header">
                            <h2>Compliance Dashboard</h2>
                            <p>Monitor your compliance metrics</p>
                        </div>

                        <div className="dashboard">
                            {dashboard ? (
                                <>
                                    <div className="glass-card metric-card large">
                                        <div className="metric-value">{dashboard.compliance_score.toFixed(1)}/100</div>
                                        <div className="metric-label">Overall Compliance Score</div>
                                    </div>

                                    <div className="metrics-grid">
                                        <div className="glass-card metric-card">
                                            <div className="metric-value">{dashboard.total_documents}</div>
                                            <div className="metric-label">Documents</div>
                                        </div>
                                        <div className="glass-card metric-card">
                                            <div className="metric-value">{dashboard.total_chunks}</div>
                                            <div className="metric-label">Chunks</div>
                                        </div>
                                        <div className="glass-card metric-card">
                                            <div className="metric-value">{dashboard.total_queries}</div>
                                            <div className="metric-label">Queries</div>
                                        </div>
                                        <div className="glass-card metric-card">
                                            <div className="metric-value">{(dashboard.avg_confidence * 100).toFixed(0)}%</div>
                                            <div className="metric-label">Avg Confidence</div>
                                        </div>
                                    </div>
                                </>
                            ) : (
                                <div className="glass-card">
                                    <div className="loading-dashboard">Loading...</div>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}

export default App
