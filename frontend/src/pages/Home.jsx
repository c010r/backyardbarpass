import React, { useEffect, useState } from 'react';
import api, { getMediaUrl } from '../api';
import { motion } from 'framer-motion';
import { Calendar, MapPin, ArrowRight } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

const Home = () => {
    const [eventos, setEventos] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        // Redirección basada en roles para Staff y Superuser
        const token = localStorage.getItem('token');
        if (token) {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                if (payload.is_staff) {
                    if (payload.is_superuser) {
                        navigate('/dashboard');
                    } else {
                        navigate('/scanner');
                    }
                    return;
                }
            } catch (e) {
                console.error("Token inválido");
            }
        }

        api.get('/eventos/')
            .then(res => {
                setEventos(res.data.results);
                setLoading(false);
            })
            .catch(err => {
                console.error("Error cargando eventos:", err);
                setLoading(false);
            });
    }, []);

    if (loading) return <div style={{ height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>Cargando eventos...</div>;

    return (
        <div style={{ padding: '140px 5% 60px' }}>
            <header style={{ marginBottom: '60px', textAlign: 'center' }}>
                <motion.h1
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="gradient-text"
                    style={{ fontSize: '4rem', marginBottom: '10px' }}
                >
                    Próximos Eventos
                </motion.h1>
                <p style={{ color: 'var(--text-secondary)', fontSize: '1.2rem' }}>Reserva tu lugar en las mejores noches de Montevideo</p>
            </header>

            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
                gap: '40px',
                maxWidth: '1200px',
                margin: '0 auto'
            }}>
                {eventos.map((evento, index) => (
                    <motion.div
                        key={evento.id}
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="glass"
                        style={{ overflow: 'hidden', cursor: 'pointer' }}
                        whileHover={{ y: -10, boxShadow: '0 20px 40px rgba(0,0,0,0.4)' }}
                    >
                        <div style={{ height: '220px', background: '#222', position: 'relative' }}>
                            {evento.imagen ? (
                                <img src={getMediaUrl(evento.imagen)} alt={evento.titulo} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                            ) : (
                                <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#444' }}>
                                    Sin imagen disponible
                                </div>
                            )}
                            <div style={{
                                position: 'absolute', top: '20px', right: '20px',
                                background: 'var(--accent)', color: 'black',
                                padding: '5px 15px', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 700
                            }}>
                                DISPONIBLE
                            </div>
                        </div>

                        <div style={{ padding: '25px' }}>
                            <h3 style={{ fontSize: '1.6rem', marginBottom: '15px' }}>{evento.titulo}</h3>

                            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', color: 'var(--text-secondary)', marginBottom: '25px' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                    <Calendar size={18} color="var(--accent)" />
                                    {new Date(evento.fecha_inicio).toLocaleDateString('es-UY', { weekday: 'long', day: 'numeric', month: 'long' })}
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                    <MapPin size={18} color="var(--accent)" />
                                    {evento.ubicacion}
                                </div>
                            </div>

                            <Link to={`/evento/${evento.id}`} style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                background: 'rgba(255,255,255,0.05)',
                                padding: '15px 20px',
                                borderRadius: '15px',
                                fontWeight: 600,
                                border: '1px solid var(--glass-border)',
                                transition: '0.3s'
                            }}>
                                Ver Entradas <ArrowRight size={20} />
                            </Link>
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    );
};

export default Home;
