import gradio as gr
from PIL import Image
from pypdf import PdfReader, PdfWriter
import os
import tempfile


# --------------------------------------------------
# Get file information
# --------------------------------------------------
def get_file_info(files):

    if not files:
        return "No files uploaded."

    result = "CURRENT FILE ORDER\n\n"

    for i, file in enumerate(files, 1):

        file_name = os.path.basename(file)
        extension = os.path.splitext(file_name)[1].lower()

        if extension == ".pdf":
            reader = PdfReader(file)
            pages = len(reader.pages)

            result += f"{i}. 📄 {file_name} - PDF - {pages} pages\n"

        else:
            result += f"{i}. 🖼️ {file_name} - Image\n"

    result += f"\nTotal files: {len(files)}"

    return result


# --------------------------------------------------
# Move file up
# --------------------------------------------------
def move_up(files, position):

    if not files:
        return files, "No files uploaded."

    try:
        position = int(position)
    except:
        return files, "Enter a valid file number."

    index = position - 1

    if index <= 0 or index >= len(files):
        return files, "Cannot move this file up."

    files[index - 1], files[index] = files[index], files[index - 1]

    return files, get_file_info(files)


# --------------------------------------------------
# Move file down
# --------------------------------------------------
def move_down(files, position):

    if not files:
        return files, "No files uploaded."

    try:
        position = int(position)
    except:
        return files, "Enter a valid file number."

    index = position - 1

    if index < 0 or index >= len(files) - 1:
        return files, "Cannot move this file down."

    files[index], files[index + 1] = files[index + 1], files[index]

    return files, get_file_info(files)


# --------------------------------------------------
# Merge PDF and Images
# --------------------------------------------------
def merge_files(files):

    if not files:
        return None, "Please upload PDF or image files."

    writer = PdfWriter()

    total_pages = 0

    for file in files:

        file_name = os.path.basename(file)
        extension = os.path.splitext(file_name)[1].lower()

        # -------------------------
        # PDF
        # -------------------------
        if extension == ".pdf":

            reader = PdfReader(file)

            for page in reader.pages:
                writer.add_page(page)
                total_pages += 1

        # -------------------------
        # Image
        # -------------------------
        elif extension in [".jpg", ".jpeg", ".png", ".webp"]:

            image = Image.open(file)

            # Convert image to RGB
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Temporary PDF
            temp_pdf = tempfile.NamedTemporaryFile(
                suffix=".pdf",
                delete=False
            )

            temp_pdf.close()

            image.save(temp_pdf.name, "PDF")

            image_reader = PdfReader(temp_pdf.name)

            for page in image_reader.pages:
                writer.add_page(page)
                total_pages += 1

            os.remove(temp_pdf.name)

    # -------------------------
    # Save final PDF
    # -------------------------
    output_file = "merged_document.pdf"

    with open(output_file, "wb") as f:
        writer.write(f)

    status = (
        "✅ Files merged successfully!\n\n"
        f"Total files: {len(files)}\n"
        f"Total pages: {total_pages}"
    )

    return output_file, status


# --------------------------------------------------
# Clear files
# --------------------------------------------------
def clear_files():

    return [], "", "", None


# --------------------------------------------------
# Gradio UI
# --------------------------------------------------
with gr.Blocks(title="PDF & Image Merger") as app:

    gr.Markdown(
        """
        # 📄 PDF & Image Merger

        Upload PDF and image files, arrange their order,
        view the current order, merge them into one PDF,
        and download the final file.
        """
    )

    # ----------------------------------------------
    # Upload
    # ----------------------------------------------

    files = gr.File(
        label="Upload PDF / Image Files",
        file_count="multiple",
        file_types=[
            ".pdf",
            ".jpg",
            ".jpeg",
            ".png",
            ".webp"
        ],
        type="filepath"
    )

    # ----------------------------------------------
    # View files
    # ----------------------------------------------

    view_button = gr.Button(
        "👀 View Uploaded Files"
    )

    file_list = gr.Textbox(
        label="Current File Order",
        lines=12
    )

    view_button.click(
        fn=get_file_info,
        inputs=files,
        outputs=file_list
    )

    # ----------------------------------------------
    # Arrange files
    # ----------------------------------------------

    gr.Markdown("## 🔢 Arrange File Order")

    position = gr.Number(
        label="Enter File Number",
        value=1,
        precision=0
    )

    with gr.Row():

        up_button = gr.Button(
            "⬆️ Move Up"
        )

        down_button = gr.Button(
            "⬇️ Move Down"
        )

    up_button.click(
        fn=move_up,
        inputs=[files, position],
        outputs=[files, file_list]
    )

    down_button.click(
        fn=move_down,
        inputs=[files, position],
        outputs=[files, file_list]
    )

    # ----------------------------------------------
    # Merge
    # ----------------------------------------------

    gr.Markdown("## 🔀 Merge Files")

    merge_button = gr.Button(
        "🔀 Merge PDF / Images",
        variant="primary"
    )

    status = gr.Textbox(
        label="Status",
        lines=5
    )

    download_file = gr.File(
        label="📥 Download Merged File"
    )

    merge_button.click(
        fn=merge_files,
        inputs=files,
        outputs=[download_file, status]
    )

    # ----------------------------------------------
    # Clear
    # ----------------------------------------------

    clear_button = gr.Button(
        "🗑️ Clear All"
    )

    clear_button.click(
        fn=clear_files,
        inputs=None,
        outputs=[
            files,
            file_list,
            status,
            download_file
        ]
    )


# --------------------------------------------------
# Launch
# --------------------------------------------------

app.launch()
