import os
from pathlib import Path

import PIL.Image

BACKGROUND_IMAGE_PATH = "welcomebanner.png"
CHARACTERS_FOLDER_PATH = "characters"
OUTPUT_FOLDER_PATH = "output"


OUTPUT_FILENAME_PREFIX = "welcome_"
OUTPUT_EXT = "WebP"

STAMP_FROM = "right" # left, center, right

MARGIN_TOP_PERCENT = 5
TARGET_WIDTH_BACKGROUND_PERCENT = 50
MINIMUM_HEIGHT_BACKGROUND_PERCENT = 90

def stamp_character(background_path, character_image_path) -> PIL.Image.Image:
    background = PIL.Image.open(background_path).convert("RGBA")
    character_image = PIL.Image.open(character_image_path).convert("RGBA")

    character_image = character_image.crop(character_image.getbbox())

    # Stamps on the right side of the background

    target_character_width = int(background.width * TARGET_WIDTH_BACKGROUND_PERCENT / 100)
    target_character_height = int(
        target_character_width * (character_image.height / character_image.width)
    )

    if target_character_height < background.height * MINIMUM_HEIGHT_BACKGROUND_PERCENT / 100:
        target_character_height = int(background.height * MINIMUM_HEIGHT_BACKGROUND_PERCENT / 100)
        target_character_width = int(
            target_character_height * (character_image.width / character_image.height)
        )
    character_image = character_image.resize(
        (target_character_width, target_character_height)
    )

    if STAMP_FROM == "left":
        paste_x = 0
    elif STAMP_FROM == "center":
        paste_x = int(background.width / 2 - character_image.width / 2)
    elif STAMP_FROM == "right":
        paste_x = background.width - character_image.width
    else:
        raise ValueError(f"Unknown STAMP_FROM: {STAMP_FROM}")
    paste_y = int(background.height * MARGIN_TOP_PERCENT / 100)

    if paste_y + character_image.height < background.height:
        # Start from the bottom
        paste_y = background.height - character_image.height

    background.paste(character_image, (paste_x, paste_y), character_image)
    return background


def do_stamp():
    ext_list = [".png", ".jpg", ".jpeg", ".webp"]
    saved_filenames = []
    for ext in ext_list:
        for path in Path(CHARACTERS_FOLDER_PATH).rglob(f"*{ext}"):
            print(path)
            character_image = stamp_character(BACKGROUND_IMAGE_PATH, path)

            output_folder = OUTPUT_FOLDER_PATH

            for subfolder in reversed(path.parents):
                if subfolder.name and subfolder.name not in ("characters", ".") and subfolder.is_dir():
                    output_folder = os.path.join(output_folder, subfolder.name)
                    output_folder = output_folder.replace(os.sep, "/")
            os.makedirs(output_folder, exist_ok=True)

            filename = (
                OUTPUT_FILENAME_PREFIX + path.stem + f".{OUTPUT_EXT.lower()}"
            )
            if filename in saved_filenames:
                found_unique_filename = False
                idx = 2
                while not found_unique_filename:
                    filename = (
                        OUTPUT_FILENAME_PREFIX
                        + path.stem
                        + f"_{idx}"
                        + f".{OUTPUT_EXT.lower()}"
                    )
                    if filename not in saved_filenames:
                        found_unique_filename = True

            saved_filenames.append(filename)
            with open(output_folder + '/' + filename, "wb") as f:
                character_image.save(f, OUTPUT_EXT)


if __name__ == "__main__":
    do_stamp()
