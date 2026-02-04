import React, { useState } from 'react';
import api from '../api';
import { motion } from 'framer-motion';
import { User, Mail, Lock, Phone, CreditCard, Calendar } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Register = () => {
    const [formData, setFormData] = useState({
        cedula: '', nombre: '', apellido: '',
        fecha_nacimiento: '', email: '',
        telefono: '', password: '', password_confirm: ''
    });
    const [errors, setErrors] = useState({});
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await api.post('/auth/registro/', formData);
            localStorage.setItem('token', res.data.token.access);
            localStorage.setItem('cliente', JSON.stringify(res.data.cliente));
            window.location.href = '/';
        } catch (err) {
            setErrors(err.response?.data || { general: 'Error al registrarse' });
        }
    };

    const inputStyle = {
        width: '100%', padding: '12px 12px 12px 40px', borderRadius: '10px',
        background: 'rgba(255,255,255,0.05)', border: '1px solid var(--glass-border)',
        color: 'white', fontSize: '0.9rem', outline: 'none'
    };

    const iconStyle = { position: 'absolute', left: '12px', top: '12px', color: 'var(--text-secondary)' };

    return (
        <div style={{ padding: '140px 5% 60px', display: 'flex', justifyContent: 'center' }}>
            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="glass"
                style={{ padding: '35px', width: '100%', maxWidth: '600px' }}
            >
                <h2 style={{ fontSize: '2.2rem', marginBottom: '10px', textAlign: 'center' }}>Crea tu Cuenta</h2>
                <p style={{ color: 'var(--text-secondary)', textAlign: 'center', marginBottom: '25px' }}>Únete a la comunidad de Backyard</p>

                <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                    <div style={{ position: 'relative' }}>
                        <CreditCard style={iconStyle} size={18} />
                        <input type="text" placeholder="Cédula (sin puntos)" required style={inputStyle}
                            onChange={(e) => setFormData({ ...formData, cedula: e.target.value })} />
                        {errors.cedula && <small style={{ color: '#ff4d4d' }}>{errors.cedula[0]}</small>}
                    </div>

                    <div style={{ position: 'relative' }}>
                        <Calendar style={iconStyle} size={18} />
                        <input type="date" required style={inputStyle}
                            onChange={(e) => setFormData({ ...formData, fecha_nacimiento: e.target.value })} />
                        {errors.fecha_nacimiento && <small style={{ color: '#ff4d4d' }}>{errors.fecha_nacimiento[0]}</small>}
                    </div>

                    <div style={{ position: 'relative' }}>
                        <User style={iconStyle} size={18} />
                        <input type="text" placeholder="Nombre" required style={inputStyle}
                            onChange={(e) => setFormData({ ...formData, nombre: e.target.value })} />
                    </div>

                    <div style={{ position: 'relative' }}>
                        <User style={iconStyle} size={18} />
                        <input type="text" placeholder="Apellido" required style={inputStyle}
                            onChange={(e) => setFormData({ ...formData, apellido: e.target.value })} />
                    </div>

                    <div style={{ position: 'relative', gridColumn: 'span 2' }}>
                        <Mail style={iconStyle} size={18} />
                        <input type="email" placeholder="Correo Electrónico" required style={inputStyle}
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })} />
                        {errors.email && <small style={{ color: '#ff4d4d' }}>{errors.email[0]}</small>}
                    </div>

                    <div style={{ position: 'relative' }}>
                        <Phone style={iconStyle} size={18} />
                        <input type="text" placeholder="Teléfono" required style={inputStyle}
                            onChange={(e) => setFormData({ ...formData, telefono: e.target.value })} />
                    </div>

                    <div style={{ position: 'relative' }}>
                        <Lock style={iconStyle} size={18} />
                        <input type="password" placeholder="Contraseña" required style={inputStyle}
                            onChange={(e) => setFormData({ ...formData, password: e.target.value })} />
                    </div>

                    <div style={{ position: 'relative', gridColumn: 'span 2' }}>
                        <Lock style={iconStyle} size={18} />
                        <input type="password" placeholder="Confirmar Contraseña" required style={inputStyle}
                            onChange={(e) => setFormData({ ...formData, password_confirm: e.target.value })} />
                    </div>

                    <button type="submit" style={{
                        gridColumn: 'span 2', background: 'var(--accent)', color: 'black', fontWeight: 800,
                        padding: '14px', borderRadius: '10px', border: 'none', cursor: 'pointer',
                        fontSize: '1rem', marginTop: '10px'
                    }}>
                        REGISTRARSE
                    </button>
                </form>
            </motion.div>
        </div>
    );
};

export default Register;
