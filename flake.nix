{
  description = "Storytime: Python FastAPI backend + Node/TypeScript frontend";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    poetry.url = "github:nix-community/poetry2nix";
  };

  outputs = { self, nixpkgs, flake-utils, poetry, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python311;
        pythonPackages = python.withPackages (ps: [
          ps.fastapi
          ps.uvicorn
          ps.httpx
          ps.python-dotenv
        ]);
      in {
        devShells.default = pkgs.mkShell {
          name = "storytime-dev-shell";
          buildInputs = [
            pythonPackages
            pkgs.nodejs_20
            pkgs.nodePackages.npm
          ];
          shellHook = ''
            export PYTHONPATH=$PWD/backend
            export PATH=$PWD/frontend/node_modules/.bin:$PATH
          '';
        };
      }
    );
} 