"""Compatibility shims for third-party libraries.

`apply_gradio_client_patch` works around a known bug in ``gradio_client`` 1.3
(the version pinned by Gradio 4.x): when a component's JSON schema contains a
boolean ``additionalProperties`` value, ``get_type`` does ``"const" in schema``
on that bool and raises ``TypeError: argument of type 'bool' is not iterable``
while building the ``/info`` API schema. We guard the two entry points so a
non-dict schema degrades to ``"Any"`` instead of crashing the route.
"""

from __future__ import annotations


def apply_gradio_client_patch() -> None:
    import gradio_client.utils as gcu

    if getattr(gcu, "_data_analyst_patched", False):
        return

    _orig_get_type = gcu.get_type
    _orig_to_py = gcu._json_schema_to_python_type

    def _safe_get_type(schema):
        if not isinstance(schema, dict):
            return "Any"
        return _orig_get_type(schema)

    def _safe_to_py(schema, defs=None):
        if isinstance(schema, bool):
            return "Any"
        return _orig_to_py(schema, defs)

    gcu.get_type = _safe_get_type
    gcu._json_schema_to_python_type = _safe_to_py
    gcu._data_analyst_patched = True
