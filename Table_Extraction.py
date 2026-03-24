import pdfplumber
import pandas as pd
import re

def extract_tables(pdf_path):
    """
    Extract all tables from the PDF using pdfplumber and return as a list of dicts.
    Each dict contains 'table' (DataFrame) and 'heading' (string from text above the table, cleaned with proper spacing).
    """
    try:
        tables = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                # Extract full page text with spaces preserved
                page_text = page.extract_text()
                
                # Extract tables
                page_tables = page.extract_tables()
                print(f"Page {page_num}: Found {len(page_tables)} tables")  # Debug
                
                for i, table_data in enumerate(page_tables):
                    print(f"Processing table {i+1} on page {page_num}: {len(table_data)} rows")  # Debug
                    if table_data:
                        # Find the table start in the page text
                        table_start_text = str(table_data[0][0]) if table_data[0] else ""
                        table_start_index = page_text.find(table_start_text) if table_start_text else -1
                        
                        # Extract text before the table and get the last line as heading
                        heading = f"Table {len(tables) + 1}"
                        if table_start_index != -1:
                            text_before = page_text[:table_start_index].strip()
                            lines_before = text_before.split('\n')
                            if lines_before:
                                heading = lines_before[-1].strip()
                        
                        # Clean heading: Remove leading "X.Y. " (e.g., "5.1. " from "5.1. Structured comparison Of my life")
                        heading = re.sub(r'^\d+(\.\d+)*\.\s*', '', heading).strip()
                        
                        # Fallback: Insert spaces between words if concatenated (e.g., "Structuredcomparison" -> "Structured comparison")
                        heading = re.sub(r'([a-z])([A-Z])', r'\1 \2', heading)
                        
                        # Convert to DataFrame
                        df = pd.DataFrame(table_data[1:], columns=table_data[0]) if len(table_data) > 1 else pd.DataFrame(table_data)
                        df = df.dropna(how='all').dropna(axis=1, how='all')
                        
                        # Make column names unique to avoid Streamlit error
                        if df.shape[1] > 0:
                            seen = {}
                            new_columns = []
                            for col in df.columns:
                                if col in seen:
                                    seen[col] += 1
                                    new_columns.append(f"{col}_{seen[col]}")
                                else:
                                    seen[col] = 0
                                    new_columns.append(col)
                            df.columns = new_columns
                        
                        # Only add if DataFrame has data
                        if not df.empty:
                            tables.append({
                                'table': df,
                                'heading': heading
                            })
                            print(f"Added table {len(tables)}: Heading '{heading}', Shape {df.shape}")  # Debug
                        else:
                            print(f"Skipped empty table {i+1} on page {page_num}")  # Debug
        
        print(f"Total tables extracted: {len(tables)}")  # Debug
        return tables
    
    except Exception as e:
        print(f"Error extracting tables: {e}")
        return []