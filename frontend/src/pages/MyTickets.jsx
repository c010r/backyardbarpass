import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api, { getMediaUrl } from '../api';
import { motion } from 'framer-motion';
import { Download, Calendar, MapPin, ScanLine, CheckCircle2 } from 'lucide-react';

const MyTickets = () => {
    const [entradas, setEntradas] = useState([]);
    const [loading, setLoading] = useState(true);
    const [confirming, setConfirming] = useState(false);
    const location = useLocation();
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            navigate('/login');
            return;
        }

        // Verificar si venimos de un pago exitoso de Mercado Pago
        const queryParams = new URLSearchParams(location.search);
        const paymentId = queryParams.get('payment_id');
        const status = queryParams.get('status');

        const fetchTickets = () => {
            api.get('/mis-entradas/')
                .then(res => {
                    setEntradas(res.data);
                    setLoading(false);
                })
                .catch(err => {
                    console.error(err);
                    setLoading(false);
                });
        };

        if (paymentId && status === 'approved') {
            setConfirming(true);
            // Llamar al backend para confirmar el pago manualmente (por si el webhook falló/no existe en localhost)
            api.post('/pagos/confirmar-interactivo/', { payment_id: paymentId })
                .then(() => {
                    // Limpiar la URL para evitar re-procesamientos
                    navigate('/mis-entradas', { replace: true });
                    fetchTickets();
                })
                .catch(err => {
                    console.error("Error confirmando pago:", err);
                    fetchTickets();
                })
                .finally(() => setConfirming(false));
        } else {
            fetchTickets();
        }
    }, [location, navigate]);

    if (confirming) return (
        <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', gap: '20px' }}>
            <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ repeat: Infinity, duration: 2 }}>
                <CheckCircle2 size={60} color="var(--accent)" />
            </motion.div>
            <h2 style={{ fontSize: '2rem' }}>Confirmando tu pago...</h2>
            <p style={{ color: 'var(--text-secondary)' }}>Estamos validando tu transacción con Mercado Pago</p>
        </div>
    );

    if (loading) return <div style={{ height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>Buscando tus tickets...</div>;

    return (
        <div style={{ padding: '140px 5% 60px' }}>
            <header style={{ marginBottom: '50px', textAlign: 'center' }}>
                <h1 className="gradient-text" style={{ fontSize: '3.5rem' }}>Mis Entradas</h1>
                <p style={{ color: 'var(--text-secondary)' }}>Presenta estos QRs en la puerta del bar</p>
            </header>

            {entradas.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '100px 0' }}>
                    <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary)' }}>Aún no tienes entradas compradas.</p>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '30px', maxWidth: '1200px', margin: '0 auto' }}>
                    {entradas.map((entrada, index) => (
                        <motion.div
                            key={entrada.id}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: index * 0.1 }}
                            className="glass"
                            style={{ position: 'relative', overflow: 'hidden' }}
                        >
                            {/* Diseño de Ticket */}
                            <div style={{ padding: '25px', borderBottom: '2px dashed var(--glass-border)' }}>
                                <h3 style={{ fontSize: '1.4rem', marginBottom: '10px' }}>{entrada.evento_titulo}</h3>
                                <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', display: 'flex', flexDirection: 'column', gap: '5px' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Calendar size={14} /> {new Date(entrada.fecha_creacion).toLocaleDateString()}</div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><ScanLine size={14} /> Lote: {entrada.lote_nombre}</div>
                                </div>
                            </div>

                            <div style={{ padding: '30px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px' }}>
                                {/* Imagen del QR */}
                                <div style={{
                                    background: 'white', padding: '15px', borderRadius: '15px', width: '200px', height: '200px',
                                    display: 'flex', alignItems: 'center', justifyContent: 'center'
                                }}>
                                    <img
                                        src={getMediaUrl(entrada.imagen_qr)}
                                        alt="Ticket QR"
                                        style={{ width: '100%', imageRendering: 'pixelated' }}
                                    />
                                </div>

                                <div style={{
                                    background: entrada.usada ? 'rgba(255,255,255,0.05)' : 'rgba(76, 175, 80, 0.1)',
                                    color: entrada.usada ? 'var(--text-secondary)' : '#4caf50',
                                    padding: '8px 20px', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 800
                                }}>
                                    {entrada.usada ? 'YA UTILIZADA' : 'VÁLIDA PARA ENTRAR'}
                                </div>

                                <button
                                    onClick={() => {
                                        const url = getMediaUrl(entrada.imagen_qr);
                                        const link = document.createElement('a');
                                        link.href = url;
                                        link.setAttribute('download', `Ticket_${entrada.evento_titulo}_${entrada.id.substring(0, 8)}.png`);
                                        document.body.appendChild(link);
                                        link.click();
                                        link.remove();
                                    }}
                                    className="download-btn"
                                    style={{
                                        background: 'rgba(255,255,255,0.05)',
                                        border: '1px solid rgba(255,255,255,0.1)',
                                        color: 'white',
                                        padding: '10px 20px',
                                        borderRadius: '12px',
                                        fontSize: '0.8rem',
                                        cursor: 'pointer',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '10px',
                                        transition: 'all 0.3s'
                                    }}
                                >
                                    <Download size={16} /> Guardar QR
                                </button>

                                <small style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontFamily: 'monospace' }}>
                                    ID: {entrada.id.substring(0, 18)}...
                                </small>
                            </div>

                            {/* Decoración de Ticket Circular */}
                            <div style={{ position: 'absolute', width: '30px', height: '30px', background: 'var(--bg-dark)', borderRadius: '50%', left: '-15px', bottom: 'calc(50% + 40px)' }}></div>
                            <div style={{ position: 'absolute', width: '30px', height: '30px', background: 'var(--bg-dark)', borderRadius: '50%', right: '-15px', bottom: 'calc(50% + 40px)' }}></div>
                        </motion.div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default MyTickets;
