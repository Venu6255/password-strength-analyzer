// Password Strength Analyzer - JavaScript Functions
class PasswordAnalyzer {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.initTooltips();
    }

    bindEvents() {
        // Password analyzer events
        const passwordInput = document.getElementById('passwordInput');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const clearBtn = document.getElementById('clearBtn');
        const togglePassword = document.getElementById('togglePassword');
        const viewDetailsBtn = document.getElementById('viewDetailsBtn');

        // Wordlist generator events
        const generateBtn = document.getElementById('generateBtn');
        const clearWordlistBtn = document.getElementById('clearWordlistBtn');
        const downloadBtn = document.getElementById('downloadBtn');

        // Password input events
        if (passwordInput) {
            passwordInput.addEventListener('input', this.debounce(() => {
                this.handlePasswordInput();
            }, 300));

            passwordInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.analyzePassword();
                }
            });
        }

        // Button events
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.analyzePassword());
        }

        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearPassword());
        }

        if (togglePassword) {
            togglePassword.addEventListener('click', () => this.togglePasswordVisibility());
        }

        if (viewDetailsBtn) {
            viewDetailsBtn.addEventListener('click', () => this.showDetailedAnalysis());
        }

        if (generateBtn) {
            generateBtn.addEventListener('click', () => this.generateWordlist());
        }

        if (clearWordlistBtn) {
            clearWordlistBtn.addEventListener('click', () => this.clearWordlistForm());
        }

        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => this.downloadWordlist());
        }

        // Smooth scrolling for navigation links
        document.querySelectorAll('.smooth-scroll').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Auto-resize textareas
        document.querySelectorAll('textarea').forEach(textarea => {
            textarea.addEventListener('input', this.autoResize);
        });
    }

    // Password Analysis Functions
    async analyzePassword() {
        const passwordInput = document.getElementById('passwordInput');
        const password = passwordInput.value.trim();

        if (!password) {
            this.showToast('Please enter a password to analyze', 'error');
            passwordInput.focus();
            return;
        }

        try {
            this.showLoading(true);
            
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ password: password })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.displayAnalysisResults(data.analysis);
                this.currentAnalysis = data.analysis; // Store for detailed view
            } else {
                this.showToast(data.error || 'Analysis failed', 'error');
            }
        } catch (error) {
            console.error('Analysis error:', error);
            this.showToast('Network error occurred', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    displayAnalysisResults(analysis) {
        // Show results container
        const resultsContainer = document.getElementById('analysisResults');
        const emptyState = document.getElementById('emptyState');
        
        if (resultsContainer && emptyState) {
            resultsContainer.classList.remove('d-none');
            emptyState.classList.add('d-none');
        }

        // Update strength score and bar
        const strengthScore = document.getElementById('strengthScore');
        const strengthBar = document.getElementById('strengthBar');
        const strengthLabel = document.getElementById('strengthLabel');

        if (strengthScore) {
            strengthScore.textContent = analysis.strength_score + '%';
            strengthScore.className = `badge bg-${analysis.strength_color}`;
        }

        if (strengthBar) {
            strengthBar.style.width = analysis.strength_score + '%';
            strengthBar.className = `progress-bar progress-bar-striped progress-bar-animated bg-${analysis.strength_color}`;
        }

        if (strengthLabel) {
            strengthLabel.textContent = analysis.strength_label;
        }

        // Update entropy and length
        const entropyValue = document.getElementById('entropyValue');
        const lengthValue = document.getElementById('lengthValue');

        if (entropyValue) {
            entropyValue.textContent = analysis.entropy;
        }

        if (lengthValue) {
            lengthValue.textContent = analysis.length;
        }

        // Update character indicators
        this.updateCharacterIndicators(analysis.character_analysis);

        // Add animation to results
        resultsContainer.style.opacity = '0';
        setTimeout(() => {
            resultsContainer.style.transition = 'opacity 0.5s ease';
            resultsContainer.style.opacity = '1';
        }, 100);
    }

    updateCharacterIndicators(charAnalysis) {
        const indicators = {
            'lowercaseInd': charAnalysis.has_lowercase,
            'uppercaseInd': charAnalysis.has_uppercase,
            'digitInd': charAnalysis.has_digits,
            'specialInd': charAnalysis.has_special
        };

        Object.entries(indicators).forEach(([id, hasChar]) => {
            const element = document.getElementById(id);
            if (element) {
                element.className = hasChar ? 'indicator active' : 'indicator inactive';
            }
        });
    }

    showDetailedAnalysis() {
        if (!this.currentAnalysis) {
            this.showToast('No analysis data available', 'error');
            return;
        }

        const modal = new bootstrap.Modal(document.getElementById('detailsModal'));
        const content = document.getElementById('detailsContent');
        
        if (content) {
            content.innerHTML = this.generateDetailedAnalysisHTML(this.currentAnalysis);
        }
        document.getElementById('loadingOverlay').classList.remove('show');
        modal.show();
    }

    generateDetailedAnalysisHTML(analysis) {
        return `
            <div class="detailed-analysis">
                <div class="row mb-4">
                    <div class="col-md-6">
                        <h6 class="fw-bold">Password Metrics</h6>
                        <ul class="list-unstyled">
                            <li><strong>Length:</strong> ${analysis.length} characters</li>
                            <li><strong>Entropy:</strong> ${analysis.entropy} bits</li>
                            <li><strong>Unique Characters:</strong> ${analysis.character_analysis.unique_chars}</li>
                            <li><strong>Character Diversity:</strong> ${Math.round(analysis.character_analysis.char_diversity * 100)}%</li>
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <h6 class="fw-bold">Time to Crack</h6>
                        <p class="lead">${analysis.time_to_crack}</p>
                        <h6 class="fw-bold">Strength Score</h6>
                        <p class="lead">${analysis.strength_score}% - ${analysis.strength_label}</p>
                    </div>
                </div>

                <div class="row mb-4">
                    <div class="col-md-6">
                        <h6 class="fw-bold text-danger">Detected Issues</h6>
                        ${this.generatePatternIssuesHTML(analysis.pattern_analysis)}
                    </div>
                    <div class="col-md-6">
                        <h6 class="fw-bold text-success">Recommendations</h6>
                        <ul class="list-unstyled">
                            ${analysis.recommendations.map(rec => `<li><i class="bi bi-check-circle text-success me-2"></i>${rec}</li>`).join('')}
                        </ul>
                    </div>
                </div>

                ${analysis.zxcvbn_analysis ? this.generateZxcvbnHTML(analysis.zxcvbn_analysis) : ''}

                <div class="text-muted small mt-4">
                    <i class="bi bi-clock me-1"></i>Analysis completed on ${analysis.analysis_timestamp}
                </div>
            </div>
        `;
    }

    generatePatternIssuesHTML(patternAnalysis) {
        const issues = [];
        
        if (patternAnalysis.has_common_patterns && patternAnalysis.has_common_patterns.length > 0) {
            issues.push(`Common patterns: ${patternAnalysis.has_common_patterns.join(', ')}`);
        }
        
        if (patternAnalysis.has_keyboard_patterns && patternAnalysis.has_keyboard_patterns.length > 0) {
            issues.push(`Keyboard patterns: ${patternAnalysis.has_keyboard_patterns.join(', ')}`);
        }
        
        if (patternAnalysis.has_repeated_chars && patternAnalysis.has_repeated_chars.length > 0) {
            issues.push(`Repeated characters: ${patternAnalysis.has_repeated_chars.join(', ')}`);
        }
        
        if (patternAnalysis.has_sequential_chars && patternAnalysis.has_sequential_chars.length > 0) {
            issues.push(`Sequential characters: ${patternAnalysis.has_sequential_chars.join(', ')}`);
        }
        
        if (patternAnalysis.contains_dictionary_words && patternAnalysis.contains_dictionary_words.length > 0) {
            issues.push(`Dictionary words: ${patternAnalysis.contains_dictionary_words.join(', ')}`);
        }

        if (issues.length === 0) {
            return '<p class="text-success"><i class="bi bi-check-circle me-2"></i>No major pattern issues detected</p>';
        }

        return `<ul class="list-unstyled">${issues.map(issue => `<li><i class="bi bi-x-circle text-danger me-2"></i>${issue}</li>`).join('')}</ul>`;
    }

    generateZxcvbnHTML(zxcvbnData) {
        return `
            <div class="row mb-4">
                <div class="col-12">
                    <h6 class="fw-bold">Advanced Analysis (zxcvbn)</h6>
                    <div class="alert alert-info">
                        <p><strong>Score:</strong> ${zxcvbnData.score}/4</p>
                        ${zxcvbnData.feedback.warning ? `<p><strong>Warning:</strong> ${zxcvbnData.feedback.warning}</p>` : ''}
                        ${zxcvbnData.feedback.suggestions.length > 0 ? `
                            <p><strong>Suggestions:</strong></p>
                            <ul>${zxcvbnData.feedback.suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}</ul>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    handlePasswordInput() {
        const passwordInput = document.getElementById('passwordInput');
        const password = passwordInput.value;

        // Real-time basic feedback could be added here
        if (password.length > 0) {
            passwordInput.classList.add('is-valid');
        } else {
            passwordInput.classList.remove('is-valid');
        }
    }

    clearPassword() {
        const passwordInput = document.getElementById('passwordInput');
        const resultsContainer = document.getElementById('analysisResults');
        const emptyState = document.getElementById('emptyState');

        if (passwordInput) {
            passwordInput.value = '';
            passwordInput.classList.remove('is-valid');
            passwordInput.focus();
        }

        if (resultsContainer && emptyState) {
            resultsContainer.classList.add('d-none');
            emptyState.classList.remove('d-none');
        }

        this.currentAnalysis = null;
    }

    togglePasswordVisibility() {
        const passwordInput = document.getElementById('passwordInput');
        const toggleIcon = document.getElementById('toggleIcon');

        if (passwordInput && toggleIcon) {
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                toggleIcon.className = 'bi bi-eye-slash';
            } else {
                passwordInput.type = 'password';
                toggleIcon.className = 'bi bi-eye';
            }
        }
    }

    // Wordlist Generation Functions
    async generateWordlist() {
        const inputs = this.collectWordlistInputs();
        const options = this.collectWordlistOptions();

        if (!inputs || inputs.length === 0) {
            this.showToast('Please provide at least one input for wordlist generation', 'error');
            return;
        }

        try {
            this.showLoading(true);
            
            const response = await fetch('/generate-wordlist', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ inputs: inputs, options: options })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                this.displayWordlistResults(data);
                this.currentWordlistData = { inputs, options }; // Store for download
            } else {
                this.showToast(data.error || 'Wordlist generation failed', 'error');
            }
        } catch (error) {
            console.error('Wordlist generation error:', error);
            this.showToast('Network error occurred', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    collectWordlistInputs() {
        const inputs = [];
        const inputIds = ['nameInput', 'petInput', 'dateInput', 'locationInput', 'companyInput', 'hobbyInput', 'customInput'];

        inputIds.forEach(id => {
            const element = document.getElementById(id);
            if (element && element.value.trim()) {
                inputs.push(element.value.trim());
            }
        });

        return inputs;
    }

    collectWordlistOptions() {
        return {
            includeYears: document.getElementById('includeYears')?.checked || false,
            includeLeet: document.getElementById('includeLeet')?.checked || false,
            includeCommon: document.getElementById('includeCommon')?.checked || false,
            includeVariations: document.getElementById('includeVariations')?.checked || false
        };
    }

    displayWordlistResults(data) {
        const resultsContainer = document.getElementById('wordlistResults');
        const emptyState = document.getElementById('wordlistEmptyState');

        if (resultsContainer && emptyState) {
            resultsContainer.classList.remove('d-none');
            emptyState.classList.add('d-none');
        }

        // Update statistics
        const totalWords = document.getElementById('totalWords');
        const avgLength = document.getElementById('avgLength');

        if (totalWords) {
            totalWords.textContent = data.total_words.toLocaleString();
        }

        if (avgLength) {
            avgLength.textContent = data.statistics.average_length;
        }

        // Update preview
        const preview = document.getElementById('wordlistPreview');
        if (preview && data.wordlist_preview) {
            preview.innerHTML = data.wordlist_preview
                .slice(0, 20)
                .map(word => `<div class="preview-item">${this.escapeHtml(word)}</div>`)
                .join('');
        }

        // Animation
        resultsContainer.style.opacity = '0';
        setTimeout(() => {
            resultsContainer.style.transition = 'opacity 0.5s ease';
            resultsContainer.style.opacity = '1';
        }, 100);

        this.showToast(`Generated ${data.total_words} passwords successfully!`, 'success');
    }

    async downloadWordlist() {
        if (!this.currentWordlistData) {
            this.showToast('No wordlist to download', 'error');
            return;
        }

        const format = document.getElementById('downloadFormat')?.value || 'txt';
        const filename = 'wordlist';

        try {
            this.showLoading(true);

            const response = await fetch('/download-wordlist', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    ...this.currentWordlistData,
                    format: format,
                    filename: filename
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Create download link and trigger download
                const link = document.createElement('a');
                link.href = data.download_url;
                link.download = data.file_info.filename;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);

                this.showToast(`Downloaded ${data.file_info.filename} (${data.file_info.size} words)`, 'success');
            } else {
                this.showToast(data.error || 'Download failed', 'error');
            }
        } catch (error) {
            console.error('Download error:', error);
            this.showToast('Download failed', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    clearWordlistForm() {
        const inputIds = ['nameInput', 'petInput', 'dateInput', 'locationInput', 'companyInput', 'hobbyInput', 'customInput'];
        
        inputIds.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.value = '';
            }
        });

        const resultsContainer = document.getElementById('wordlistResults');
        const emptyState = document.getElementById('wordlistEmptyState');

        if (resultsContainer && emptyState) {
            resultsContainer.classList.add('d-none');
            emptyState.classList.remove('d-none');
        }

        this.currentWordlistData = null;

        // Focus first input
        const firstInput = document.getElementById('nameInput');
        if (firstInput) {
            firstInput.focus();
        }
    }

    // Utility Functions
    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            if (show) {
                overlay.classList.add('show');
            } else {
                overlay.classList.remove('show');
            }
        }
    }

    showToast(message, type = 'success') {
        const toastId = type === 'error' ? 'errorToast' : 'successToast';
        const messageId = type === 'error' ? 'errorMessage' : 'toastMessage';
        
        const toastElement = document.getElementById(toastId);
        const messageElement = document.getElementById(messageId);

        if (toastElement && messageElement) {
            messageElement.textContent = message;
            const toast = new bootstrap.Toast(toastElement);
            toast.show();
        }
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    autoResize(event) {
        const textarea = event.target;
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    initTooltips() {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// Hide loading overlay whenever any Bootstrap modal is about to be shown
document.querySelectorAll('.modal').forEach(modalEl => {
  modalEl.addEventListener('show.bs.modal', () => {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.classList.remove('show');
  });
});

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new PasswordAnalyzer();
    
    // Initialize other Bootstrap components
    const toastElements = [].slice.call(document.querySelectorAll('.toast'));
    toastElements.map(function (toastEl) {
        return new bootstrap.Toast(toastEl);
    });
});

// Export for potential testing or extension
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PasswordAnalyzer;
}