import re
from functools import lru_cache

@lru_cache(maxsize=1)
def load_document(file_name):
    if not file_name.endswith('.txt'):
        file_name += '.txt'
    with open(file_name, "r", encoding="utf-8") as f:
        return f.read()

# FULL 28 HEADINGS - Exact text from your list/TXT
HEADING_MAP = {
    'scope of supply': 'Scope of Supply',
    'effective date of order': 'Effective Date of Order:',
    'delivery schedule': 'Delivery Schedule and Liquidated Damages:',
    'order value': 'Order Value:',
    'taxes & duties': 'Taxes & Duties:',
    'payment terms': 'Payment Terms:',
    'supplies inspections & testing': 'Supplies inspections & Testing:',
    'quality': 'Quality',
    'warranty/ defect liability period': 'Warranty/ Defect Liability Period:',
    'packing and marking': 'Packing and Marking:',
    'transfer of title and risk': 'Transfer of Title and Risk:',
    'insurance': 'Insurance:',
    'assignment and sub-contracting': 'Assignment and Sub-Contracting:',
    'compliance of laws': 'Compliance of Laws, Standards and Codes:',
    'suppliers representations and warranties': 'Suppliers Representations and Warranties',
    'replacement of defective parts and materials': 'Replacement of Defective Parts and Materials:',
    'risk purchase': 'Risk Purchase:',
    'limitation of liabilities': 'Limitation of Liabilities:',
    'intellectual property rights': 'Intellectual Property Rights and Ownership of Design, Data and Documents:',
    'secrecy and confidentiality': 'Secrecy and Confidentiality:',
    'indemnification': 'Indemnification:',
    'force majeure': 'Force Majeure:',
    'suspension': 'Suspension:',
    'termination': 'Termination:',
    'arbitration': 'Arbitration:',
    'governing law and jurisdiction': 'Governing Law and Jurisdiction:',
    'general': 'General:',
    'general covenants': 'General Covenants # Compliance with Code of Ethical Business Conduct'
}

def extract_clause(doc, query):
    q_lower = query.lower()
    for key, exact_heading in HEADING_MAP.items():
        if key in q_lower:
            start = doc.find(exact_heading)
            if start != -1:
                # Find the END of this section (next numbered heading OR end of doc)
                end_text = doc[start:]
                
                # Look for next numbered heading (handles 1-28 numbering)
                next_heading_match = re.search(r'\n(\d{1,2}\.\s+[A-Za-z\s:&#-]+)', end_text)
                
                if next_heading_match:
                    end = start + next_heading_match.start()
                else:
                    # No next heading found, go to end of document
                    end = len(doc)
                
                section = doc[start:end].strip()
                print(f"✓ '{query}' → {exact_heading} ({len(section)} chars)")
                return section[:10000]  # Limit output length
    
    return f"No match. Try these keys: {', '.join(HEADING_MAP.keys())}"

def run_query(extracted_file_name, query, *args, **kwargs):
    doc = load_document(extracted_file_name)


