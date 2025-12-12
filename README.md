# itzCode

A temperorary name for 1141 YZU CS321B Final Proj.

## Initial Setup

0. (Optional) Python Virtual Environment

    - [ ] Create `venv`

    ```powershell
    python -m venv .venv
    ```

    - [ ] Enter Virtual Env

        0. Windows

        ```powershell
        .\.venv\Scripts\activate
        ```

        1. Linux

        ```shell
        source .\.venv\bin\activate
        ```

## Usage

0. From `*.itz` to `*.cpp`

-   [ ] Using for demostrating specific file

    ```powershell
    python .\demo.py <specific features name>
    ```

-   [ ] Using for demostrating all features

    ```powershell
    python .\demo.py --all
    ```

1. From `*.cpp` to EXEC

    1-1. Windows

    ```powershell
    Get-ChildItem .\results\*.cpp | ForEach-Object { g++ -std=c++20 $_.FullName -o ("results\" + $_.BaseName + ".exe") }
    ```

    1-2. Linux / Mac

    ```shell
    for f in results/*.cpp; do g++ -std=c++20 "$f" -o "${f%.cpp}"; done
    ```

## TASKs

-   [x] Define variables
-   [x] Basic arithmetic
-   [x] Condition statements

    -   [x] if
    -   [x] else
    -   [x] then

-   [x] Loop statements

    -   [x] for
    -   [x] while

-   [x] Print
-   [x] Comments
-   [x] Simple Algorithms

    -   [x] max/min
    -   [x] max_elements/min_elements
    -   [x] sort

-   [x] Input
-   [ ] Functions

    -   [x] functions
    -   [ ] struct
    -   [ ] class

-   [ ] STL Containers

    -   [ ] vectors
    -   [ ] stack
    -   [ ] queue
    -   [ ] link-list

-   [x] File I/O

    -   [x] Read File
    -   [x] Write File
    -   [x] Append File

## Project Structure

The following tree illustrates the organization of the project and the purpose of each file.

````text
.
├── demo.py                  # Main Entry Point (Driver Script)
├── build.bat                # (Optional) Windows One-Click Build Script
├── examples/                # Source Code Examples (*.itz)
│   ├── algorithm.itz        # Algorithm implementation (Bubble Sort, Min/Max)
│   ├── comments.itz         # Comment handling tests
│   ├── expressions.itz      # Math operations & type inference tests
│   ├── file.itz             # File I/O tests (Read/Write/Append)
│   ├── function.itz         # Function & Recursion tests
│   ├── hello-world.itz      # Basic String Interpolation
│   ├── input.itz            # User Input (cin) tests
│   ├── logic.itz            # Logic gates & comparison tests
│   ├── loop.itz             # Loops (For/While) tests
│   └── random.itz           # Random number generation tests
├── src/                     # Compiler Core Modules
│   ├── token.py             # Definition of Language Tokens (Enums)
│   ├── lexer.py             # Lexical Analyzer (Raw Text -> Tokens)
│   ├── parser.py            # Syntax Parser (Tokens -> C++ Logic)
│   └── emitter.py           # Code Generator (Manages C++ output buffers)
└── results/                 # Build Artifacts (Generated .cpp & .exe)

## FAQ:

### 0. `-bash: /mnt/c/Users/<user>/.pyenv/pyenv-win/shims/python: cannot execute: required file not found`

> -   [x] Solution:
>
> ```powershell
> python3 <rest of the cli commands>
> ```
````
