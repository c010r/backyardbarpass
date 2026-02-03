import React from 'react';
import { Link } from 'react-router-dom';
import { Ticket, User, LogOut, ScanLine, BarChart3 } from 'lucide-react';
import { motion } from 'framer-motion';

const Navbar = () => {
    const token = localStorage.getItem('token');

    // Nota: El backend debe incluir 'is_staff' y 'is_superuser' en el payload del JWT
    // o podemos basarnos en el user_id para determinar los roles.

    // Función para verificar si el usuario es Staff
    const isStaff = () => {
        if (!token) return false;
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            // Buscamos la propiedad is_staff en el payload del JWT
            return payload.is_staff === true;
        } catch (e) {
            return false;
        }
    };

    const isSuperuser = () => {
        if (!token) return false;
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            // Buscamos el flag is_superuser en el token
            return payload.is_superuser === true;
        } catch (e) {
            return false;
        }
    };

    return (
        <nav className="glass" style={{
            position: 'fixed',
            top: '20px',
            left: '50%',
            transform: 'translateX(-50%)',
            width: '90%',
            maxWidth: '1200px',
            height: '70px',
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 30px'
        }}>
            <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <motion.div
                    whileHover={{ rotate: 15 }}
                    style={{ background: 'var(--accent)', padding: '8px', borderRadius: '12px' }}
                >
                    <Ticket size={24} color="black" />
                </motion.div>
                <span style={{ fontSize: '1.5rem', fontWeight: 800, letterSpacing: '1px' }}>
                    BACKYARD<span style={{ color: 'var(--accent)' }}>PASS</span>
                </span>
            </Link>

            <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
                {token ? (
                    <>
                        {isStaff() && (
                            <>
                                {isSuperuser() && (
                                    <Link to="/dashboard" className="nav-link" style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '5px'
                                    }}>
                                        <BarChart3 size={18} /> Dashboard
                                    </Link>
                                )}
                                <Link to="/scanner" className="nav-link" style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '5px',
                                    color: 'var(--accent)'
                                }}>
                                    <ScanLine size={18} /> Scanner Staff
                                </Link>
                            </>
                        )}
                        {!isStaff() && (
                            <Link to="/mis-entradas" className="nav-link">Mis Entradas</Link>
                        )}
                        <button
                            onClick={() => { localStorage.clear(); window.location.href = '/'; }}
                            style={{
                                background: 'transparent',
                                border: '1px solid var(--glass-border)',
                                color: 'white',
                                padding: '8px 15px',
                                borderRadius: '10px',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px'
                            }}
                        >
                            <LogOut size={16} /> Salir
                        </button>
                    </>
                ) : (
                    <Link to="/login" style={{
                        background: 'var(--accent)',
                        color: 'black',
                        fontWeight: 700,
                        padding: '10px 25px',
                        borderRadius: '12px',
                        transition: '0.3s'
                    }}>
                        Ingresar
                    </Link>
                )}
            </div>
        </nav>
    );
};

export default Navbar;
