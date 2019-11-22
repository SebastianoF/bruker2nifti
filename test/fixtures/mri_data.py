import os
import shutil

import pytest

@pytest.fixture
def banana_data(tmp_path, request):
    input_dir = os.path.join(os.path.abspath(request.fspath.dirname), "..",
      "test_data", "bru_banana")
    output_dir = os.path.join(tmp_path, "bru_banana")
    shutil.copytree(input_dir, output_dir)
    return os.path.join(tmp_path, "bru_banana")
