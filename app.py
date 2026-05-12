ValueError: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).
Traceback:
File "/mount/src/cznon-dashboard/app.py", line 102, in <module>
    fig.add_trace(go.Scatter(
                  ~~~~~~~~~~^
        x=agg_trend['Date'], y=agg_trend['Points'],
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<4 lines>...
        hovertemplate="<b>%{x|%B %Y}</b><br>Score: %{y:.1f} pts<extra></extra>"
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ))
    ^
File "/home/adminuser/venv/lib/python3.14/site-packages/plotly/graph_objs/_scatter.py", line 2797, in __init__
    self._set_property("marker", arg, marker)
    ~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.14/site-packages/plotly/basedatatypes.py", line 4403, in _set_property
    _set_property_provided_value(self, name, arg, provided)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.14/site-packages/plotly/basedatatypes.py", line 398, in _set_property_provided_value
    obj[name] = val
    ~~~^^^^^^
File "/home/adminuser/venv/lib/python3.14/site-packages/plotly/basedatatypes.py", line 4924, in __setitem__
    self._set_compound_prop(prop, value)
    ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.14/site-packages/plotly/basedatatypes.py", line 5335, in _set_compound_prop
    val = validator.validate_coerce(val, skip_invalid=self._skip_invalid)
File "/home/adminuser/venv/lib/python3.14/site-packages/_plotly_utils/basevalidators.py", line 2468, in validate_coerce
    v = self.data_class(v, skip_invalid=skip_invalid, _validate=_validate)
File "/home/adminuser/venv/lib/python3.14/site-packages/plotly/graph_objs/scatter/_marker.py", line 1129, in __init__
    self._process_kwargs(**dict(arg, **kwargs))
    ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.14/site-packages/plotly/basedatatypes.py", line 4451, in _process_kwargs
    raise err
