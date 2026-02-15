from .db import db, BaseModel


class IngestParams(BaseModel):
    collection_name = "ingest_params"
    schema = [
        {
            "name": "tile_id",
            "type": "text",
            "required": True,
            "unique": True,
            "options": {"min": 8, "max": 8}
        },
        {
            "name": "valid_image_pixels",
            "type": "number",
            "required": True
        }
    ]

    def __init__(self, tile_id: str, valid_image_pixels: float):
        super().__init__()
        self.tile_id = tile_id
        self.valid_image_pixels = valid_image_pixels

    @classmethod
    def get_by_id(cls, tile_id: str):
        record = db.collection("ingest_params").get_one(tile_id)
        return cls(
            tile_id=record.tile_id,
            valid_image_pixels=record.valid_image_pixels
        )

IngestParams.create_collection()