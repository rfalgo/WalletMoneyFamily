# WalletMoneyFamily 💰👨‍👩‍👧‍👦

**Gestión inteligente de finanzas familiares** – Una aplicación web para registrar ingresos, gastos, visualizar reportes y compartir el control económico con todos los miembros de la familia.


**Aplicación desplegada**: https://walletmoneyfamily.onrender.com

## 📋 Descripción del proyecto

WalletMoneyFamily es una aplicación web desarrollada con **Flask** que permite a las familias gestionar sus finanzas de forma colaborativa:

- Registro e inicio de sesión seguro (contraseñas hasheadas)
- Registro de ingresos y gastos con título, monto, categoría, fecha, miembro y descripción
- Dashboard con:
  - Saldo total familiar, ingresos, gastos y miembros registrados
  - Tabla de últimos 10 movimientos
  - Gráficos interactivos (barras, pastel y línea) con Chart.js
  - Lista de miembros de la familia
- Eliminación del último movimiento
- Acceso compartido: todos los miembros de la misma familia ven los mismos movimientos

Tecnologías utilizadas:
- Backend: Flask + Flask-Login
- Base de datos: PostgreSQL (persistente en producción)
- Frontend: Bootstrap 5 + Chart.js + Font Awesome
- Despliegue: Render.com (con redeploy automático desde GitHub)

## 🛠️ Instrucciones de instalación (ejecución local)

### Requisitos previos
- Python 3.10 o superior
- Git
- PostgreSQL 

### Pasos

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/rfalgo/WalletMoneyFamily.git