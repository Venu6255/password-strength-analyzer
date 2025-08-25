from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import os
import json
from datetime import datetime
from pssw_config import Config
from pssw_analyzer import PasswordAnalyzer
from pssw_wordlist import WordlistGenerator

app = Flask(__name__)
app.config.from_object(Config)

# Initialize components
password_analyzer = PasswordAnalyzer()
wordlist_generator = WordlistGenerator()

@app.route('/')
def index():
    """Main page"""
    return render_template('pssw_index.html')

@app.route('/analyze', methods=['POST'])
def analyze_password():
    """Analyze password strength"""
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        if len(password) > app.config['MAX_PASSWORD_LENGTH']:
            return jsonify({'error': f'Password too long (max {app.config["MAX_PASSWORD_LENGTH"]} characters)'}), 400
        
        # Analyze password
        analysis = password_analyzer.analyze_password(password)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/generate-wordlist', methods=['POST'])
def generate_wordlist():
    """Generate custom wordlist"""
    try:
        data = request.get_json()
        
        # Get user inputs
        user_inputs = data.get('inputs', [])
        options = data.get('options', {})
        
        # Validate inputs
        if not user_inputs:
            return jsonify({'error': 'At least one input is required'}), 400
        
        # Generate wordlist
        wordlist = wordlist_generator.generate_wordlist(
            user_inputs,
            include_years=options.get('includeYears', True),
            include_leet=options.get('includeLeet', True),
            include_common=options.get('includeCommon', True),
            include_variations=options.get('includeVariations', True)
        )
        
        if not wordlist:
            return jsonify({'error': 'No wordlist generated from inputs'}), 400
        
        # Get statistics
        stats = wordlist_generator.get_wordlist_statistics(wordlist)
        
        return jsonify({
            'success': True,
            'wordlist_preview': wordlist[:50],  # First 50 words for preview
            'statistics': stats,
            'total_words': len(wordlist)
        })
    
    except Exception as e:
        return jsonify({'error': f'Wordlist generation failed: {str(e)}'}), 500

@app.route('/download-wordlist', methods=['POST'])
def download_wordlist():
    """Download generated wordlist"""
    try:
        data = request.get_json()
        
        user_inputs = data.get('inputs', [])
        options = data.get('options', {})
        format_type = data.get('format', 'txt')
        filename_base = data.get('filename', 'wordlist')
        
        if not user_inputs:
            return jsonify({'error': 'No inputs provided'}), 400
        
        # Generate wordlist
        wordlist = wordlist_generator.generate_wordlist(
            user_inputs,
            include_years=options.get('includeYears', True),
            include_leet=options.get('includeLeet', True),
            include_common=options.get('includeCommon', True),
            include_variations=options.get('includeVariations', True)
        )
        
        if not wordlist:
            return jsonify({'error': 'No wordlist generated'}), 400
        
        # Save wordlist
        file_info = wordlist_generator.save_wordlist(wordlist, filename_base, format_type)
        
        if not file_info:
            return jsonify({'error': 'Failed to save wordlist'}), 500
        
        return jsonify({
            'success': True,
            'download_url': f"/download-file/{file_info['filename']}",
            'file_info': file_info
        })
    
    except Exception as e:
        return jsonify({'error': f'Download preparation failed: {str(e)}'}), 500

@app.route('/download-file/<filename>')
def download_file(filename):
    """Serve file download"""
    try:
        file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            flash('File not found', 'error')
            return redirect(url_for('index'))
        
        return send_file(file_path, as_attachment=True, download_name=filename)
    
    except Exception as e:
        flash(f'Download failed: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/results')
def results():
    """Results page"""
    return render_template('pssw_results.html')

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('pssw_index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)
    
    # Run the app
    app.run(debug=True, host='127.0.0.1', port=5000)