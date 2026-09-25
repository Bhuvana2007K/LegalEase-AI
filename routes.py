from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from schemas import (
    DocumentRequest,
    ExportRequest,
)

from document_service import (
    gemini_service,
)
from document_utils.exporters import (
    export_docx,
    export_pdf,
    export_txt,
)

from document_utils.text_utils import (
    sanitize_text,
)


router = APIRouter()


# ============================================================
# GENERATE DOCUMENT
# ============================================================

@router.post(
    "/generate",
    tags=["Documents"],
)
def generate_document(
    request: DocumentRequest,
):

    try:

        content = (
            gemini_service.generate_document(
                request
            )
        )

        return {
            "document_type": request.document_type,
            "content": content,
            "model": gemini_service.model_name,
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except RuntimeError as error:

        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error


# ============================================================
# EXPORT DOCUMENT
# ============================================================

@router.post(
    "/export/{format}",
    tags=["Documents"],
)
def export_document(
    format: str,
    request: ExportRequest,
):

    if format not in {
        "txt",
        "docx",
        "pdf",
    }:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported format. "
                "Use txt, docx, or pdf."
            ),
        )

    content = sanitize_text(
        request.content
    )

    try:

        # ----------------------------------------------------
        # TXT
        # ----------------------------------------------------

        if format == "txt":

            data = export_txt(
                content
            )

            return Response(
                content=data,
                media_type=(
                    "text/plain; charset=utf-8"
                ),
                headers={
                    "Content-Disposition":
                    (
                        'attachment; '
                        'filename="legalease_document.txt"'
                    )
                },
            )

        # ----------------------------------------------------
        # DOCX
        # ----------------------------------------------------

        if format == "docx":

            data = export_docx(
                content,
                request.document_type,
            )

            return Response(
                content=data,
                media_type=(
                    "application/"
                    "vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                headers={
                    "Content-Disposition":
                    (
                        'attachment; '
                        'filename="legalease_document.docx"'
                    )
                },
            )

        # ----------------------------------------------------
        # PDF
        # ----------------------------------------------------

        data = export_pdf(
            content,
            request.document_type,
        )

        return Response(
            content=data,
            media_type="application/pdf",
            headers={
                "Content-Disposition":
                (
                    'attachment; '
                    'filename="legalease_document.pdf"'
                )
            },
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Document export failed: {error}"
            ),
        ) from error
