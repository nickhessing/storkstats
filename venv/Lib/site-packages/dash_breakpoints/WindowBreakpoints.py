# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class WindowBreakpoints(Component):
    """A WindowBreakpoints component.
Component description

Keyword arguments:

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- height (number; optional):
    Current height, NOTE: avoid using in a server callback.

- heightBreakpoint (string; optional):
    Current height breakpoint.

- heightBreakpointNames (list of strings; optional):
    Name of each height breakpoint, array of length N + 1.

- heightBreakpointThresholdsPx (list of numbers; optional):
    Window heights on which to separate breakpoints, array of length
    N.

- width (number; optional):
    Current width, NOTE: avoid using in a server callback.

- widthBreakpoint (string; optional):
    Current width breakpoint.

- widthBreakpointNames (list of strings; optional):
    Name of each width breakpoint, array of length N + 1.

- widthBreakpointThresholdsPx (list of numbers; optional):
    Window widths on which to separate breakpoints, array of length N."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_breakpoints'
    _type = 'WindowBreakpoints'
    @_explicitize_args
    def __init__(self, widthBreakpointThresholdsPx=Component.UNDEFINED, widthBreakpointNames=Component.UNDEFINED, heightBreakpointThresholdsPx=Component.UNDEFINED, heightBreakpointNames=Component.UNDEFINED, width=Component.UNDEFINED, height=Component.UNDEFINED, widthBreakpoint=Component.UNDEFINED, heightBreakpoint=Component.UNDEFINED, id=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'height', 'heightBreakpoint', 'heightBreakpointNames', 'heightBreakpointThresholdsPx', 'width', 'widthBreakpoint', 'widthBreakpointNames', 'widthBreakpointThresholdsPx']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'height', 'heightBreakpoint', 'heightBreakpointNames', 'heightBreakpointThresholdsPx', 'width', 'widthBreakpoint', 'widthBreakpointNames', 'widthBreakpointThresholdsPx']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(WindowBreakpoints, self).__init__(**args)
