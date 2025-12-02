"""Font rasterization module using FreeType."""

import freetype
from typing import Tuple, Optional, List
from dataclasses import dataclass
from fontTools.ttLib import TTFont


@dataclass
class GlyphBitmap:
    """Represents a rasterized glyph bitmap."""
    char_code: int
    width: int
    height: int
    advance_x: int
    offset_x: int
    offset_y: int
    bitmap: bytes  # 1-bit bitmap data
    pitch: int  # Bytes per row (may include padding)

    @property
    def char(self) -> str:
        """Get the character representation."""
        try:
            return chr(self.char_code)
        except ValueError:
            return '?'


class RasterizerError(Exception):
    """Exception raised for rasterization errors."""
    pass


class FontRasterizer:
    """Rasterizes font glyphs to 1-bit bitmaps using FreeType."""

    def __init__(self, font_path: str, size: int = 16):
        """Initialize the font rasterizer.

        Args:
            font_path: Path to the font file
            size: Font size in pixels

        Raises:
            RasterizerError: If font cannot be loaded
        """
        self.font_path = font_path
        self.size = size
        self.face: Optional[freetype.Face] = None

        self._load_face()

    def _load_face(self) -> None:
        """Load the font face using FreeType."""
        try:
            self.face = freetype.Face(self.font_path)
            # Set pixel size (width, height)
            # Setting width to 0 means it will be calculated proportionally
            self.face.set_pixel_sizes(0, self.size)
        except Exception as e:
            raise RasterizerError(f"Failed to load font with FreeType: {e}")

    def rasterize_glyph(self, char_code: int) -> Optional[GlyphBitmap]:
        """Rasterize a single glyph to a 1-bit bitmap.

        Args:
            char_code: Unicode code point of the character

        Returns:
            GlyphBitmap object or None if character cannot be rendered

        Raises:
            RasterizerError: If rasterization fails
        """
        if self.face is None:
            raise RasterizerError("Font face not loaded")

        try:
            # Load the glyph
            self.face.load_char(char_code, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_MONO)

            bitmap = self.face.glyph.bitmap
            metrics = self.face.glyph.metrics

            if bitmap.width == 0 or bitmap.rows == 0:
                # Empty glyph (e.g., space character)
                return GlyphBitmap(
                    char_code=char_code,
                    width=0,
                    height=0,
                    advance_x=self.face.glyph.advance.x >> 6,  # Convert from 26.6 fixed point
                    offset_x=0,
                    offset_y=0,
                    bitmap=b'',
                    pitch=0
                )

            # Convert 8bpp grayscale to 1bpp
            bitmap_data, pitch = self._convert_to_1bit(bitmap)

            return GlyphBitmap(
                char_code=char_code,
                width=bitmap.width,
                height=bitmap.rows,
                advance_x=self.face.glyph.advance.x >> 6,
                offset_x=self.face.glyph.bitmap_left,
                offset_y=self.face.glyph.bitmap_top,
                bitmap=bitmap_data,
                pitch=pitch
            )

        except Exception as e:
            # Some characters might not be available in the font
            return None

    def _convert_to_1bit(self, bitmap: freetype.Bitmap) -> Tuple[bytes, int]:
        """Convert FreeType bitmap to 1-bit format.

        Args:
            bitmap: FreeType bitmap object

        Returns:
            Tuple of (1-bit bitmap data as bytes, pitch in bytes)
        """
        if bitmap.pixel_mode == freetype.FT_PIXEL_MODE_MONO:
            # Already 1-bit, just copy the data
            # For MONO mode, pitch is already in bytes
            return bytes(bitmap.buffer), bitmap.pitch

        # Convert grayscale to 1-bit
        # Threshold at 128 (middle gray)
        # Calculate bytes per row (same as FreeType would use)
        bytes_per_row = (bitmap.width + 7) // 8
        result = []
        threshold = 128

        for y in range(bitmap.rows):
            row_bits = 0
            for x in range(bitmap.width):
                pixel_index = y * bitmap.pitch + x
                pixel_value = bitmap.buffer[pixel_index]

                if pixel_value >= threshold:
                    bit_position = 7 - (x % 8)
                    row_bits |= (1 << bit_position)

                if (x + 1) % 8 == 0 or x == bitmap.width - 1:
                    result.append(row_bits)
                    row_bits = 0

        return bytes(result), bytes_per_row

    def rasterize_charset(self, char_codes: set[int]) -> List[GlyphBitmap]:
        """Rasterize multiple characters.

        Args:
            char_codes: Set of character codes to rasterize

        Returns:
            List of GlyphBitmap objects (excluding failed glyphs)
        """
        glyphs = []

        for char_code in sorted(char_codes):
            glyph = self.rasterize_glyph(char_code)
            if glyph is not None:
                glyphs.append(glyph)

        return glyphs

    def get_font_metrics(self) -> dict:
        """Get font metrics information.

        Returns:
            Dictionary with font metrics
        """
        if self.face is None:
            return {}

        return {
            'size': self.size,
            'height': self.face.size.height >> 6,
            'ascender': self.face.size.ascender >> 6,
            'descender': self.face.size.descender >> 6,
            'max_advance': self.face.size.max_advance >> 6,
            'underline_position': self.face.underline_position >> 6,
            'underline_thickness': self.face.underline_thickness >> 6,
        }

    def preview_glyph(self, glyph: GlyphBitmap, char: str = '#', empty: str = '.') -> str:
        """Generate a text preview of a glyph bitmap.

        Args:
            glyph: GlyphBitmap to preview
            char: Character to use for set bits
            empty: Character to use for unset bits

        Returns:
            Multi-line string representation of the bitmap
        """
        if glyph.width == 0 or glyph.height == 0:
            return f"[Empty glyph: '{glyph.char}']"

        lines = []
        lines.append(f"Character: '{glyph.char}' (U+{glyph.char_code:04X})")
        lines.append(f"Size: {glyph.width}x{glyph.height}, Advance: {glyph.advance_x}px")
        lines.append("")

        byte_index = 0
        for y in range(glyph.height):
            row = ""
            for x in range(glyph.width):
                byte_pos = byte_index + (x // 8)
                bit_pos = 7 - (x % 8)

                if byte_pos < len(glyph.bitmap):
                    bit_set = (glyph.bitmap[byte_pos] >> bit_pos) & 1
                    row += char if bit_set else empty
                else:
                    row += empty

            lines.append(row)
            # Move to next row in bitmap using pitch
            byte_index += glyph.pitch

        return '\n'.join(lines)
