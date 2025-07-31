{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { nixpkgs, flake-utils, ... }:
  let
    overlays.default = final: prev: {
      pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
        (py-final: py-prev: {
          sffmt = py-final.callPackage ./sffmt.nix {};
        })
      ];

      sffmt = final.python3Packages.sffmt;
    };

    eachSystem = system:
    let
      pkgs = import nixpkgs {
        inherit system;
        overlays = [ overlays.default ];
      };

    in {
      devShells.default = pkgs.mkShell {
        name = "sffmt";
        venvDir = "./.venv";
        buildInputs = with pkgs.python3Packages; [
          pkgs.ruff
          pkgs.uv
          python
          venvShellHook
          setuptools
          sqlglot
          pytest
        ];
        postVenvCreation = ''
          printf '%s\n' ''${PYTHONPATH//:/$'\n'} > "$(python -c 'import site; print(site.getsitepackages()[0])')/nix-deps.pth"
          pip install --no-build-isolation --no-deps -e .
        '';
      };

      packages.default = pkgs.sffmt;
    };

  in {
    inherit overlays;
    inherit (flake-utils.lib.eachDefaultSystem eachSystem) devShells packages;
  };
}
