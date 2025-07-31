{
  lib,
  buildPythonPackage,
  setuptools,
  pythonOlder,
  sqlglot,
  pytestCheckHook,
}:

buildPythonPackage {
  pname = "sffmt";
  version = builtins.head (builtins.match ".*__version__ = \"([^\"]+)\".*" (builtins.readFile ./sffmt.py));
  src = ./.;
  pyproject = true;

  disabled = pythonOlder "3.14";
  dependencies = [ sqlglot ];
  build-system = [ setuptools ];
  nativeCheckInputs = [ pytestCheckHook ];

  meta = with lib; {
    homepage = "https://github.com/padhia/sffmt";
    description = "Format SQL statements";
    maintainers = with maintainers; [
      padhia
    ];
  };
}
