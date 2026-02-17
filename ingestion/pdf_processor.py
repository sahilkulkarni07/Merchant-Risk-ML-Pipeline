import pdfplumber
import asyncio


async def extract_pdf_text_async(file_path: str) -> str:

    # Asynchronously extracts text from a PDF file.
    # Simulate async background processing
    
    await asyncio.sleep(0.1)

    text_content = []

    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
    except Exception as e:
        raise RuntimeError(f"Failed to process PDF: {e}")

    return "\n".join(text_content)
