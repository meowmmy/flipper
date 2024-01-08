
import base64
from nbt import nbt


def nbt_to_python(tag):
    if isinstance(tag, nbt.TAG_Compound):
        return {key: nbt_to_python(tag[key]) for key in tag.keys()}
    elif isinstance(tag, nbt.TAG_List):
        return [nbt_to_python(item) for item in tag]
    elif hasattr(tag, 'value'):  # For simple types like TAG_Int, TAG_String, etc.
        return tag.value
    else:
        return str(tag)
