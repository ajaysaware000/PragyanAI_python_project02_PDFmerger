import gradio as gr
from pypdf import PdfReader, PdfWriter
from PIL import Image
import os
import tempfile


# ==========================================
# SHOW FILE INFORMATION
# ==========================================

def show_files(files):

    if not files:
        return "No files uploaded."

    result = "CURRENT FILE ORDER\n\n"

    total_pages = 0

    for i, file in enumerate(files, 1):

        file_name = os.path.basename(file)
        extension = os.path.splitext(file_name)[1].lower()

        if extension == ".pdf":

            reader = PdfReader(file)
            pages = len(reader.pages)

            total_pages += pages

            result += (
                f"{i}. 📄 {file_name} "
                f"- PDF - {pages} pages\n"
            )

        elif extension in [".jpg", ".jpeg", ".png", ".webp"]:

            result += (
                f"{i}. 🖼️ {file_name} "
                f"- Image - 1 page\n"
            )

            total_pages += 1

    result += "\n-------------------------\n"
    result += f"Total Files: {len(files)}\n"
    result += f"Total Pages: {total_pages}"

    return result


# ==========================================
# MOVE FILE UP
# ==========================================

def move_up(files, position):

    if not files:
        return files, "No files uploaded."

    try:
        position = int(position)
    except:
        return files, "Please enter a valid file number."

    index = position - 1

    if index <= 0:

        return files, "This file cannot be moved up."

    if index >= len(files):

        return files, "Invalid file number."

    # Swap files
    files[index - 1], files[index] = (
        files[index],
        files[index - 1]
    )

    return files, show_files(files)


# ==========================================
# MOVE FILE DOWN
# ==========================================

def move_down(files, position):

    if not files:
        return files, "No files uploaded."

    try:
        position = int(position)
    except:
        return files, "Please enter a valid file number."

    index = position - 1

    if index < 0:

        return files, "Invalid file number."

    if index >= len(files) - 1:

        return files, "This file cannot be moved down."

    # Swap files
    files[index], files[index + 1] = (
        files[index + 1],
        files[index]
    )

    return files, show_files(files)


# ==========================================
# MERGE PDF AND IMAGE FILES
# ==========================================

def merge_files(files):

    if not files:

        return (
            None,
            "❌ Please upload PDF or image files first."
        )

    writer = PdfWriter()

    total_pages = 0

    temporary_files = []

    try:

        # Process files in current order
        for file in files:

            file_name = os.path.basename(file)

            extension = os.path.splitext(
                file_name
            )[1].lower()

            # ----------------------------------
            # PDF FILE
            # ----------------------------------

            if extension == ".pdf":

                reader = PdfReader(file)

                for page in reader.pages:

                    writer.add_page(page)

                    total_pages += 1

            # ----------------------------------
            # IMAGE FILE
            # ----------------------------------

            elif extension in [
                ".jpg",
                ".jpeg",
                ".png",
                ".webp"
            ]:

                image = Image.open(file)

                # Convert image to RGB
                if image.mode != "RGB":

                    image = image.convert("RGB")

                # Create temporary PDF
                temp_file = tempfile.NamedTemporaryFile(
                    suffix=".pdf",
                    delete=False
                )

                temp_path = temp_file.name

                temp_file.close()

                # Save image as PDF
                image.save(
                    temp_path,
                    "PDF"
                )

                temporary_files.append(temp_path)

                # Read converted PDF
                image_reader = PdfReader(
                    temp_path
                )

                for page in image_reader.pages:

                    writer.add_page(page)

                    total_pages += 1

                image.close()

        # ----------------------------------
        # CREATE FINAL PDF
        # ----------------------------------

        output_file = "merged_document.pdf"

        with open(output_file, "wb") as output:

            writer.write(output)

        status = (
            "✅ MERGE SUCCESSFUL!\n\n"
            f"Total Files: {len(files)}\n"
            f"Total Pages: {total_pages}\n"
            f"Output File: {output_file}"
        )

        return output_file, status

    except Exception as e:

        return (
            None,
            f"❌ Error while merging files:\n{str(e)}"
        )

    finally:

        # Delete temporary image PDFs
        for temp_file in temporary_files:

            if os.path.exists(temp_file):

                os.remove(temp_file)


# ==========================================
# CLEAR ALL
# ==========================================

def clear_all():

    return [], "", "", None


# ==========================================
# GRADIO APPLICATION
# ==========================================

with gr.Blocks(
    title="PDF & Image Merger"
) as app:

    # ======================================
    # TITLE
    # ======================================

    gr.Markdown(
        """
        # 📄 PDF & Image Merger

        Upload PDF and image files, arrange their
        order, view the files, merge them into one
        PDF and download the final document.
        """
    )

    # ======================================
    # FILE UPLOAD
    # ======================================

    files = gr.File(
        label="📂 Upload PDF / Image Files",
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

    # ======================================
    # VIEW FILES
    # ======================================

    view_button = gr.Button(
        "👀 View Uploaded Files"
    )

    file_list = gr.Textbox(
        label="📋 Current File Order",
        lines=12
    )

    view_button.click(
        fn=show_files,
        inputs=files,
        outputs=file_list
    )

    # ======================================
    # ARRANGE FILES
    # ======================================

    gr.Markdown(
        """
        ## 🔢 Arrange File Order

        Enter the file number and use Move Up
        or Move Down.
        """
    )

    position = gr.Number(
        label="File Number",
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

    # IMPORTANT:
    # These events are INSIDE Blocks

    up_button.click(
        fn=move_up,
        inputs=[
            files,
            position
        ],
        outputs=[
            files,
            file_list
        ]
    )

    down_button.click(
        fn=move_down,
        inputs=[
            files,
            position
        ],
        outputs=[
            files,
            file_list
        ]
    )

    # ======================================
    # MERGE
    # ======================================

    gr.Markdown(
        """
        ## 🔀 Merge Files
        """
    )

    merge_button = gr.Button(
        "🔀 Merge PDF / Images",
        variant="primary"
    )

    status = gr.Textbox(
        label="📊 Status",
        lines=6
    )

    download_file = gr.File(
        label="📥 Download Merged PDF"
    )

    merge_button.click(
        fn=merge_files,
        inputs=files,
        outputs=[
            download_file,
            status
        ]
    )

    # ======================================
    # CLEAR
    # ======================================

    clear_button = gr.Button(
        "🗑️ Clear All"
    )

    clear_button.click(
        fn=clear_all,
        inputs=[],
        outputs=[
            files,
            file_list,
            status,
            download_file
        ]
    )


# ==========================================
# LAUNCH
# ==========================================

app.launch()
