'use strict'

function showTab(tabId) {
    // Fjern 'active' fra alle tabs
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab_content').forEach(content => content.classList.remove('active'));

    // Tilføj 'active' til valgt tab og dens indhold
    document.querySelector(`.tab[onclick="showTab('${tabId}')"]`).classList.add('active');
    document.getElementById(tabId).classList.add('active');
}