import React, { useState } from 'react';
import api from '../api';
import { motion } from 'framer-motion';
import { Mail, Lock, LogIn } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';

const Login = () => {
    const [formData, setFormData] = useState({ email: '', password: '' });
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await api.post('/auth/login/', formData);

            localStorage.setItem('token', res.data.token.access);

            // Guardar datos del perfil (sea cliente o staff)
            const profileData = res.data.cliente || res.data.user;
            localStorage.setItem('cliente', JSON.stringify(profileData));

            window.location.href = '/';
        } catch (err) {
            setError('Credenciales inválidas o error de conexión.');
        }
    };

    return (
        <div style={{ padding: '140px 5% 60px', display: 'flex', justifyContent: 'center' }}>
            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="glass"
                style={{ padding: '40px', width: '100%', maxWidth: '450px' }}
            >
                <h2 style={{ fontSize: '2.5rem', marginBottom: '10px', textAlign: 'center' }}>Bienvenido</h2>
                <p style={{ color: 'var(--text-secondary)', textAlign: 'center', marginBottom: '30px' }}>Ingresa para gestionar tus entradas</p>

                {error && <p style={{ color: '#ff4d4d', textAlign: 'center', marginBottom: '20px' }}>{error}</p>}

                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div style={{ position: 'relative' }}>
                        <Mail style={{ position: 'absolute', left: '15px', top: '15px', color: 'var(--text-secondary)' }} size={20} />
                        <input
                            type="text"
                            placeholder="Email o Usuario"
                            required
                            style={{
                                width: '100%', padding: '15px 15px 15px 45px', borderRadius: '12px',
                                background: 'rgba(255,255,255,0.05)', border: '1px solid var(--glass-border)',
                                color: 'white', fontSize: '1rem', outline: 'none'
                            }}
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        />
                    </div>
                    <div style={{ position: 'relative' }}>
                        <Lock style={{ position: 'absolute', left: '15px', top: '15px', color: 'var(--text-secondary)' }} size={20} />
                        <input
                            type="password"
                            placeholder="Contraseña"
                            required
                            style={{
                                width: '100%', padding: '15px 15px 15px 45px', borderRadius: '12px',
                                background: 'rgba(255,255,255,0.05)', border: '1px solid var(--glass-border)',
                                color: 'white', fontSize: '1rem', outline: 'none'
                            }}
                            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                        />
                    </div>

                    <button type="submit" style={{
                        background: 'var(--accent)', color: 'black', fontWeight: 800, padding: '15px',
                        borderRadius: '12px', border: 'none', cursor: 'pointer', display: 'flex',
                        alignItems: 'center', justifyContent: 'center', gap: '10px', fontSize: '1.1rem'
                    }}>
                        INGRESAR <LogIn size={20} />
                    </button>
                </form>

                <p style={{ marginTop: '30px', textAlign: 'center', color: 'var(--text-secondary)' }}>
                    ¿No tienes cuenta? <Link to="/registro" style={{ color: 'var(--accent)', fontWeight: 600 }}>Regístrate aquí</Link>
                </p>
            </motion.div>
        </div>
    );
};

export default Login;
