import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart3, Users, Ticket, TrendingUp, Calendar, RefreshCw, DownloadCloud } from 'lucide-react';

const Dashboard = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    const fetchStats = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('token');
            const response = await axios.get(`${API_URL}/api/staff/stats/`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            setStats(response.data);
        } catch (err) {
            setError("No se pudieron cargar las estadísticas.");
        } finally {
            setLoading(false);
        }
    };

    const handleExport = async (eventoId, titulo) => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(`${API_URL}/api/staff/export-csv/${eventoId}/`, {
                headers: { 'Authorization': `Bearer ${token}` },
                responseType: 'blob'
            });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `lista_${titulo}.csv`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            alert("Error al exportar la lista.");
        }
    };

    useEffect(() => {
        fetchStats();
    }, []);

    if (loading) return (
        <div className="dash-container">
            <div className="loader-container">
                <div className="loader"></div>
                <p>Cargando métricas...</p>
            </div>
        </div>
    );

    if (error) return <div className="dash-container"><p className="error-msg">{error}</p></div>;

    return (
        <div className="dash-container">
            <header className="dash-header">
                <div>
                    <h1>Panel de Control</h1>
                    <p>Métricas en tiempo real de Backyard Bar</p>
                </div>
                <button className="refresh-btn" onClick={fetchStats}>
                    <RefreshCw size={20} /> Actualizar
                </button>
            </header>

            {/* Tarjetas de Resumen Global */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon income"><TrendingUp /></div>
                    <div className="stat-info">
                        <h3>Total Recaudado</h3>
                        <p className="stat-value">${stats.total_recaudado_global.toLocaleString()}</p>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon events"><Calendar /></div>
                    <div className="stat-info">
                        <h3>Eventos Activos</h3>
                        <p className="stat-value">{stats.total_eventos_activos}</p>
                    </div>
                </div>
            </div>

            <h2 className="section-title">Detalle por Evento</h2>

            <div className="events-list">
                {stats.eventos.map(evento => (
                    <div key={evento.id} className="event-row-card">
                        <div className="event-main-info">
                            <h3>{evento.titulo}</h3>
                            <div className="event-badges">
                                <span className="badge"><Ticket size={14} /> {evento.vendidas} Vendidas</span>
                                <span className="badge success"><Users size={14} /> {evento.usadas} Ingresos</span>
                            </div>
                        </div>

                        <div className="progress-container">
                            <div className="progress-labels">
                                <span>Ocupación</span>
                                <span>{Math.round((evento.usadas / (evento.vendidas || 1)) * 100)}%</span>
                            </div>
                            <div className="progress-bar-bg">
                                <div
                                    className="progress-bar-fill"
                                    style={{ width: `${(evento.usadas / (evento.vendidas || 1)) * 100}%` }}
                                ></div>
                            </div>
                        </div>

                        <div className="event-revenue">
                            <p className="label">Recaudado</p>
                            <p className="value">${evento.recaudado.toLocaleString()}</p>
                            <button
                                className="export-mini-btn"
                                onClick={() => handleExport(evento.id, evento.titulo)}
                                title="Exportar Lista de Invitados"
                            >
                                <DownloadCloud size={16} /> CSV
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            <style jsx>{`
                .dash-container {
                    padding: 100px 5% 50px;
                    max-width: 1200px;
                    margin: 0 auto;
                    font-family: 'Inter', sans-serif;
                    color: white;
                }

                .dash-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 40px;
                }

                .dash-header h1 {
                    font-size: 2.5rem;
                    background: linear-gradient(to right, #fff, #94a3b8);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin: 0;
                }

                .refresh-btn {
                    background: rgba(255,255,255,0.05);
                    border: 1px solid rgba(255,255,255,0.1);
                    color: white;
                    padding: 10px 20px;
                    border-radius: 12px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    transition: all 0.3s;
                }

                .refresh-btn:hover {
                    background: rgba(255,255,255,0.1);
                }

                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 50px;
                }

                .stat-card {
                    background: rgba(30, 41, 59, 0.5);
                    border: 1px solid rgba(255,255,255,0.05);
                    padding: 25px;
                    border-radius: 24px;
                    display: flex;
                    align-items: center;
                    gap: 20px;
                }

                .stat-icon {
                    width: 60px;
                    height: 60px;
                    border-radius: 18px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }

                .stat-icon.income { background: rgba(34, 197, 94, 0.1); color: #22c55e; }
                .stat-icon.events { background: rgba(59, 130, 246, 0.1); color: #3b82f6; }

                .stat-info h3 { font-size: 0.9rem; color: #94a3b8; margin: 0; }
                .stat-value { font-size: 1.8rem; fontWeight: 800; margin: 5px 0 0; }

                .section-title {
                    font-size: 1.5rem;
                    margin-bottom: 25px;
                    border-left: 4px solid var(--accent);
                    padding-left: 15px;
                }

                .events-list {
                    display: flex;
                    flex-direction: column;
                    gap: 15px;
                }

                .event-row-card {
                    background: rgba(30, 41, 59, 0.5);
                    border-radius: 20px;
                    padding: 25px;
                    display: grid;
                    grid-template-columns: 1.5fr 1.5fr 1fr;
                    align-items: center;
                    gap: 30px;
                }

                .event-main-info h3 { margin: 0 0 10px; font-size: 1.2rem; }
                .event-badges { display: flex; gap: 10px; }
                .badge {
                    background: rgba(255,255,255,0.05);
                    padding: 4px 10px;
                    border-radius: 8px;
                    font-size: 0.8rem;
                    display: flex;
                    align-items: center;
                    gap: 5px;
                    color: #94a3b8;
                }
                .badge.success { color: var(--accent); }

                .progress-container { width: 100%; }
                .progress-labels {
                    display: flex;
                    justify-content: space-between;
                    font-size: 0.8rem;
                    color: #94a3b8;
                    margin-bottom: 8px;
                }
                .progress-bar-bg {
                    height: 8px;
                    background: #0f172a;
                    border-radius: 4px;
                    overflow: hidden;
                }
                .progress-bar-fill {
                    height: 100%;
                    background: linear-gradient(to right, #3b82f6, var(--accent));
                    border-radius: 4px;
                }

                .event-revenue { text-align: right; }
                .event-revenue .label { font-size: 0.8rem; color: #94a3b8; margin: 0; }
                .event-revenue .value { font-size: 1.4rem; font-weight: 700; color: #fff; margin: 5px 0 0; }

                .export-mini-btn {
                    margin-top: 10px;
                    background: rgba(255,255,255,0.05);
                    border: 1px solid rgba(255,255,255,0.1);
                    color: #94a3b8;
                    padding: 5px 12px;
                    border-radius: 8px;
                    font-size: 0.75rem;
                    cursor: pointer;
                    display: inline-flex;
                    align-items: center;
                    gap: 5px;
                    transition: all 0.2s;
                }

                .export-mini-btn:hover {
                    background: var(--accent);
                    color: black;
                    border-color: var(--accent);
                }

                .loader-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    min-height: 400px;
                }

                .loader {
                    border: 4px solid #334155;
                    border-top: 4px solid var(--accent);
                    border-radius: 50%;
                    width: 50px;
                    height: 50px;
                    animation: spin 1s linear infinite;
                    margin-bottom: 20px;
                }

                @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            `}</style>
        </div>
    );
};

export default Dashboard;
