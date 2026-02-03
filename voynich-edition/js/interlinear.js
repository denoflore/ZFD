/**
 * Interlinear View Controller for Voynich Digital Edition
 * Phase 5: Toggle between EVA and Glagolitic views
 */

(function() {
    'use strict';

    // Current view state
    let currentView = 'eva';

    /**
     * Initialize interlinear view toggles
     */
    function initInterlinearToggle() {
        const toggleContainer = document.querySelector('.view-toggle');
        if (!toggleContainer) return;

        const buttons = toggleContainer.querySelectorAll('button');
        buttons.forEach(btn => {
            btn.addEventListener('click', function() {
                const view = this.dataset.view;
                if (view) {
                    switchView(view);
                    updateToggleButtons(this);
                }
            });
        });
    }

    /**
     * Switch between EVA and Glagolitic views
     */
    function switchView(view) {
        currentView = view;

        // Hide all layer views
        const allViews = document.querySelectorAll('.layer-view');
        allViews.forEach(v => v.classList.remove('active'));

        // Show selected view
        const targetView = document.querySelector(`.layer-view.${view}-view`);
        if (targetView) {
            targetView.classList.add('active');
        }

        // Update five-layer displays if present
        const fiveLayers = document.querySelectorAll('.interlinear-five-layer');
        fiveLayers.forEach(container => {
            const layers = container.querySelectorAll('.layer-row');
            layers.forEach(layer => {
                // Show/hide based on view preference
                if (view === 'eva') {
                    // EVA view: show EVA, Croatian, English
                    layer.classList.toggle('hidden',
                        layer.classList.contains('layer-glagolitic') ||
                        layer.classList.contains('layer-latin')
                    );
                } else if (view === 'glagolitic') {
                    // Glagolitic view: show all five layers
                    layer.classList.remove('hidden');
                } else if (view === 'compact') {
                    // Compact: EVA and English only
                    layer.classList.toggle('hidden',
                        !layer.classList.contains('layer-eva') &&
                        !layer.classList.contains('layer-english')
                    );
                }
            });
        });

        // Store preference
        try {
            localStorage.setItem('voynich-view-preference', view);
        } catch (e) {
            // localStorage not available
        }
    }

    /**
     * Update toggle button active states
     */
    function updateToggleButtons(activeButton) {
        const buttons = document.querySelectorAll('.view-toggle button');
        buttons.forEach(btn => btn.classList.remove('active'));
        activeButton.classList.add('active');
    }

    /**
     * Apply confidence-based word styling
     */
    function applyConfidenceStyles() {
        const words = document.querySelectorAll('[data-confidence]');
        words.forEach(word => {
            const conf = parseFloat(word.dataset.confidence);
            word.classList.remove('word-high-conf', 'word-med-conf', 'word-low-conf');

            if (conf > 0.8) {
                word.classList.add('word-high-conf');
            } else if (conf >= 0.5) {
                word.classList.add('word-med-conf');
            } else {
                word.classList.add('word-low-conf');
            }
        });
    }

    /**
     * Create word tooltips with transliteration details
     */
    function initWordTooltips() {
        const words = document.querySelectorAll('.transliterated-word');
        words.forEach(word => {
            const eva = word.dataset.eva || '';
            const glagolitic = word.dataset.glagolitic || '';
            const latin = word.dataset.latin || '';
            const conf = word.dataset.confidence || '';

            const tooltip = `EVA: ${eva}\nGlag: ${glagolitic}\nLatin: ${latin}\nConf: ${(parseFloat(conf) * 100).toFixed(0)}%`;
            word.setAttribute('data-tooltip', tooltip);
            word.classList.add('word-tooltip');
        });
    }

    /**
     * Restore view preference from localStorage
     */
    function restoreViewPreference() {
        try {
            const saved = localStorage.getItem('voynich-view-preference');
            if (saved) {
                const btn = document.querySelector(`.view-toggle button[data-view="${saved}"]`);
                if (btn) {
                    btn.click();
                }
            }
        } catch (e) {
            // localStorage not available
        }
    }

    /**
     * Render five-layer interlinear block from data
     */
    function renderFiveLayerBlock(lineData) {
        const layers = lineData.layers || {};
        const lineNum = lineData.line_num || '';
        const confidence = lineData.confidence_avg || 0;

        let confClass = 'high';
        if (confidence < 0.5) confClass = 'low';
        else if (confidence < 0.8) confClass = 'medium';

        return `
            <div class="transcription-line">
                <span class="line-number">Line ${lineNum}</span>
                <span class="line-confidence ${confClass}">${(confidence * 100).toFixed(0)}%</span>
                <div class="interlinear-five-layer">
                    <div class="layer-row layer-eva">
                        <span class="layer-label">EVA</span>
                        <span class="layer-content">${escapeHtml(layers.eva || '')}</span>
                    </div>
                    <div class="layer-row layer-glagolitic">
                        <span class="layer-label">Glagolitic</span>
                        <span class="layer-content">${escapeHtml(layers.glagolitic || '')}</span>
                    </div>
                    <div class="layer-row layer-latin">
                        <span class="layer-label">Latin</span>
                        <span class="layer-content">${escapeHtml(layers.latin || '')}</span>
                    </div>
                    <div class="layer-row layer-croatian">
                        <span class="layer-label">Croatian</span>
                        <span class="layer-content">${escapeHtml(layers.croatian_short || '')}</span>
                    </div>
                    <div class="layer-row layer-english">
                        <span class="layer-label">English</span>
                        <span class="layer-content">${escapeHtml(layers.croatian_expanded || '')}</span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Escape HTML special characters
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Load and render Glagolitic transcription for a folio
     */
    async function loadGlagoliticTranscription(folioId, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        try {
            // Try to load from embedded data first
            if (window.glagoliticTranscription) {
                renderTranscription(window.glagoliticTranscription, container);
                return;
            }

            // Otherwise fetch from JSON file
            const response = await fetch(`../../06_Pipelines/glagolitic_ocr/transcriptions/json/${folioId}.json`);
            if (!response.ok) {
                container.innerHTML = '<p class="text-muted">Glagolitic transcription not available.</p>';
                return;
            }

            const data = await response.json();
            renderTranscription(data, container);

        } catch (error) {
            console.warn('Could not load Glagolitic transcription:', error);
            container.innerHTML = '<p class="text-muted">Glagolitic transcription not available.</p>';
        }
    }

    /**
     * Render transcription data into container
     */
    function renderTranscription(data, container) {
        if (!data.lines || data.lines.length === 0) {
            container.innerHTML = '<p class="text-muted">No transcription lines available.</p>';
            return;
        }

        let html = '';
        data.lines.forEach(line => {
            html += renderFiveLayerBlock(line);
        });

        container.innerHTML = html;

        // Apply styling
        applyConfidenceStyles();
        initWordTooltips();
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        initInterlinearToggle();
        applyConfidenceStyles();
        initWordTooltips();
        restoreViewPreference();
    }

    // Export functions for external use
    window.VoynichInterlinear = {
        switchView: switchView,
        loadGlagoliticTranscription: loadGlagoliticTranscription,
        renderFiveLayerBlock: renderFiveLayerBlock
    };

})();
