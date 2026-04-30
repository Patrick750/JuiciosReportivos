<template>
  <aside class="sidebar">
    <!-- Logo -->
    <div class="sidebar-logo">
      <div class="logo-icon">🌿</div>
      <div>
        <div class="logo-title">Juicios</div>
        <div class="logo-sub">Evaluativos SENA</div>
      </div>
    </div>

    <!-- Nav -->
    <nav class="sidebar-nav">
      <div class="nav-section-label">Principal</div>
      <RouterLink to="/dashboard" class="nav-item">
        <span class="nav-icon">📊</span>
        <span>Dashboard</span>
      </RouterLink>
      <RouterLink to="/importar" class="nav-item">
        <span class="nav-icon">📥</span>
        <span>Importar Reporte</span>
      </RouterLink>

      <div class="nav-section-label mt-24">Análisis</div>
      <RouterLink to="/dashboard-fases" class="nav-item">
        <span class="nav-icon">🏁</span>
        <span>Dashboard Fases</span>
      </RouterLink>

      <div class="nav-section-label mt-24">Configuración</div>
      <RouterLink to="/proyecto-formativo" class="nav-item">
        <span class="nav-icon">🗂️</span>
        <span>Proyecto Formativo</span>
      </RouterLink>
    </nav>

    <div class="sidebar-footer">
      <div class="footer-badge">SENA v1.0</div>
    </div>
  </aside>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.sidebar {
  width: var(--sidebar-w);
  min-width: var(--sidebar-w);
  background: var(--bg-card);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  position: relative;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px 20px 20px;
  border-bottom: 1px solid var(--border);
}
.logo-icon { font-size: 1.8rem; line-height: 1; }
.logo-title { font-size: 1rem; font-weight: 800; color: var(--text); }
.logo-sub   { font-size: 0.7rem; color: var(--sena-green); font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; }

.sidebar-nav { flex: 1; padding: 16px 12px; }
.nav-section-label {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  color: var(--text-muted);
  padding: 0 8px;
  margin-bottom: 6px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all var(--transition);
  margin-bottom: 2px;
}
.nav-item:hover { background: rgba(255,255,255,0.05); color: var(--text); }
.nav-item.router-link-active {
  background: rgba(57,169,0,0.12);
  color: var(--sena-green);
  font-weight: 600;
}
.nav-icon { font-size: 1rem; width: 20px; text-align: center; }

.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid var(--border);
}
.footer-badge {
  font-size: 0.7rem;
  color: var(--text-muted);
  background: var(--bg-card2);
  border: 1px solid var(--border);
  border-radius: 99px;
  padding: 4px 12px;
  display: inline-block;
  letter-spacing: 0.5px;
}
</style>
