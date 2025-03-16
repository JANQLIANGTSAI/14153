# DEIA Compliance Scanner  

## 👤 Author  
**Max J. Tsai**  
✉ **Email:** mt8168@gmail.com  
🔗 **GitHub:** https://github.com/JANQLIANGTSAI
© 2025 Max J. Tsai. All rights reserved.  

📝 *This project is released under the **MIT License**, which allows modification, distribution, and private use with minimal restrictions.*

## 🚀 Overview  
This Python program scans webpages for Diversity, Equity, Inclusion, and Accessibility (DEIA) terms to assist with compliance under **Executive Order 14151**. It extracts webpage content, identifies DEIA-related terms, and reports the number of occurrences for each URL.   

## 📌 Features  
✔ Scrapes webpage content using **BeautifulSoup**  
```python
    - adding option to exluse sections, i.e. <footer>
```
✔ Tokenizes and matches DEIA terms and their synonyms  4
```python
    - to-do: STEM for matching; staCy does not work with Python 3.13 (anyone can help?)
```
✔ Displays URLs with the count of DEIA-related term occurrences  

## 🛠️ Installation  
Make sure you have **Python 3.x** installed, then install the required dependencies:  

```bash
python -m venv .venv (and activate)
pip install requirements.txt
```

---
⚠️ **This tool is experimental. Use at your own risk, as with any open-source software.** 