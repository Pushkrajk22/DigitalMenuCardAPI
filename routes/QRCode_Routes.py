from fastapi import APIRouter, Query, Security
from fastapi.responses import StreamingResponse
from fastapi.security.api_key import APIKeyHeader
import io
import segno

router = APIRouter(prefix="/qr", tags=["QR Code"])
api_key_header = APIKeyHeader(name="Authorization", auto_error=True)

@router.get("/generate_qr")
def generate_qr(
    link: str = Query(..., description="URL to encode in QR"),
    Authorization: str = Security(api_key_header)
):
    qr = segno.make(link)

    # Generate PNG in memory (you can also use SVG or PDF)
    img_io = io.BytesIO()
    qr.save(img_io, kind='png', scale=10)  # `scale` controls image size
    img_io.seek(0)

    return StreamingResponse(img_io, media_type="image/png")
