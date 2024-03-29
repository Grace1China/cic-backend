from rest_framework.metadata import BaseMetadata

class MinimalMetadata(BaseMetadata):
    """
    Don't include field and other information for `OPTIONS` requests.
    Just return the name and description.
    """
    def determine_metadata(self, request, view):
        return {
            'name': view.get_view_name(),
            'description': view.get_view_description(),
            "actions": {
                "POST": {
                    "note": {
                        "type": "string",
                        "required": False,
                        "read_only": False,
                        "label": "title",
                        "max_length": 100
                    }
                }
            }
        }

    