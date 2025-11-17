// src/static/js/dashboard.js
console.log("dashboard.js cargado");

document.addEventListener('DOMContentLoaded', () => {
    const el = document.getElementById('chart-data');
    if (!el) {
        console.error("No se encontró #chart-data");
        return;
    }

    let data;
    try {
        data = {
            meses: JSON.parse(el.dataset.meses || '[]'),
            ingresos: JSON.parse(el.dataset.ingresos || '[]'),
            gastos: JSON.parse(el.dataset.gastos || '[]'),
            categorias: JSON.parse(el.dataset.categorias || '[]'),
            montos: JSON.parse(el.dataset.montos || '[]'),
            fechas: JSON.parse(el.dataset.fechas || '[]'),
            saldo: JSON.parse(el.dataset.saldo || '[]')
        };
        console.log("Datos cargados:", data);
    } catch (e) {
        console.error("Error al parsear JSON:", e);
        return;
    }

    // === GRÁFICO DE BARRAS ===
    if (data.meses.length > 0) {
        new Chart('barChart', {
            type: 'bar',
            data: {
                labels: data.meses,
                datasets: [
                    { label: 'Ingresos', data: data.ingresos, backgroundColor: '#4facfe' },
                    { label: 'Gastos', data: data.gastos, backgroundColor: '#f5576c' }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }

    // === GRÁFICO DE PASTEL ===
    if (data.categorias.length > 0 && data.montos.some(m => m > 0)) {
        new Chart('pieChart', {
            type: 'doughnut',
            data: {
                labels: data.categorias,
                datasets: [{
                    data: data.montos,
                    backgroundColor: ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ffa726']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }

    // === GRÁFICO DE LÍNEA ===
    if (data.fechas.length > 0) {
        new Chart('lineChart', {
            type: 'line',
            data: {
                labels: data.fechas,
                datasets: [{
                    label: 'Saldo',
                    data: data.saldo,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }

    // === CATEGORÍAS DINÁMICAS ===
    const tipoSelect = document.querySelector('select[name="tipo"]');
    if (tipoSelect) {
        toggleForm(tipoSelect);
        tipoSelect.addEventListener('change', () => toggleForm(tipoSelect));
    }
});

function toggleForm(select) {
    const catSelect = document.getElementById('categoria-select');
    const btnIngreso = document.getElementById('btn-ingreso');
    const btnGasto = document.getElementById('btn-gasto');

    const cats = select.value === 'ingreso'
        ? ['Salario', 'Freelance', 'Inversión', 'Regalo', 'Otros']
        : ['Comida', 'Transporte', 'Entretenimiento', 'Salud', 'Educación', 'Otros'];

    catSelect.innerHTML = '';
    cats.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c;
        opt.textContent = c;
        catSelect.appendChild(opt);
    });

    btnIngreso.style.display = select.value === 'ingreso' ? 'block' : 'none';
    btnGasto.style.display = select.value === 'gasto' ? 'block' : 'none';
}