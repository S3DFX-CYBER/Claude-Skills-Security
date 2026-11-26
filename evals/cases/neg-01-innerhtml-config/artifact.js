// Build-time injected config, not user input.
const cfg = window.__APP_CONFIG__;
document.getElementById('docs').innerHTML = cfg.docsMarkup;
document.getElementById('ver').textContent = cfg.version;
