import fitz
from docx import Document 
from langchain.schema import Document as docu

# Extracts text from .txt files
def get_text_from_txt(file_path, dept):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if content:
            document = [
                docu(
                    page_content=content,
                    metadata={"source": file_path, "page": 1, "department": dept}  #can add version details that will help in future
                )
            ]
            return document
        return [] 
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


# Extracts text from .pdf files
def get_text_from_pdf(file_path, dept):
    try:
        doc = fitz.open(file_path)
        documents = []
        for page_num, page in enumerate(doc):  # type: ignore
            text = page.get_text()
            if text:  # Only add pages with actual text
                documents.append(
                    docu(
                        page_content=text,
                        metadata={"source": file_path, "page": page_num + 1, "department": dept}
                    )
                )
        return documents
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


# Extracts text from .docx files
def get_text_from_docx(file_path, dept):
    try:
        doc = Document(file_path)
        full_text = [para.text for para in doc.paragraphs if para.text.strip()]
        content = "\n".join(full_text)

        if content:  # Ensure we don’t create empty documents
            document = [
                docu(
                    page_content=content,
                    metadata={"source": file_path, "page": 1, "department": dept }
                )
            ]
            return document
        return []
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

# -------------------- RAW TEXT --------------------
def process_raw_text(raw_text: str, dept: str):
    """
    Wrap raw text into a LangChain Document with department metadata.
    """
    try:
        if raw_text and raw_text.strip():
            return [
                docu(
                    page_content=raw_text.strip(),
                    metadata={"source": "raw_input", "page": 1, "department": dept},
                )
            ]
        return []
    except Exception as e:
        print(f"Error processing raw text: {e}")
        return None


# -------------------- Dispatcher --------------------
def extract_text(file_path: str | None = None, dept: str = "General Inquiry", text: str | None = None):
    """
    Unified entry point:
      - Pass file_path to extract from .txt / .pdf / .docx
      - Or pass raw `text`
    """
    if text is not None:
        return process_raw_text(text, dept)

    if file_path:
        if file_path.endswith(".txt"):
            return get_text_from_txt(file_path, dept)
        elif file_path.endswith(".pdf"):
            return get_text_from_pdf(file_path, dept)
        elif file_path.endswith(".docx"):
            return get_text_from_docx(file_path, dept)
        else:
            print(f"Unsupported file format: {file_path}")
            return None

    print("No input provided (file_path or text required).")
    return None

# def main():
#     # Example usage
#     text = extract_text("../../documents/Leave Policy.docx")
#     # print(text[0]['page_content'])
#     # print("--------------------------------------------------")
#     # print(text[0]['metadata'])
#     print(text)
# if __name__ == "__main__":
#     main()
