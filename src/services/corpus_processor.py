import os
import re
from typing import List, Dict
import json
from tqdm import tqdm


class CorpusProcessor:
    """Processa e normaliza textos bíblicos (SBLGNT, BHS) para análise."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.verses = []
        
    def parse_sblgnt_file(self, filepath: str) -> List[Dict]:
        """
        Parse arquivos MorphGNT format (SBLGNT).
        Formato: book chapter verse part word pos parsing_code
        Ex: 610101 N- Βίβλος βίβλος βίβλος N-NSF
        """
        verses_data = []
        current_verse = {"book": "", "chapter": 0, "verse": 0, "text": "", "words": []}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split()
                    if len(parts) < 6:
                        continue
                    
                    # Parse reference: BBCCVVPP (book, chapter, verse, part)
                    ref = parts[0]
                    book_num = ref[:2]
                    chapter = int(ref[2:4])
                    verse = int(ref[4:6])
                    
                    # Format: ref pos parsing word1 word2 word3 lemma
                    # We want word1 (index 3) - the actual Greek word with accents/punctuation
                    word = parts[3]  # Greek word with accents
                    
                    # Se mudou de verso, salva o anterior
                    if current_verse["verse"] != verse or current_verse["chapter"] != chapter:
                        if current_verse["text"]:
                            verses_data.append(current_verse.copy())
                        current_verse = {
                            "book": self._get_book_name(book_num),
                            "chapter": chapter,
                            "verse": verse,
                            "text": "",
                            "words": [],
                            "language": "greek"
                        }
                    
                    current_verse["words"].append(word)
                    current_verse["text"] += word + " "
                
                # Adiciona último verso
                if current_verse["text"]:
                    verses_data.append(current_verse)
                    
        except Exception as e:
            print(f"Erro ao processar {filepath}: {e}")
        
        return verses_data
    
    def _get_book_name(self, book_num: str) -> str:
        """Mapeia código numérico para nome do livro (NT)."""
        books = {
            "61": "Matthew", "62": "Mark", "63": "Luke", "64": "John",
            "65": "Acts", "66": "Romans", "67": "1Corinthians", "68": "2Corinthians",
            "69": "Galatians", "70": "Ephesians", "71": "Philippians", "72": "Colossians",
            "73": "1Thessalonians", "74": "2Thessalonians", "75": "1Timothy", 
            "76": "2Timothy", "77": "Titus", "78": "Philemon", "79": "Hebrews",
            "80": "James", "81": "1Peter", "82": "2Peter", "83": "1John",
            "84": "2John", "85": "3John", "86": "Jude", "87": "Revelation"
        }
        return books.get(book_num, f"Book{book_num}")
    
    def process_all_sblgnt(self, sblgnt_dir: str = None) -> List[Dict]:
        """Processa todos os arquivos SBLGNT no diretório."""
        if sblgnt_dir is None:
            sblgnt_dir = os.path.join("Documentação", "Bible", "sblgnt")
        
        all_verses = []
        if not os.path.exists(sblgnt_dir):
            print(f"Diretório {sblgnt_dir} não encontrado.")
            return all_verses
        
        files = [f for f in os.listdir(sblgnt_dir) if f.endswith("-morphgnt.txt")]
        for filename in tqdm(files, desc="Processando livros", unit="livro"):
            filepath = os.path.join(sblgnt_dir, filename)
            verses = self.parse_sblgnt_file(filepath)
            all_verses.extend(verses)
        
        return all_verses
    
    def save_corpus(self, verses: List[Dict], output_file: str = "data/nt_corpus.json"):
        """Salva corpus processado em JSON."""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(verses, f, ensure_ascii=False, indent=2)
        print(f"Corpus salvo em {output_file} ({len(verses)} versos)")
    
    def load_corpus(self, corpus_file: str = "data/nt_corpus.json") -> List[Dict]:
        """Carrega corpus processado."""
        if not os.path.exists(corpus_file):
            return []
        with open(corpus_file, 'r', encoding='utf-8') as f:
            return json.load(f)


if __name__ == "__main__":
    # Teste rápido
    processor = CorpusProcessor()
    verses = processor.process_all_sblgnt()
    if verses:
        processor.save_corpus(verses)
        print(f"\n✓ Processados {len(verses)} versos do NT")
        print(f"Exemplo: {verses[0]}")
