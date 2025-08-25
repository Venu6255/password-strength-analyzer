# Password Strength Analyzer Pro

A modern, privacy-first web app that analyzes password strength with advanced entropy and pattern analysis, and generates custom wordlists for security testing.

## Features

- Local password analysis with no data sent to servers  
- Entropy, character diversity, and pattern detection  
- Time-to-crack estimates based on entropy  
- Custom wordlist generation using personal info and variations  
- Responsive Bootstrap 5 UI with animations  
- Integration with zxcvbn for professional strength feedback  
- Download wordlists in TXT or CSV format  

## Getting Started

### Prerequisites

- Python 3.7+  
- Git (for cloning repository)  
- Recommended: Create and activate a Python virtual environment

### Installation

1. Clone this repository:

  git clone https://github.com/<Venu6255>/password-strength-analyzer.git

  cd password-strength-analyzer


2. Create and activate a virtual environment:


3. Install dependencies:

  pip install -r pssw_requirements.txt


4. Run the Flask app:

  python pssw_app.py


5. Open your browser at `http://127.0.0.1:5000`

## Usage

- Enter a password to analyze its strength and get detailed feedback.  
- Use the wordlist generator to create customized password lists for testing.  
- Download generated wordlists for use in security audits.

## Project Structure

- `pssw_app.py` - Main Flask application  
- `pssw_analyzer.py` - Password strength analysis logic  
- `pssw_wordlist.py` - Smart wordlist generation  
- `pssw_config.py` - Configuration constants  
- `templates/` - HTML templates (Bootstrap 5)  
- `static/` - CSS, JS, and generated wordlists  
- `pssw_requirements.txt` - Python dependencies

## Contributing

Contributions, issues, and feature requests are welcome!  
Feel free to fork the repo and submit pull requests.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements

- Inspired by leading password strength checkers and security best practices  
- Built with Flask, Bootstrap 5, and zxcvbn library
