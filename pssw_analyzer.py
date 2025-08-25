import re
import math
import string
from datetime import datetime
from pssw_config import Config

try:
    from zxcvbn import zxcvbn
    ZXCVBN_AVAILABLE = True
except ImportError:
    ZXCVBN_AVAILABLE = False

class PasswordAnalyzer:
    def __init__(self):
        self.config = Config()
    
    def analyze_password(self, password):
        """Comprehensive password analysis"""
        if not password:
            return self._empty_analysis()
        
        analysis = {
            'password': password,
            'length': len(password),
            'strength_score': 0,
            'strength_label': 'Very Weak',
            'strength_color': 'danger',
            'entropy': 0,
            'time_to_crack': 'Less than a second',
            'character_analysis': self._analyze_characters(password),
            'pattern_analysis': self._analyze_patterns(password),
            'recommendations': [],
            'zxcvbn_analysis': None,
            'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Calculate entropy and strength
        analysis['entropy'] = self._calculate_entropy(password)
        analysis['strength_score'] = self._calculate_strength_score(password, analysis)
        analysis['strength_label'], analysis['strength_color'] = self._get_strength_label(analysis['strength_score'])
        analysis['time_to_crack'] = self._estimate_crack_time(analysis['entropy'])
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(password, analysis)
        
        # Use zxcvbn if available
        if ZXCVBN_AVAILABLE:
            analysis['zxcvbn_analysis'] = self._zxcvbn_analysis(password)
        
        return analysis
    
    def _empty_analysis(self):
        """Return empty analysis for invalid input"""
        return {
            'password': '',
            'length': 0,
            'strength_score': 0,
            'strength_label': 'Invalid',
            'strength_color': 'secondary',
            'entropy': 0,
            'time_to_crack': 'N/A',
            'character_analysis': {},
            'pattern_analysis': {},
            'recommendations': ['Please enter a password to analyze'],
            'zxcvbn_analysis': None,
            'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _analyze_characters(self, password):
        """Analyze character composition"""
        analysis = {
            'has_lowercase': bool(re.search(r'[a-z]', password)),
            'has_uppercase': bool(re.search(r'[A-Z]', password)),
            'has_digits': bool(re.search(r'\d', password)),
            'has_special': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)),
            'lowercase_count': len(re.findall(r'[a-z]', password)),
            'uppercase_count': len(re.findall(r'[A-Z]', password)),
            'digit_count': len(re.findall(r'\d', password)),
            'special_count': len(re.findall(r'[!@#$%^&*(),.?":{}|<>]', password)),
            'unique_chars': len(set(password)),
            'char_diversity': len(set(password)) / len(password) if password else 0
        }
        
        analysis['character_types'] = sum([
            analysis['has_lowercase'],
            analysis['has_uppercase'],
            analysis['has_digits'],
            analysis['has_special']
        ])
        
        return analysis
    
    def _analyze_patterns(self, password):
        """Analyze password patterns"""
        analysis = {
            'has_common_patterns': self._check_common_patterns(password),
            'has_keyboard_patterns': self._check_keyboard_patterns(password),
            'has_repeated_chars': self._check_repeated_characters(password),
            'has_sequential_chars': self._check_sequential_characters(password),
            'common_substitutions': self._check_leet_speak(password),
            'contains_dictionary_words': self._check_dictionary_words(password)
        }
        
        return analysis
    
    def _check_common_patterns(self, password):
        """Check for common password patterns"""
        password_lower = password.lower()
        common_found = []
        
        for pattern in self.config.COMMON_PATTERNS:
            if pattern in password_lower:
                common_found.append(pattern)
        
        return common_found
    
    def _check_keyboard_patterns(self, password):
        """Check for keyboard patterns"""
        keyboard_patterns = [
            'qwerty', 'asdf', 'zxcv', '1234', '4567', '7890',
            'qwertyuiop', 'asdfghjkl', 'zxcvbnm'
        ]
        
        password_lower = password.lower()
        patterns_found = []
        
        for pattern in keyboard_patterns:
            if pattern in password_lower or pattern[::-1] in password_lower:
                patterns_found.append(pattern)
        
        return patterns_found
    
    def _check_repeated_characters(self, password):
        """Check for repeated characters"""
        repeated = []
        i = 0
        while i < len(password) - 2:
            if password[i] == password[i+1] == password[i+2]:
                repeated.append(password[i] * 3)
                i += 3
            else:
                i += 1
        
        return repeated
    
    def _check_sequential_characters(self, password):
        """Check for sequential characters"""
        sequential = []
        
        # Check for numeric sequences
        for i in range(len(password) - 2):
            if (password[i:i+3].isdigit() and 
                int(password[i+1]) == int(password[i]) + 1 and 
                int(password[i+2]) == int(password[i+1]) + 1):
                sequential.append(password[i:i+3])
        
        # Check for alphabetic sequences
        for i in range(len(password) - 2):
            substr = password[i:i+3].lower()
            if (substr.isalpha() and 
                ord(substr[1]) == ord(substr[0]) + 1 and 
                ord(substr[2]) == ord(substr[1]) + 1):
                sequential.append(password[i:i+3])
        
        return sequential
    
    def _check_leet_speak(self, password):
        """Check for common leet speak substitutions"""
        substitutions = []
        
        for char, replacements in self.config.LEET_REPLACEMENTS.items():
            for replacement in replacements:
                if replacement in password:
                    substitutions.append(f'{replacement} -> {char}')
        
        return substitutions
    
    def _check_dictionary_words(self, password):
        """Basic dictionary word check"""
        # This is a simplified version - in a full implementation,
        # you'd use a proper dictionary or wordlist
        common_words = [
            'password', 'admin', 'user', 'login', 'welcome',
            'secret', 'master', 'super', 'root', 'test'
        ]
        
        password_lower = password.lower()
        found_words = []
        
        for word in common_words:
            if word in password_lower:
                found_words.append(word)
        
        return found_words
    
    def _calculate_entropy(self, password):
        """Calculate password entropy"""
        if not password:
            return 0
        
        # Determine character set size
        charset_size = 0
        
        if re.search(r'[a-z]', password):
            charset_size += 26
        if re.search(r'[A-Z]', password):
            charset_size += 26
        if re.search(r'\d', password):
            charset_size += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            charset_size += 32
        
        # Calculate entropy
        if charset_size > 0:
            entropy = len(password) * math.log2(charset_size)
        else:
            entropy = 0
        
        return round(entropy, 2)
    
    def _calculate_strength_score(self, password, analysis):
        """Calculate overall strength score (0-100)"""
        score = 0
        
        # Length scoring (0-30 points)
        length = len(password)
        if length >= 12:
            score += 30
        elif length >= 8:
            score += 20
        elif length >= 6:
            score += 10
        elif length >= 4:
            score += 5
        
        # Character diversity (0-25 points)
        char_types = analysis['character_analysis']['character_types']
        score += char_types * 6.25
        
        # Character diversity ratio (0-15 points)
        diversity_ratio = analysis['character_analysis']['char_diversity']
        score += diversity_ratio * 15
        
        # Entropy bonus (0-20 points)
        entropy = analysis['entropy']
        if entropy >= 60:
            score += 20
        elif entropy >= 40:
            score += 15
        elif entropy >= 25:
            score += 10
        elif entropy >= 15:
            score += 5
        
        # Pattern penalties (0-10 points deduction)
        patterns = analysis['pattern_analysis']
        if patterns['has_common_patterns']:
            score -= 10
        if patterns['has_keyboard_patterns']:
            score -= 5
        if patterns['has_repeated_chars']:
            score -= 5
        if patterns['has_sequential_chars']:
            score -= 5
        
        return max(0, min(100, round(score)))
    
    def _get_strength_label(self, score):
        """Get strength label and color based on score"""
        if score >= 80:
            return 'Very Strong', 'success'
        elif score >= 60:
            return 'Strong', 'info'
        elif score >= 40:
            return 'Moderate', 'warning'
        elif score >= 20:
            return 'Weak', 'danger'
        else:
            return 'Very Weak', 'danger'
    
    def _estimate_crack_time(self, entropy):
        """Estimate time to crack based on entropy"""
        if entropy <= 0:
            return 'Instantly'
        
        # Assume 1 billion attempts per second
        attempts_per_second = 1_000_000_000
        possible_combinations = 2 ** entropy
        
        # Time to crack 50% of passwords
        seconds = possible_combinations / (2 * attempts_per_second)
        
        if seconds < 1:
            return 'Less than a second'
        elif seconds < 60:
            return f'{int(seconds)} seconds'
        elif seconds < 3600:
            return f'{int(seconds/60)} minutes'
        elif seconds < 86400:
            return f'{int(seconds/3600)} hours'
        elif seconds < 2592000:
            return f'{int(seconds/86400)} days'
        elif seconds < 31536000:
            return f'{int(seconds/2592000)} months'
        else:
            years = int(seconds/31536000)
            if years > 1000000:
                return 'Millions of years'
            else:
                return f'{years} years'
    
    def _generate_recommendations(self, password, analysis):
        """Generate recommendations for password improvement"""
        recommendations = []
        
        char_analysis = analysis['character_analysis']
        pattern_analysis = analysis['pattern_analysis']
        
        # Length recommendations
        if analysis['length'] < 8:
            recommendations.append('Use at least 8 characters (12+ recommended)')
        elif analysis['length'] < 12:
            recommendations.append('Consider using 12 or more characters for better security')
        
        # Character type recommendations
        if not char_analysis['has_lowercase']:
            recommendations.append('Add lowercase letters')
        if not char_analysis['has_uppercase']:
            recommendations.append('Add uppercase letters')
        if not char_analysis['has_digits']:
            recommendations.append('Add numbers')
        if not char_analysis['has_special']:
            recommendations.append('Add special characters (!@#$%^&*)')
        
        # Pattern recommendations
        if pattern_analysis['has_common_patterns']:
            recommendations.append('Avoid common password patterns')
        if pattern_analysis['has_keyboard_patterns']:
            recommendations.append('Avoid keyboard patterns (qwerty, 123456, etc.)')
        if pattern_analysis['has_repeated_chars']:
            recommendations.append('Avoid repeated characters (aaa, 111)')
        if pattern_analysis['has_sequential_chars']:
            recommendations.append('Avoid sequential characters (abc, 123)')
        if pattern_analysis['contains_dictionary_words']:
            recommendations.append('Avoid common dictionary words')
        
        # Diversity recommendations
        if char_analysis['char_diversity'] < 0.7:
            recommendations.append('Use more unique characters')
        
        # General recommendations
        if analysis['strength_score'] < 60:
            recommendations.extend([
                'Consider using a passphrase instead of a password',
                'Use a password manager to generate strong passwords',
                'Enable two-factor authentication where possible'
            ])
        
        return recommendations[:8]  # Limit to 8 recommendations
    
    def _zxcvbn_analysis(self, password):
        """Use zxcvbn library for additional analysis"""
        try:
            result = zxcvbn(password)
            return {
                'score': result['score'],
                'crack_times': result['crack_times_display'],
                'feedback': {
                    'warning': result['feedback']['warning'],
                    'suggestions': result['feedback']['suggestions']
                }
            }
        except Exception:
            return None