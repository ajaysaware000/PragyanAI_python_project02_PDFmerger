import io
import streamlit as st
from pypdf import PdfReader, PdfWriter


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
    "Upload multiple PDF files, view the file list, "
    "merge them into a single PDF, and download the result."
)

st.info(
    "Built with Python + Streamlit + PyPDF. "
    "All PDF files are processed for merging."
)


# ============================================================
# SESSION STATE
# ============================================================

if "merged_pdf" not in st.session_state:
    st.session_state.merged_pdf = None

if "merged_filename" not in st.session_state:
    st.session_state.merged_filename = "merged_pdf.pdf"


# ============================================================
# SECTION 1 — UPLOAD PDF FILES
# ============================================================

st.header("1. Upload PDF Files")

uploaded_files = st.file_uploader(
    "Select PDF Files",
    type=["pdf"],
    accept_multiple_files=True
)


# ============================================================
# SECTION 2 — DISPLAY FILE LIST
# ============================================================

if uploaded_files:

    st.divider()

    st.header("2. Uploaded PDF File List")

    st.write(
        f"**Total Files:** {len(uploaded_files)}"
    )

    for index, uploaded_file in enumerate(
        uploaded_files,
        start=1
    ):

        file_size = uploaded_file.size / 1024

        st.write(
            f"**{index}.** {uploaded_file.name} "
            f"— {file_size:.2f} KB"
        )


# ============================================================
# SECTION 3 — MERGE PDF FILES
# ============================================================

if uploaded_files:

    st.divider()

    st.header("3. Merge PDF Files")

    st.write(
        "PDF files will be merged in the same order "
        "as displayed above."
    )

    if st.button(
        "🔗 Merge PDF Files",
        type="primary",
        use_container_width=True
    ):

        if len(uploaded_files) < 2:

            st.warning(
                "⚠️ Please upload at least 2 PDF files."
            )

        else:

            try:

                # Create PDF writer
                pdf_writer = PdfWriter()

                # Add each uploaded PDF
                for uploaded_file in uploaded_files:

                    uploaded_file.seek(0)

                    pdf_reader = PdfReader(
                        uploaded_file
                    )

                    # Add every page
                    for page in pdf_reader.pages:

                        pdf_writer.add_page(page)

                # Create memory buffer
                output_buffer = io.BytesIO()

                # Write merged PDF
                pdf_writer.write(
                    output_buffer
                )

                pdf_writer.close()

                # Get PDF bytes
                st.session_state.merged_pdf = (
                    output_buffer.getvalue()
                )

                st.session_state.merged_filename = (
                    "merged_pdf.pdf"
                )

                st.success(
                    f"✅ Successfully merged "
                    f"{len(uploaded_files)} PDF files!"
                )

            except Exception as e:

                st.session_state.merged_pdf = None

                st.error(
                    f"❌ Error while merging PDFs: {e}"
                )


# ============================================================
# SECTION 4 — MERGED PDF STATUS
# ============================================================

if st.session_state.merged_pdf:

    st.divider()

    st.header("4. Merged PDF Status")

    st.success(
        "✅ PDF files have been merged successfully."
    )

    merged_size = (
        len(st.session_state.merged_pdf) / 1024
    )

    st.write(
        f"**Output File:** "
        f"{st.session_state.merged_filename}"
    )

    st.write(
        f"**Merged File Size:** "
        f"{merged_size:.2f} KB"
    )

    st.write(
        "Your merged PDF is ready to download."
    )


# ============================================================
# SECTION 5 — DOWNLOAD MERGED PDF
# ============================================================

if st.session_state.merged_pdf:

    st.divider()

    st.header("5. Download Merged PDF")

    st.download_button(
        label="⬇️ Download Merged PDF",
        data=st.session_state.merged_pdf,
        file_name=st.session_state.merged_filename,
        mime="application/pdf",
        use_container_width=True
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "PragyanAI | Python + Streamlit + PyPDF"
)
