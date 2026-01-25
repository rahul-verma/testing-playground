# Order Tracking Demo (Testing Techniques)

## Setup

From inside `order-tracking-demo/`:

1. Create & activate a virtualenv
2. install pytest

`pip install -U pip pytest`

3. Run

`pytest`
or 
`pytest -vv`

4. As the test modules grow, you can run a particular module as:

`pytest -q tests/<test_modname>.py`