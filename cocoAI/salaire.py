# Import required libraries
import json

from IPython.display import Markdown, display
from mistralai import DocumentURLChunk, Mistral
from mistralai.models import OCRResponse

from common.keys import MISTRAL_API_KEY
from common.path import COMMERCIAL_ONE_DRIVE_PATH, rapatrie_file

CHIEN_QUI_FUME_PATH = (
    COMMERCIAL_ONE_DRIVE_PATH
    / "2 - DOSSIERS à l'ETUDE"
    / "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF"
)


api_key = MISTRAL_API_KEY  # Replace with your API key
client = Mistral(api_key=api_key)

pdf_path = (
    CHIEN_QUI_FUME_PATH / "3. DOCUMENTATION FINANCIÈRE" / "2022 - GALLA - BILAN.pdf"
)
pdf_file = rapatrie_file(pdf_path)

# TODO : reprendre ici


# Upload PDF file to Mistral's OCR service
uploaded_file = client.files.upload(
    file={
        "file_name": pdf_file.stem,
        "content": pdf_file.read_bytes(),
    },
    purpose="ocr",
)

# Get URL for the uploaded file
signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)

# Process PDF with OCR, including embedded images
pdf_response = client.ocr.process(
    document=DocumentURLChunk(document_url=signed_url.url),
    model="mistral-ocr-latest",
    include_image_base64=True,
)

# Convert response to JSON format
response_dict = json.loads(pdf_response.model_dump_json())

print(json.dumps(response_dict, indent=4)[0:1000])  # check the first 1000 characters


def replace_images_in_markdown(markdown_str: str, images_dict: dict) -> str:
    """
    Replace image placeholders in markdown with base64-encoded images.

    Args:
        markdown_str: Markdown text containing image placeholders
        images_dict: Dictionary mapping image IDs to base64 strings

    Returns:
        Markdown text with images replaced by base64 data
    """
    for img_name, base64_str in images_dict.items():
        markdown_str = markdown_str.replace(
            f"![{img_name}]({img_name})", f"![{img_name}]({base64_str})"
        )
    return markdown_str


def get_combined_markdown(ocr_response: OCRResponse) -> str:
    """
    Combine OCR text and images into a single markdown document.

    Args:
        ocr_response: Response from OCR processing containing text and images

    Returns:
        Combined markdown string with embedded images
    """
    markdowns: list[str] = []
    # Extract images from page
    for page in ocr_response.pages:
        image_data = {}
        for img in page.images:
            image_data[img.id] = img.image_base64
        # Replace image placeholders with actual images
        markdowns.append(replace_images_in_markdown(page.markdown, image_data))

    return "\n\n".join(markdowns)


# Display combined markdowns and images
display(Markdown(get_combined_markdown(pdf_response)))


def main():

    return


if __name__ == "__main__":
    main()
