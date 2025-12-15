import os
import sys
import subprocess
import platform
from src.lexer import Lexer
from src.parser import Parser
from src.emitter import Emitter

def cpp2exec(cpp_filename):
    """
    將 results/{cpp_filename} (e.g., hello.cpp) 編譯成執行檔
    """
    # 設定路徑
    cpp_path = os.path.join("results", cpp_filename)
    base_name = os.path.splitext(cpp_filename)[0]
    
    # 判斷作業系統決定副檔名
    exe_ext = ".exe" if platform.system() == "Windows" else ""
    exec_path = os.path.join("results", f"{base_name}{exe_ext}")

    print(f"  [Building] C++ -> Executable ({exec_path})...")

    # 編譯指令: g++ -std=c++20 input.cpp -o output.exe
    cmd = ["g++", "-std=c++20", cpp_path, "-o", exec_path]

    try:
        subprocess.run(cmd, check=True)
        print("  [Success] Executable created.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  [Error] GCC Compilation failed: {e}")
        return False
    except FileNotFoundError:
        print("  [Error] g++ not found. Please install MinGW (Windows) or GCC (Linux).")
        return False

def compile_file(filename):
    """
    讀取 examples/{filename}，編譯並輸出到 results/{filename}.cpp
    然後呼叫 g++ 轉為執行檔
    """
    input_path = os.path.join("examples", filename)
    
    # 建立 results 資料夾 (如果不存在)
    output_dir = "results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 決定輸出檔名: hello.itz -> results/hello.cpp
    base_name = os.path.splitext(filename)[0]
    output_filename = f"{base_name}.cpp"
    output_path = os.path.join(output_dir, output_filename)

    print(f"Compiling: {filename} -> {output_path}")

    # 1. 讀取檔案
    try:
        with open(input_path, "r", encoding='utf-8') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"  [Error] File '{input_path}' not found.")
        return False

    # 2. 初始化編譯器模組
    lexer = Lexer(source_code)
    emitter = Emitter(output_path)
    parser = Parser(lexer, emitter)

    # 3. 執行轉譯 (itz -> cpp)
    try:
        parser.program()
        emitter.writeFile()
        print("  [Transpilation Success]")
        
        # 4. 執行編譯 (cpp -> exe)
        # 這裡直接呼叫 cpp2exec
        if cpp2exec(output_filename):
            return True
        else:
            return False

    except Exception as e:
        print(f"  [Error] {e}")
        return False

def run_all_demos():
    """
    批次編譯 ./examples 資料夾下所有的 .itz 檔案
    """
    print("=== Batch Compiling All Examples ===")
    if not os.path.exists("examples"):
        print("Error: ./examples directory not found.")
        return

    files = [f for f in os.listdir("examples") if f.endswith(".itz")]
    if not files:
        print("No .itz files found in ./examples")
        return

    success_count = 0
    for file in files:
        if compile_file(file):
            success_count += 1
        print("-" * 30)
    
    print(f"Batch completed: {success_count}/{len(files)} files compiled successfully.")

def main():
    print("--- itzCode Tiny Compiler Driver ---")

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Compile one file:  python demo.py <filename.itz>")
        print("  Compile all files: python demo.py --all")
        return

    arg = sys.argv[1]

    if arg == "--all":
        run_all_demos()
    else:
        # 編譯單一檔案
        compile_file(arg)

if __name__ == "__main__":
    main()