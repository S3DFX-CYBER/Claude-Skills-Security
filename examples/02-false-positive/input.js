// static/support.js
// 5. innerHTML, assigned from a build-time config object
document.getElementById('support-link').innerHTML =
  window.__APP_CONFIG__.supportUrl;

// 6. eval(), on a constant expression
const buildFlags = eval('({"beta": true})');
