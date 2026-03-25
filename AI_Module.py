import re
import os
from functools import lru_cache

@lru_cache(maxsize=1)
def load_document(file_name):
    if not os.path.exists(file_name):
        print(f"Warning: File not found: {file_name}")
        return ""
    
    if not file_name.endswith('.txt'):
        file_name += '.txt'
    
    # Check if .txt version exists
    if not os.path.exists(file_name):
        print(f"Warning: Extracted text not found: {file_name}")
        return ""
        
    with open(file_name, "r", encoding="utf-8") as f:
        return f.read()

# FULL 28 HEADINGS - Updated to match document exactly
HEADING_MAP = {
    'scope of supply': '1. Scope of Supply',
    'effective date of order': '2. Effective Date of Order:',
    'delivery schedule': '3. Delivery Schedule and Liquidated Damages:',
    'order value': '4. Order Value:',
    'taxes & duties': '5. Taxes & Duties:',
    'payment terms': '6. Payment Terms:',
    'supplies inspections & testing': '7. Supplies inspections & Testing:',
    'quality': '8. Quality',
    'warranty': '9. Warranty/ Defect Liability Period:',
    'packing and marking': '10. Packing and Marking:',
    'transfer of title and risk': '11. Transfer of Title and Risk:',
    'insurance': '12. Insurance:',
    'assignment and sub-contracting': '13. Assignment and Sub-Contracting:',
    'compliance of laws': '14. Compliance of Laws, Standards and Codes:',
    'suppliers representations and warranties': '15. Suppliers Representations and Warranties',
    'replacement of defective parts and materials': '16. Replacement of Defective Parts and Materials:',
    'risk purchase': '17. Risk Purchase:',
    'limitation of liabilities': '18. Limitation of Liabilities:',
    'intellectual property rights': '19. Intellectual Property Rights and Ownership of Design, Data and Documents:',
    'secrecy and confidentiality': '20. Secrecy and Confidentiality:',
    'indemnification': '21. Indemnification:',
    'force majeure': '22. Force Majeure:',
    'suspension': '23. Suspension:',
    'termination': '24. Termination:',
    'arbitration': '25. Arbitration:',
    'governing law and jurisdiction': '26. Governing Law and Jurisdiction:',
    'general': '27. General:',
    'general covenants': '28. General Covenants # Compliance with Code of Ethical Business Conduct'
}

def extract_clause(doc, query):
    if not doc.strip():
        return "No document content available. Please check if PDF extraction succeeded."
    
    q_lower = query.lower()
    print(f"Searching document for: '{q_lower}'")
    
    found_section = None
    section_title = None
    
    for key, exact_heading in HEADING_MAP.items():
        if key in q_lower:
            # Try multiple heading variations from document
            headings_to_try = [
                exact_heading,
                exact_heading.replace(':', ''),
                exact_heading.replace(':', ': -'),
                f"{exact_heading.split('.')[1].strip() if '.' in exact_heading else exact_heading}",
            ]
            
            for heading in headings_to_try:
                start = doc.find(heading)
                if start != -1:
                    section_title = heading
                    # Find section end (next numbered heading)
                    end_text = doc[start:]
                    next_match = re.search(r'\n(\d{1,2}\.[\sA-Za-z&:\-/]+)', end_text, re.IGNORECASE)
                    end = len(doc) if not next_match else start + next_match.start()
                    
                    section = doc[start:end].strip()
                    if len(section) > 200:  # Valid section length
                        found_section = section[:12000]
                        print(f"✓ Found '{section_title}' - {len(found_section)} chars")
                        break
            
            if found_section:
                break
    
    if found_section:
        return f"**{section_title}**\n\n{found_section}"
    
    # Fallback - direct text search
    matches = re.finditer(re.escape(q_lower), doc, re.IGNORECASE)
    contexts = []
    for match in list(matches)[:3]:
        context_start = max(0, match.start() - 300)
        context_end = min(len(doc), match.end() + 300)
        context = doc[context_start:context_end].replace('\n', ' ').strip()
        contexts.append(context)
    
    if contexts:
        return f"No exact heading match. Relevant text found:\n\n" + "\n\n---\n\n".join(contexts)
    
    return f"No '{query}' found. Available sections:\n{list(HEADING_MAP.keys())}\n\nPreview: {doc[:1000]}..."

def run_query(extracted_file_name, query, *args, **kwargs):
    doc = load_document(extracted_file_name)
    return extract_clause(doc, query)

