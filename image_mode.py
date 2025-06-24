# image_mode.py
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

# Load the BLIP image captioning model and processor once at startup
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

def get_image_description(image_path: str) -> str:
    """
    Generate a textual description of the image at image_path
    using the BLIP image captioning model.
    """
    try:
        # Open the image and convert to RGB
        image = Image.open(image_path).convert("RGB")

        # Preprocess image and generate caption
        inputs = processor(images=image, return_tensors="pt")
        output_ids = model.generate(**inputs)

        # Decode the model's output into a string
        caption = processor.decode(output_ids[0], skip_special_tokens=True)
        return caption

    except Exception as e:
        return f"Error generating image description: {e}"