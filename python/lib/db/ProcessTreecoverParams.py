from .db import db, BaseModel


class ProcessTreecoverParams(BaseModel):
    collection_name = "process_treecover_params"
    schema = [
        {
            "name": "tile_id",
            "type": "text",
            "required": True,
            "unique": True,
            "options": {"min": 8, "max": 8}
        },
        {
            "name": "ndvi_diff_cut_trees",
            "type": "number",
            "required": True
        },
        {
            "name": "ndvi_tree_lower_bound",
            "type": "number",
            "required": True
        }
    ]

    def __init__(self, tile_id: str, ndvi_diff_cut_trees: float, ndvi_tree_lower_bound: float):
        super().__init__()
        self.tile_id = tile_id
        self.ndvi_diff_cut_trees = ndvi_diff_cut_trees
        self.ndvi_tree_lower_bound = ndvi_tree_lower_bound

    @classmethod
    def get_by_id(cls, tile_id: str):
        record = db.collection("process_treecover_params").get_one(tile_id)
        return cls(
            tile_id=record.tile_id,
            ndvi_diff_cut_trees=record.ndvi_diff_cut_trees,
            ndvi_tree_lower_bound=record.ndvi_tree_lower_bound
        )

ProcessTreecoverParams.create_collection()