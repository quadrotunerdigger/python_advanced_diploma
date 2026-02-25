"""Tests for media API."""

import io
import pytest
from httpx import AsyncClient


class TestUploadMedia:
    """Tests for POST /api/medias."""

    @pytest.mark.asyncio
    async def test_upload_image_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test successful image upload."""
        # Create a simple test image (1x1 pixel PNG)
        png_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
            b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
        )

        response = await client.post(
            "/api/medias",
            files={"file": ("test.png", io.BytesIO(png_data), "image/png")},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["result"] is True
        assert "media_id" in data
        assert isinstance(data["media_id"], int)

    @pytest.mark.asyncio
    async def test_upload_jpeg_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test successful JPEG upload."""
        # Minimal valid JPEG (1x1 pixel)
        jpeg_data = (
            b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01"
            b"\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06"
            b"\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b"
            b"\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c"
            b"\x1c $.' ,02444444444444444444444444444444444444444444"
            b"\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00"
            b"\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01"
            b"\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04"
            b"\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02"
            b"\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01"
            b"}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07\"q"
            b"\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82"
            b"\t\n\x16\x17\x18\x19\x1a%&'()*456789:CDEFGHIJSTUVWXYZ"
            b"cdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92"
            b"\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6"
            b"\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba"
            b"\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5"
            b"\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8"
            b"\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff"
            b"\xda\x00\x08\x01\x01\x00\x00?\x00\xfb\xd5\x00\x00\x00"
            b"\x00\xff\xd9"
        )

        response = await client.post(
            "/api/medias",
            files={"file": ("test.jpg", io.BytesIO(jpeg_data), "image/jpeg")},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["result"] is True

    @pytest.mark.asyncio
    async def test_upload_without_auth(
        self,
        client: AsyncClient,
    ):
        """Test upload without authentication."""
        png_data = b"\x89PNG\r\n\x1a\n"

        response = await client.post(
            "/api/medias",
            files={"file": ("test.png", io.BytesIO(png_data), "image/png")},
        )

        assert response.status_code == 422  # Missing api-key header

    @pytest.mark.asyncio
    async def test_upload_invalid_file_type(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test upload with invalid file type."""
        response = await client.post(
            "/api/medias",
            files={"file": ("test.txt", io.BytesIO(b"text content"), "text/plain")},
            headers=auth_headers,
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["result"] is False
        assert data["detail"]["error_type"] == "InvalidFile"

    @pytest.mark.asyncio
    async def test_upload_no_file(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        """Test upload without file."""
        response = await client.post(
            "/api/medias",
            headers=auth_headers,
        )

        assert response.status_code == 422  # Missing file