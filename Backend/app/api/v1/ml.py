import io
import ipaddress
import socket
import sys
from pathlib import Path
from urllib.parse import urlsplit
import httpx
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel
from PIL import Image
from app.schemas.schemas import DiseasePredictionResponse

router = APIRouter(prefix="/ml", tags=["ml"])
MAX_IMAGE_BYTES = 10 * 1024 * 1024

class ImageUrlPredictRequest(BaseModel):
    image_url: str


def validate_image_url(image_url: str) -> None:
    try:
        parsed = urlsplit(image_url)
        hostname = parsed.hostname
        parsed_port = parsed.port
    except ValueError as error:
        raise HTTPException(status_code=400, detail="Image URL is malformed.") from error

    if parsed.scheme not in {"http", "https"} or not hostname or parsed.username or parsed.password:
        raise HTTPException(status_code=400, detail="Image URL must be a valid HTTP or HTTPS URL.")

    try:
        port = parsed_port or (443 if parsed.scheme == "https" else 80)
        addresses = {
            ipaddress.ip_address(result[4][0])
            for result in socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
        }
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail="Image URL host could not be resolved.") from error

    if not addresses or any(not address.is_global for address in addresses):
        raise HTTPException(status_code=400, detail="Image URL must resolve to a public host.")


async def fetch_image_from_url(image_url: str) -> bytes:
    validate_image_url(image_url)
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
            async with client.stream("GET", image_url, headers={"Accept": "image/*"}) as response:
                if 300 <= response.status_code < 400:
                    raise HTTPException(status_code=400, detail="Image URL redirects; provide a direct image URL.")
                if response.status_code >= 400:
                    raise HTTPException(status_code=502, detail=f"Image URL fetch failed with HTTP {response.status_code}.")

                content_type = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
                if content_type and not content_type.startswith("image/") and content_type != "application/octet-stream":
                    raise HTTPException(status_code=400, detail="Image URL must point to an image.")

                contents = bytearray()
                async for chunk in response.aiter_bytes():
                    contents.extend(chunk)
                    if len(contents) > MAX_IMAGE_BYTES:
                        raise HTTPException(status_code=413, detail="Image must be 10 MB or smaller.")
    except HTTPException:
        raise
    except httpx.TimeoutException as error:
        raise HTTPException(status_code=504, detail="Timed out while fetching image URL.") from error
    except httpx.HTTPError as error:
        raise HTTPException(status_code=502, detail="Could not fetch the image URL.") from error

    return bytes(contents)


def predict_image(contents: bytes) -> DiseasePredictionResponse:
    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"Invalid image: {error}") from error

    try:
        root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        if str(root_dir) not in sys.path:
            sys.path.insert(0, str(root_dir))
        from Disease_prediction_model.model2_disease_prediction import predict_disease as run_model

        prediction = run_model(contents)
    except Exception as error:
        raise HTTPException(status_code=503, detail="Disease prediction model is unavailable.") from error

    scientific_name = "N/A"
    cause = prediction["cause"]
    if "(" in cause and ")" in cause:
        scientific_name = cause.split("(", 1)[1].split(")", 1)[0].replace("*", "")

    return DiseasePredictionResponse(
        name=prediction["full_label"],
        scientificName=scientific_name,
        confidence=prediction["confidence_pct"],
        cause=cause,
        preventiveMeasures=prediction["treatment_measures"],
        plantType=prediction["crop"]
    )


@router.post("/predict-disease", response_model=DiseasePredictionResponse)
async def predict_disease(file: UploadFile = File(...)):
    try:
        contents = await file.read()
    except Exception as error:
        raise HTTPException(status_code=400, detail="Could not read uploaded image.") from error
    return predict_image(contents)


@router.post("/predict-disease-json", response_model=DiseasePredictionResponse)
async def predict_disease_from_url(request: ImageUrlPredictRequest):
    contents = await fetch_image_from_url(request.image_url)
    return predict_image(contents)
