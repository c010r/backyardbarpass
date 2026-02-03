import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api, { getMediaUrl } from '../api';
import { motion } from 'framer-motion';
import { Calendar, MapPin, ShieldCheck, ChevronRight } from 'lucide-react';

const EventDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [evento, setEvento] = useState(null);
    const [cantidad, setCantidad] = useState(1);
    const [loading, setLoading] = useState(true);
    const [comprando, setComprando] = useState(false);

    useEffect(() => {
        api.get(`/eventos/${id}/`)
            .then(res => {
                setEvento(res.data);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                navigate('/');
            });
    }, [id, navigate]);

    const handleComprar = async () => {
        const token = localStorage.getItem('token');
        if (!token) {
            navigate('/login');
            return;
        }

        setComprando(true);
        try {
            const res = await api.post('/compras/reservar/', {
                evento_id: parseInt(id),
                cantidad: cantidad
            });

            const mpInitPoint = res.data.mp_init_point;
            const mpPreferenceId = res.data.mp_preference_id;

            if (mpInitPoint) {
                // Redirigir usando el punto de inicio proporcionado por MP (vía backend)
                window.location.href = mpInitPoint;
            } else if (mpPreferenceId) {
                // Fallback a URL manual si por alguna razón no viene el point
                window.location.href = `https://www.mercadopago.com.uy/checkout/v1/redirect?pref_id=${mpPreferenceId}`;
            } else {
                throw new Error("No se pudo generar la preferencia de pago.");
            }

        } catch (err) {
            const errorMsg = err.response?.data?.error || err.response?.data?.detail || err.message || 'Error desconocido';
            alert(`Error: ${errorMsg}`);
            setComprando(false);
        }
    };

    if (loading) return <div style={{ height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>Cargando evento...</div>;

    const loteActual = evento.lotes.find(l => l.activo && l.stock_disponible > 0);

    return (
        <div style={{ padding: '120px 5% 60px' }}>
            <div style={{ maxWidth: '1100px', margin: '0 auto', display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '50px' }}>

                <motion.div initial={{ opacity: 0, x: -30 }} animate={{ opacity: 1, x: 0 }}>
                    <div style={{ borderRadius: '25px', overflow: 'hidden', height: '400px', marginBottom: '30px', border: '1px solid var(--glass-border)' }}>
                        <img src={getMediaUrl(evento.imagen) || 'https://images.unsplash.com/photo-1540039155733-5bb30b53aa14?auto=format&fit=crop&w=1000&q=80'}
                            alt={evento.titulo} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    </div>
                    <h1 style={{ fontSize: '3rem', marginBottom: '20px' }}>{evento.titulo}</h1>
                    <div style={{ display: 'flex', gap: '30px', marginBottom: '30px', color: 'var(--text-secondary)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Calendar size={20} color="var(--accent)" /> {new Date(evento.fecha_inicio).toLocaleDateString()}</div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><MapPin size={20} color="var(--accent)" /> {evento.ubicacion}</div>
                    </div>
                    <p style={{ fontSize: '1.2rem', lineHeight: '1.8', color: 'var(--text-secondary)' }}>{evento.descripcion}</p>
                </motion.div>

                <motion.div initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }}>
                    <div className="glass" style={{ padding: '40px', position: 'sticky', top: '120px' }}>
                        <h2 style={{ marginBottom: '25px', fontSize: '1.8rem' }}>Reserva tu lugar</h2>

                        {!loteActual ? (
                            <div style={{ padding: '20px', background: 'rgba(255,0,0,0.1)', borderRadius: '15px', color: '#ff4d4d', textAlign: 'center', fontWeight: 700 }}>
                                ¡ENTRADAS AGOTADAS!
                            </div>
                        ) : (
                            <>
                                <div style={{ marginBottom: '30px' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                                        <span style={{ fontWeight: 600 }}>{loteActual.nombre}</span>
                                        <span style={{ color: 'var(--accent)', fontWeight: 800, fontSize: '1.2rem' }}>${loteActual.precio}</span>
                                    </div>
                                    <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Quedan {loteActual.stock_disponible} disponibles</p>
                                </div>

                                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '30px', background: 'rgba(255,255,255,0.05)', padding: '15px', borderRadius: '15px' }}>
                                    <span>Cantidad</span>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                                        <button onClick={() => setCantidad(Math.max(1, cantidad - 1))} style={{ background: 'transparent', border: '1px solid var(--glass-border)', color: 'white', width: '35px', height: '35px', borderRadius: '50%', cursor: 'pointer' }}>-</button>
                                        <span style={{ fontSize: '1.2rem', fontWeight: 700 }}>{cantidad}</span>
                                        <button onClick={() => setCantidad(Math.min(loteActual.stock_disponible, 10, cantidad + 1))} style={{ background: 'transparent', border: '1px solid var(--glass-border)', color: 'white', width: '35px', height: '35px', borderRadius: '50%', cursor: 'pointer' }}>+</button>
                                    </div>
                                </div>

                                <div style={{ borderTop: '1px solid var(--glass-border)', paddingTop: '20px', marginBottom: '30px' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px', fontSize: '1.1rem' }}>
                                        <span>Total</span>
                                        <span style={{ fontWeight: 800, color: 'var(--accent)' }}>${(loteActual.precio * cantidad).toFixed(2)}</span>
                                    </div>
                                    {evento.cobra_comision && <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>* Incluye costos de servicio</p>}
                                </div>

                                <button
                                    onClick={handleComprar}
                                    disabled={comprando}
                                    style={{
                                        width: '100%', background: 'var(--accent)', color: 'black', fontWeight: 800,
                                        padding: '18px', borderRadius: '15px', border: 'none', cursor: 'pointer',
                                        fontSize: '1.1rem', transition: '0.3s', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px'
                                    }}
                                >
                                    {comprando ? 'PROCESANDO...' : 'COMPRAR AHORA'} <ChevronRight size={20} />
                                </button>

                                <div style={{ marginTop: '25px', display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                                    <ShieldCheck size={16} /> Pago seguro vía Mercado Pago
                                </div>
                            </>
                        )}
                    </div>
                </motion.div>
            </div>
        </div>
    );
};

export default EventDetail;
