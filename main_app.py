import io
import streamlit as st
from pypdf import PdfReader, PdfWriter
import fitz


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="PragyanAI - PDF Merger",
    page_icon="📄",
    layout="centered"
)


# ============================================================
# HEADER
# ============================================================

st.title("PragyanAI - PDF Merger")

st.write(
    "Upload multiple PDF files, arrange their order, "
    "view them, merge them, and download the final PDF."
)

st.info(
    "Built with Python + Streamlit + PyPDF + PyMuPDF"
)


# ============================================================
# SESSION STATE
# ============================================================

if "pdf_files" not in st.session_state:
    st.session_state.pdf_files = []

if "merged_pdf" not in st.session_state:
    st.session_state.merged_pdf = None


# ============================================================
# FUNCTION — VIEW PDF AS IMAGES
# ============================================================

def display_pdf(pdf_file):

    try:

        # Read PDF bytes
        pdf_bytes = pdf_file.getvalue()

        # Open PDF using PyMuPDF
        document = fitz.open(
            stream=pdf_bytes,
            filetype="pdf"
        )

        # Number of pages
        page_count = len(document)

        st.caption(
            f"Total Pages: {page_count}"
        )

        # Display every page
        for page_number in range(page_count):

            page = document.load_page(
                page_number
            )

            # Render page as image
            pix = page.get_pixmap(
                matrix=fitz.Matrix(1.5, 1.5),
                alpha=False
            )

            # Convert to PNG bytes
            image_bytes = pix.tobytes(
                "png"
            )

            st.image(
                image_bytes,
                caption=f"Page {page_number + 1}",
                use_container_width=True
            )

        document.close()

    except Exception as e:

        st.error(
            f"❌ Error displaying PDF: {e}"
        )


# ============================================================
# SECTION 1 — UPLOAD PDF
# ============================================================

st.header("1. Upload PDF")

uploaded_files = st.file_uploader(
    "Select PDF Files",
    type=["pdf"],
    accept_multiple_files=True
)


# ============================================================
# STORE UPLOADED FILES
# ============================================================

if uploaded_files:

    new_file_names = [
        file.name
        for file in uploaded_files
    ]

    old_file_names = [
        file.name
        for file in st.session_state.pdf_files
    ]

    if new_file_names != old_file_names:

        st.session_state.pdf_files = uploaded_files

        # Clear previous merged PDF
        st.session_state.merged_pdf = None


# ============================================================
# SECTION 2 — ARRANGE FILE ORDER
# ============================================================

if st.session_state.pdf_files:

    st.divider()

    st.header("2. Arrange File Order")

    st.write(
        "Use the ⬆️ and ⬇️ buttons to arrange the "
        "PDF files before merging."
    )

    files = st.session_state.pdf_files

    for index in range(len(files)):

        file = files[index]

        col1, col2, col3, col4 = st.columns(
            [1, 5, 1, 1]
        )

        with col1:

            st.write(
                f"**{index + 1}**"
            )

        with col2:

            st.write(
                f"📄 **{file.name}**"
            )

        with col3:

            if st.button(
                "⬆️",
                key=f"up_{index}",
                disabled=(index == 0)
            ):

                files[index], files[index - 1] = (
                    files[index - 1],
                    files[index]
                )

                st.session_state.pdf_files = files

                # Clear old merged PDF
                st.session_state.merged_pdf = None

                st.rerun()

        with col4:

            if st.button(
                "⬇️",
                key=f"down_{index}",
                disabled=(index == len(files) - 1)
            ):

                files[index], files[index + 1] = (
                    files[index + 1],
                    files[index]
                )

                st.session_state.pdf_files = files

                # Clear old merged PDF
                st.session_state.merged_pdf = None

                st.rerun()


# ============================================================
# SECTION 3 — VIEW UPLOADED FILES
# ============================================================

if st.session_state.pdf_files:

    st.divider()

    st.header("3. View Uploaded Files")

    st.write(
        "Select a PDF file to view its pages."
    )

    files = st.session_state.pdf_files

    pdf_options = []

    for index, file in enumerate(
        files,
        start=1
    ):

        pdf_options.append(
            f"PDF {index} - {file.name}"
        )

    selected_pdf = st.selectbox(
        "Select PDF",
        pdf_options
    )

    selected_index = pdf_options.index(
        selected_pdf
    )

    selected_file = files[
        selected_index
    ]

    st.subheader(
        f"PDF {selected_index + 1}: "
        f"{selected_file.name}"
    )

    # Display PDF pages
    display_pdf(
        selected_file
    )


# ============================================================
# SECTION 4 — MERGE PDF
# ============================================================

if st.session_state.pdf_files:

    st.divider()

    st.header("4. Merge PDF")

    st.write(
        "The PDFs will be merged according to "
        "the order you arranged above."
    )

    # Show final order
    for index, file in enumerate(
        st.session_state.pdf_files,
        start=1
    ):

        st.write(
            f"**{index}.** {file.name}"
        )

    st.write("")

    if len(st.session_state.pdf_files) < 2:

        st.warning(
            "⚠️ Please upload at least 2 PDF files."
        )

    else:

        if st.button(
            "🔗 Merge PDF Files",
            type="primary",
            use_container_width=True
        ):

            try:

                # Create PDF writer
                writer = PdfWriter()

                # Add files in arranged order
                for file in st.session_state.pdf_files:

                    file.seek(0)

                    reader = PdfReader(
                        file
                    )

                    for page in reader.pages:

                        writer.add_page(
                            page
                        )

                # Create output buffer
                output = io.BytesIO()

                writer.write(
                    output
                )

                writer.close()

                # Store merged PDF
                st.session_state.merged_pdf = (
                    output.getvalue()
                )

                st.success(
                    "✅ PDF files merged successfully!"
                )

            except Exception as e:

                st.error(
                    f"❌ Error while merging PDFs: {e}"
                )


# ============================================================
# SECTION 5 — MERGED PDF
# ============================================================

if st.session_state.merged_pdf:

    st.divider()

    st.header("5. Merged PDF")

    st.success(
        "✅ Your merged PDF is ready!"
    )

    # --------------------------------------------------------
    # MERGED PDF VIEWER
    # --------------------------------------------------------

    st.subheader(
        "View Merged PDF"
    )

    try:

        # Open merged PDF
        merged_document = fitz.open(
            stream=st.session_state.merged_pdf,
            filetype="pdf"
        )

        st.caption(
            f"Total Pages: "
            f"{len(merged_document)}"
        )

        # Display pages
        for page_number in range(
            len(merged_document)
        ):

            page = merged_document.load_page(
                page_number
            )

            pix = page.get_pixmap(
                matrix=fitz.Matrix(1.5, 1.5),
                alpha=False
            )

            image_bytes = pix.tobytes(
                "png"
            )

            st.image(
                image_bytes,
                caption=f"Page {page_number + 1}",
                use_container_width=True
            )

        merged_document.close()

    except Exception as e:

        st.error(
            f"❌ Error displaying merged PDF: {e}"
        )


    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    st.subheader(
        "Download Merged PDF"
    )

    st.download_button(
        label="⬇️ Download Merged PDF",
        data=st.session_state.merged_pdf,
        file_name="merged_pdf.pdf",
        mime="application/pdf",
        use_container_width=True
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "PragyanAI | Python + Streamlit + PyPDF + PyMuPDF"
)
