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
    Get-ChildItem .\results\*.cpp | ForEach-Object { gcc $_.FullName -o ("results\" + $_.BaseName + ".exe") }
    ```

    1-2. Linux / Mac

    ```shell
    for f in results/*.cpp; do g++ "$f" -o "${f%.c}"; done
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
-   [ ] Functions
    -   [ ] functions
    -   [ ] struct
    -   [ ] class
-   [ ] STL Containers
    -   [ ] vectors
    -   [ ] stack
    -   [ ] queue
    -   [ ] link-list

## FAQ:

### 0. `-bash: /mnt/c/Users/<user>/.pyenv/pyenv-win/shims/python: cannot execute: required file not found`

> -   [x] Solution:
>
> ```powershell
> python3 <rest of the cli commands>
> ```
