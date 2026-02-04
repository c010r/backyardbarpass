import React, { useState, useEffect, useRef } from 'react';
import { Html5QrcodeScanner, Html5QrcodeSupportedFormats } from 'html5-qrcode';
import api from '../api';

const Scanner = () => {
    const [scanResult, setScanResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [isScanning, setIsScanning] = useState(true);
    const scannerRef = useRef(null);

    useEffect(() => {
        // Inicializar el scanner
        const scanner = new Html5QrcodeScanner('reader', {
            fps: 10,
            qrbox: { width: 250, height: 250 },
            rememberLastUsedCamera: true,
            supportedScanTypes: [Html5QrcodeSupportedFormats.QR_CODE]
        });

        scanner.render(onScanSuccess, onScanError);
        scannerRef.current = scanner;

        return () => {
            if (scannerRef.current) {
                scannerRef.current.clear().catch(err => console.error("Error clearing scanner", err));
            }
        };
    }, []);

    const onScanSuccess = async (decodedText) => {
        if (loading) return;

        // Pausar escaneo visualmente (limpiando el resultado anterior)
        setScanResult(null);
        setError(null);

        try {
            setLoading(true);
            const response = await api.post('/validar-entrada/', {
                codigo_qr: decodedText
            });

            setScanResult(response.data);

            // Si es válido, emitir un sonido de éxito (opcional)
            if (response.data.es_valida) {
                playBeep(true);
            } else {
                playBeep(false);
            }

        } catch (err) {
            setError(err.response?.data?.error || "Error al validar el código");
            playBeep(false);
        } finally {
            setLoading(false);
        }
    };

    const onScanError = (err) => {
        // Errores de escaneo continuo se ignoran normalmente
        // console.warn(err);
    };

    const playBeep = (success) => {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);

        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(success ? 880 : 220, audioCtx.currentTime); // A5 para éxito, A3 para fallo
        gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);

        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.2);
    };

    const resetScanner = () => {
        setScanResult(null);
        setError(null);
    };

    return (
        <div className="scanner-container">
            <div className="scanner-header">
                <h1>Validador de Entradas</h1>
                <p>Scanner Oficial - Backyard Bar</p>
            </div>

            <div className="scanner-body">
                <div id="reader" style={{ width: '100%', maxWidth: '500px', margin: '0 auto' }}></div>

                {loading && (
                    <div className="scan-overlay">
                        <div className="loader"></div>
                        <p>Validando...</p>
                    </div>
                )}

                {scanResult && (
                    <div className={`result-card ${scanResult.es_valida ? 'success' : 'warning'}`}>
                        <div className="result-icon">
                            {scanResult.es_valida ? '✅' : '⚠️'}
                        </div>
                        <h2>{scanResult.mensaje}</h2>
                        <div className="result-details">
                            <p><strong>Cliente:</strong> {scanResult.detalle.cliente_nombre}</p>
                            <p><strong>Cédula:</strong> {scanResult.detalle.cliente_cedula}</p>
                            <p><strong>Lote:</strong> {scanResult.detalle.lote_nombre}</p>
                            {scanResult.detalle.fecha_uso && (
                                <p className="usage-time">
                                    Usada el: {new Date(scanResult.detalle.fecha_uso).toLocaleString()}
                                </p>
                            )}
                        </div>
                        <button className="reset-btn" onClick={resetScanner}>Siguiente Escaneo</button>
                    </div>
                )}

                {error && (
                    <div className="result-card error">
                        <div className="result-icon">❌</div>
                        <h2>Error</h2>
                        <p>{error}</p>
                        <button className="reset-btn" onClick={resetScanner}>Reintentar</button>
                    </div>
                )}
            </div>

            <style jsx>{`
                .scanner-container {
                    padding: 20px;
                    max-width: 600px;
                    margin: 0 auto;
                    font-family: 'Inter', sans-serif;
                    background: #0f172a;
                    min-height: 100vh;
                    color: white;
                }

                .scanner-header {
                    text-align: center;
                    margin-bottom: 30px;
                }

                .scanner-header h1 {
                    font-size: 1.8rem;
                    margin-bottom: 5px;
                    background: linear-gradient(to right, #60a5fa, #a855f7);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }

                .scanner-header p {
                    color: #94a3b8;
                    font-size: 0.9rem;
                }

                .scanner-body {
                    position: relative;
                    background: #1e293b;
                    padding: 20px;
                    border-radius: 20px;
                    box-shadow: 0 10px 25px rgba(0,0,0,0.3);
                }

                #reader {
                    border-radius: 15px;
                    overflow: hidden;
                    border: 2px solid #334155 !important;
                }

                #reader__scan_region {
                    background: #000;
                }

                /* Estética de html5-qrcode */
                #reader button {
                    background: #3b82f6;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 8px;
                    margin: 10px;
                    font-weight: 600;
                    cursor: pointer;
                }

                .scan-overlay {
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(15, 23, 42, 0.8);
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    border-radius: 20px;
                    z-index: 10;
                }

                .loader {
                    border: 4px solid #334155;
                    border-top: 4px solid #3b82f6;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                    margin-bottom: 15px;
                }

                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }

                .result-card {
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    border-radius: 20px;
                    padding: 30px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    text-align: center;
                    z-index: 11;
                    animation: slideIn 0.3s ease-out;
                }

                @keyframes slideIn {
                    from { transform: translateY(20px); opacity: 0; }
                    to { transform: translateY(0); opacity: 1; }
                }

                .result-card.success { background: #065f46; }
                .result-card.warning { background: #92400e; }
                .result-card.error { background: #991b1b; }

                .result-icon {
                    font-size: 4rem;
                    margin-bottom: 15px;
                }

                .result-card h2 {
                    font-size: 1.5rem;
                    margin-bottom: 20px;
                }

                .result-details {
                    background: rgba(0,0,0,0.2);
                    padding: 15px;
                    border-radius: 12px;
                    width: 100%;
                    margin-bottom: 25px;
                    text-align: left;
                }

                .result-details p {
                    margin: 5px 0;
                    font-size: 1rem;
                }

                .usage-time {
                    font-size: 0.85rem !important;
                    color: #fca5a5;
                    margin-top: 10px !important;
                    border-top: 1px solid rgba(255,255,255,0.1);
                    padding-top: 10px;
                }

                .reset-btn {
                    background: white;
                    color: #0f172a;
                    border: none;
                    padding: 12px 30px;
                    border-radius: 12px;
                    font-weight: 700;
                    font-size: 1rem;
                    cursor: pointer;
                    transition: transform 0.2s;
                }

                .reset-btn:active {
                    transform: scale(0.95);
                }
            `}</style>
        </div>
    );
};

export default Scanner;
