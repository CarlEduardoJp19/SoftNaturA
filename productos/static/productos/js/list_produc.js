// Búsqueda de productos
document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    const searchStats = document.getElementById('searchStats');
    const cards = document.querySelectorAll('.product-card[data-search-text]');
    const totalCards = cards.length;

    function actualizarEstadisticas() {
        const visibleCards = Array.from(cards).filter(card => card.style.display !== 'none').length;
        if (searchInput.value.trim() === '') {
            searchStats.textContent = `Mostrando ${totalCards} producto${totalCards !== 1 ? 's' : ''}`;
        } else {
            searchStats.textContent = `Encontrados ${visibleCards} de ${totalCards} producto${totalCards !== 1 ? 's' : ''}`;
        }
    }

    if (searchInput) {
        actualizarEstadisticas();
        searchInput.addEventListener('input', function () {
            const searchTerm = this.value.toLowerCase().trim();
            cards.forEach(card => {
                const searchText = card.dataset.searchText || '';
                card.style.display = (searchTerm === '' || searchText.includes(searchTerm)) ? '' : 'none';
            });
            actualizarEstadisticas();
        });
    }
});

function toggleCategorias() {
    const list = document.getElementById("categoryList");
    list.style.display = (list.style.display === "block") ? "none" : "block";
}

function abrirModal(id) {
    // Cerrar todos los modales primero
    document.querySelectorAll('.modal, .modalProduc').forEach(m => {
        m.style.display = "none";
    });
    
    // Abrir el modal solicitado
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = "flex";
        document.body.style.overflow = "hidden";
        
        // Forzar renderizado de inputs (soluciona el bug visual)
        setTimeout(() => {
            modal.querySelectorAll('input, select, textarea').forEach(input => {
                input.style.display = 'block';
                input.style.visibility = 'visible';
                input.style.opacity = '1';
            });
        }, 10);
    }
}

function cerrarModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = "none";
        document.body.style.overflow = "auto";
    }
}

function abrirEditar(element) {
    // Cerrar otros modales primero
    document.querySelectorAll('.modal, .modalProduc').forEach(m => {
        m.style.display = "none";
    });
    
    const modalEditar = document.getElementById("modalEditar");
    const inputNombre = document.getElementById("editNombre");
    const form = document.getElementById("editarForm");
    inputNombre.value = element.getAttribute("data-nombre");
    form.action = element.getAttribute("data-url");
    modalEditar.style.display = "flex";
    document.body.style.overflow = "hidden";
}