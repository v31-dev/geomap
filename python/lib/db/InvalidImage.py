from .db import BaseModel


class InvalidImage(BaseModel):
    collection_name = "invalid_images"
    schema = [
        {
            "name": "_composite_id",
            "type": "text",
            "required": True,
            "unique": True
        },
        {
            "name": "tile_id",
            "type": "text",
            "required": True,
            "options": {"min": 8, "max": 8}
        },
        {
            "name": "interval_id",
            "type": "number",
            "required": True
        },
        {
            "name": "reason",
            "type": "text",
            "required": True
        },
        {
            "name": "valid_pixel_percentage",
            "type": "number",
            "required": True
        }
    ]

    def __init__(self, tile_id: str, interval_id: int, reason: str, valid_pixel_percentage: float):
        super().__init__()
        self.tile_id = tile_id
        self.interval_id = interval_id
        self.reason = reason
        self.valid_pixel_percentage = valid_pixel_percentage
        self._composite_id = f"{tile_id}:{interval_id}"

    def get_lat(self):
        return self.tile_id[5:8]

    def get_lon(self):
        return self.tile_id[0:4]

InvalidImage.create_collection()