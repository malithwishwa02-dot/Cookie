from pypdf import PdfReader

pdf_path = "/home/user/uploaded_files/Prometheus Unified Core v2.1.pdf"
output_path = "/home/user/webapp/Prometheus_Unified_Core_v2.1.raw.txt"

reader = PdfReader(pdf_path)
text = ""
for page in reader.pages:
    text += page.extract_text() + "\n"

with open(output_path, "w") as f:
    f.write(text)

print(f"Extracted {len(text)} characters to {output_path}")
