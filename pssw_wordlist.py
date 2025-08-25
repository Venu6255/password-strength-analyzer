import os
import re
import itertools
from datetime import datetime
from pssw_config import Config

class WordlistGenerator:
    def __init__(self):
        self.config = Config()
    
    def generate_wordlist(self, user_inputs, include_years=True, include_leet=True, 
                         include_common=True, include_variations=True):
        """Generate custom wordlist based on user inputs"""
        
        wordlist = set()
        
        # Clean and prepare user inputs
        cleaned_inputs = self._clean_inputs(user_inputs)
        
        if not cleaned_inputs:
            return []
        
        # Add base words
        for word in cleaned_inputs:
            wordlist.add(word)
            wordlist.add(word.lower())
            wordlist.add(word.upper())
            wordlist.add(word.capitalize())
        
        # Add variations
        if include_variations:
            wordlist.update(self._generate_variations(cleaned_inputs))
        
        # Add leet speak variations
        if include_leet:
            wordlist.update(self._generate_leet_variations(wordlist.copy()))
        
        # Add year combinations
        if include_years:
            wordlist.update(self._add_year_combinations(cleaned_inputs))
        
        # Add common number/symbol combinations
        wordlist.update(self._add_common_combinations(cleaned_inputs))
        
        # Add common patterns
        if include_common:
            wordlist.update(self._add_common_patterns(cleaned_inputs))
        
        # Filter and limit results
        final_wordlist = self._filter_wordlist(wordlist)
        
        return sorted(final_wordlist)
    
    def _clean_inputs(self, user_inputs):
        """Clean and validate user inputs"""
        if not user_inputs:
            return []
        
        # Split inputs by common separators
        all_words = []
        
        for input_text in user_inputs:
            if isinstance(input_text, str) and input_text.strip():
                # Split by various separators
                words = re.split(r'[,;\s\n\t]+', input_text.strip())
                for word in words:
                    cleaned = word.strip()
                    if cleaned and len(cleaned) >= 2:  # Minimum 2 characters
                        all_words.append(cleaned)
        
        return list(set(all_words))  # Remove duplicates
    
    def _generate_variations(self, words):
        """Generate word variations"""
        variations = set()
        
        for word in words:
            # Reverse
            variations.add(word[::-1])
            
            # First letter combinations
            if len(word) >= 3:
                variations.add(word[0] + word[1:].upper())
                variations.add(word[0].upper() + word[1:])
            
            # Remove vowels
            no_vowels = re.sub(r'[aeiouAEIOU]', '', word)
            if no_vowels and no_vowels != word:
                variations.add(no_vowels)
            
            # Double letters
            if len(word) <= 6:  # Avoid too long words
                variations.add(word + word)
            
            # Abbreviations (first letters of each word if multiple words)
            if ' ' in word:
                abbreviation = ''.join([w[0] for w in word.split() if w])
                if len(abbreviation) >= 2:
                    variations.add(abbreviation)
                    variations.add(abbreviation.upper())
        
        return variations
    
    def _generate_leet_variations(self, words):
        """Generate leet speak variations"""
        leet_words = set()
        
        for word in words:
            # Simple leet replacements
            leet_word = word
            for char, replacements in self.config.LEET_REPLACEMENTS.items():
                for replacement in replacements:
                    leet_word = leet_word.replace(char, replacement)
                    leet_word = leet_word.replace(char.upper(), replacement)
            
            if leet_word != word:
                leet_words.add(leet_word)
            
            # Partial leet (replace only some characters)
            for char, replacements in self.config.LEET_REPLACEMENTS.items():
                for replacement in replacements:
                    partial_leet = word.replace(char, replacement, 1)  # Replace only first occurrence
                    if partial_leet != word:
                        leet_words.add(partial_leet)
        
        return leet_words
    
    def _add_year_combinations(self, words):
        """Add year combinations"""
        year_combinations = set()
        current_year = datetime.now().year
        
        # Common years to append
        years = [
            str(current_year), str(current_year - 1), str(current_year + 1),
            str(current_year)[-2:], str(current_year - 1)[-2:],  # 2-digit years
            '2023', '2024', '2025', '23', '24', '25',
            '1990', '1995', '2000', '2010', '90', '95', '00', '10'
        ]
        
        for word in words:
            for year in years:
                year_combinations.add(word + year)
                year_combinations.add(year + word)
                year_combinations.add(word + '_' + year)
                year_combinations.add(word + '-' + year)
        
        return year_combinations
    
    def _add_common_combinations(self, words):
        """Add common number and symbol combinations"""
        combinations = set()
        
        # Common numbers and symbols
        suffixes = ['1', '12', '123', '1234', '!', '!!', '?', '@', '#', '01', '001']
        prefixes = ['1', '12', '@', '#']
        
        for word in words:
            for suffix in suffixes:
                combinations.add(word + suffix)
            
            for prefix in prefixes:
                combinations.add(prefix + word)
        
        return combinations
    
    def _add_common_patterns(self, words):
        """Add common password patterns"""
        patterns = set()
        
        for word in words:
            # Common password formats
            patterns.add(word + '123')
            patterns.add(word + '456')
            patterns.add(word + '789')
            patterns.add(word + '!@#')
            patterns.add(word + '***')
            patterns.add('***' + word)
            patterns.add(word.capitalize() + '1')
            patterns.add(word.capitalize() + '!')
            
            # With common words
            common_additions = ['password', 'admin', 'user', 'login', 'secure']
            for addition in common_additions:
                if word.lower() != addition:
                    patterns.add(word + addition)
                    patterns.add(addition + word)
        
        return patterns
    
    def _filter_wordlist(self, wordlist):
        """Filter and clean the wordlist"""
        filtered = []
        
        for word in wordlist:
            # Basic filters
            if (isinstance(word, str) and 
                2 <= len(word) <= 50 and  # Length limits
                word.strip() == word and  # No leading/trailing spaces
                not word.isspace()):      # Not just whitespace
                filtered.append(word)
        
        # Remove duplicates and limit size
        unique_filtered = list(set(filtered))
        
        if len(unique_filtered) > self.config.MAX_WORDLIST_SIZE:
            unique_filtered = unique_filtered[:self.config.MAX_WORDLIST_SIZE]
        
        return unique_filtered
    
    def save_wordlist(self, wordlist, filename_base="custom_wordlist", format_type="txt"):
        """Save wordlist to file"""
        if not wordlist:
            return None
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pssw_{filename_base}_{timestamp}.{format_type}"
        filepath = os.path.join(self.config.DOWNLOAD_FOLDER, filename)
        
        try:
            if format_type == "txt":
                with open(filepath, 'w', encoding='utf-8') as f:
                    for word in wordlist:
                        f.write(word + '\n')
            
            elif format_type == "csv":
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("password,length\n")  # Header
                    for word in wordlist:
                        f.write(f'"{word}",{len(word)}\n')
            
            return {
                'filename': filename,
                'filepath': filepath,
                'size': len(wordlist),
                'file_size': os.path.getsize(filepath)
            }
        
        except Exception as e:
            return None
    
    def get_wordlist_statistics(self, wordlist):
        """Get statistics about the generated wordlist"""
        if not wordlist:
            return {}
        
        stats = {
            'total_words': len(wordlist),
            'unique_words': len(set(wordlist)),
            'average_length': round(sum(len(word) for word in wordlist) / len(wordlist), 2),
            'min_length': min(len(word) for word in wordlist),
            'max_length': max(len(word) for word in wordlist),
            'length_distribution': {},
            'character_types': {
                'has_numbers': sum(1 for word in wordlist if any(c.isdigit() for c in word)),
                'has_symbols': sum(1 for word in wordlist if any(c in '!@#$%^&*()' for c in word)),
                'has_uppercase': sum(1 for word in wordlist if any(c.isupper() for c in word)),
                'has_lowercase': sum(1 for word in wordlist if any(c.islower() for c in word))
            }
        }
        
        # Length distribution
        for word in wordlist:
            length = len(word)
            stats['length_distribution'][length] = stats['length_distribution'].get(length, 0) + 1
        
        return stats