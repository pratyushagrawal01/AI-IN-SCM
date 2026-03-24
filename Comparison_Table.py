import pandas as pd
from AI_Module import run_query

def generate_comparison_table(all_docs, all_pdfs, all_pdf_names):
    if not all_docs or len(all_docs) < 2:
        return None
    
    # Key parameters to compare
    parameters = ["Total Price", "Payment Terms", "Warranty", "Delivery Time", "Support"]
    
    # Initialize comparison data
    comparison_data = {"Parameter": parameters}
    
    # Add RFP column
    rfp_doc = all_docs[0]
    rfp_text = run_query(rfp_doc, "Summarize key clauses for Total Price, Payment Terms, Warranty, Delivery Time, Support", all_docs, all_pdfs, all_pdf_names)
    comparison_data["RFP"] = [extract_param_value(rfp_text, param) for param in parameters]
    
    # Add Quotation columns
    for i, doc in enumerate(all_docs[1:], 1):
        quot_text = run_query(doc, "Summarize key clauses for Total Price, Payment Terms, Warranty, Delivery Time, Support", all_docs, all_pdfs, all_pdf_names)
        comparison_data[f"Quotation {i}"] = [extract_param_value(quot_text, param) for param in parameters]
    
    # Create DataFrame
    df = pd.DataFrame(comparison_data)
    return df

def extract_param_value(text, param):
    # Simple extraction: Look for the parameter in the text
    lines = text.split('\n')
    for line in lines:
        if param.lower() in line.lower():
            return line.strip()
    return "Not found"