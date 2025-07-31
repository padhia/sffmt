{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { nixpkgs, flake-utils, ... }:
  let
    overlays.default = final: prev: {
      pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
        (py-final: py-prev: {
          fmtsql = py-final.callPackage ./fmtsql.nix {};
        })
      ];

      fmtsql = final.python3Packages.fmtsql;
    };

    eachSystem = system:
    let
      pkgs = import nixpkgs {
        inherit system;
        overlays = [ overlays.default ];
      };

    in {
      devShells.default = pkgs.mkShell {
        name = "fmtsql";
        venvDir = "./.venv";
        buildInputs = with pkgs.python3Packages; [
          pkgs.ruff
          pkgs.uv
          python
          venvShellHook
          sqlglot
        ];
      };

      packages.default = pkgs.fmtsql;
    };

  in {
    inherit overlays;
    inherit (flake-utils.lib.eachDefaultSystem eachSystem) devShells packages;
  };
}
