
import os
import urllib.request
import urllib.error
import zipfile
import io
import nltk
from pathlib import Path
import ssl

# Constants
DATA_DIR = Path("app/data")
WIKITEXT_URL = "https://s3.amazonaws.com/research.metamind.io/wikitext/wikitext-2-v1.zip"
DICTIONARY_URL = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"

# Bypass SSL verify if needed (for some windows envs)
ssl._create_default_https_context = ssl._create_unverified_context

def ensure_data_dir():
    """Create data directory if it doesn't exist."""
    print(f"Checking data directory: {DATA_DIR.resolve()}")
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        print("Created data directory.")
    else:
        print("Data directory exists.")

def download_file(url, target_path=None):
    """Download file from URL using urllib."""
    try:
        print(f"Downloading from {url}...")
        with urllib.request.urlopen(url) as response:
            return response.read()
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

def download_wikitext():
    """Download and extract WikiText-2 dataset."""
    print("\nDownloading WikiText-2 dataset...")
    content = download_file(WIKITEXT_URL)
    
    if content:
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                # Extract only the train file
                for file_info in z.infolist():
                    if "wiki.train.tokens" in file_info.filename:
                        print(f"Extracting {file_info.filename}...")
                        # Read content
                        file_content = z.read(file_info.filename)
                        # Write to data dir
                        target_path = DATA_DIR / "wikitext-2.txt"
                        with open(target_path, "wb") as f:
                            f.write(file_content)
                        print(f"Saved to {target_path}")
                        return True
            print("Could not find train file in zip archive.")
        except Exception as e:
            print(f"Error processing zip: {e}")
    return False

def download_dictionary():
    """Download comprehensive English dictionary."""
    print("\nDownloading English dictionary...")
    content = download_file(DICTIONARY_URL)
    
    if content:
        try:
            target_path = DATA_DIR / "words_alpha.txt"
            with open(target_path, "wb") as f:
                f.write(content)
            print(f"Saved dictionary to {target_path} ({len(content) / 1024:.1f} KB)")
            return True
        except Exception as e:
            print(f"Error saving dictionary: {e}")
    return False

def download_nltk_corpora():
    """Download NLTK corpora."""
    print("\nDownloading NLTK corpora...")
    corpora = ['reuters', 'webtext', 'inaugural', 'punkt', 'words', 'names']
    
    for corpus in corpora:
        try:
            print(f"Downloading {corpus}...")
            nltk.download(corpus, quiet=True)
            print(f"  - {corpus} downloaded.")
        except Exception as e:
            print(f"  - Failed to download {corpus}: {e}")

def main():
    print("Starting data download (using urllib)...")
    ensure_data_dir()
    
    # WikiText-2
    if not (DATA_DIR / "wikitext-2.txt").exists():
        download_wikitext()
    else:
        print("\nWikiText-2 already exists. Skipping.")
        
    # Dictionary
    if not (DATA_DIR / "words_alpha.txt").exists():
        download_dictionary()
    else:
        print("\nDictionary already exists. Skipping.")
        
    # NLTK
    download_nltk_corpora()
    
    print("\nData download complete!")

if __name__ == "__main__":
    main()
