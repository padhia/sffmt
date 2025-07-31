{
  lib,
  buildPythonPackage,
  setuptools,
  pythonOlder,
  sqlglot,
}:

buildPythonPackage {
  pname = "fmtsql";
  version = "0.1.0";
  src = ./.;
  pyproject = true;

  disabled = pythonOlder "3.12";
  dependencies = [ sqlglot ];
  build-system = [ setuptools ];

  meta = with lib; {
    homepage = "https://github.com/padhia/fmtsql";
    description = "Format SQL statements";
    maintainers = with maintainers; [
      padhia
    ];
  };
}
