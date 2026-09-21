import gradio as gr
from pypdf import PdfReader, PdfWriter
import os


# Show uploaded PDF files
def show_files(files):

    if not files:
        return "No PDF files uploaded."

    result = "Uploaded PDF Files:\n\n"

    for i, file in enumerate(files, 1):

        reader = PdfReader(file)
        pages = len(reader.pages)
        file_name = os.path.basename(file)

        result += f"{i}. {file_name} - {pages} pages\n"

    return result


# Merge PDF files
def merge_pdfs(files):

    if not files:
        return None, "Please upload PDF files first."

    if len(files) < 2:
        return None, "Please upload at least 2 PDF files."

    writer = PdfWriter()

    total_pages = 0

    for file in files:

        reader = PdfReader(file)

        for page in reader.pages:
            writer.add_page(page)
            total_pages += 1

    output_file = "merged_pdf.pdf"

    with open(output_file, "wb") as f:
        writer.write(f)

    status = (
        f"PDF files merged successfully!\n"
        f"Total files: {len(files)}\n"
        f"Total pages: {total_pages}"
    )

    return output_file, status


# Gradio interface
with gr.Blocks(title="PDF Manager") as app:

    gr.Markdown(
        """
        # 📄 PDF Manager

        Upload multiple PDF files, view their details,
        merge them, and download the merged PDF.
        """
    )

    # PDF Upload
    files = gr.File(
        label="Upload PDF Files",
        file_count="multiple",
        file_types=[".pdf"],
        type="filepath"
    )

    # Show files button
    show_button = gr.Button(
        "📋 Show File List"
    )

    # File information
    file_list = gr.Textbox(
        label="File List / Distribution",
        lines=10
    )

    show_button.click(
        fn=show_files,
        inputs=files,
        outputs=file_list
    )

    # Merge button
    merge_button = gr.Button(
        "🔗 Merge PDFs"
    )

    # Status
    status = gr.Textbox(
        label="Status",
        lines=4
    )

    # Download file
    download_file = gr.File(
        label="Download Merged PDF"
    )

    merge_button.click(
        fn=merge_pdfs,
        inputs=files,
        outputs=[download_file, status]
    )


# Launch application
app.launch()
