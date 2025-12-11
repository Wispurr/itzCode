# src/parser.py
import sys
import re
from src.token import TokenType

class Parser:
    def __init__(self, lexer, emitter):
        self.lexer = lexer
        self.emitter = emitter
        self.curToken = None
        self.peekToken = None
        self.nextToken()
        self.nextToken()

    def checkToken(self, kind):
        return kind == self.curToken.kind

    def match(self, kind):
        if not self.checkToken(kind):
            sys.exit(f"[Parsing Error] Expected {kind}, got {self.curToken.kind}")
        self.nextToken()

    def nextToken(self):
        self.curToken = self.peekToken
        self.peekToken = self.lexer.getToken()

    def program(self):
        # 1. 寫入 Headers
        self.emitter.headerLine("#include <iostream>")
        self.emitter.headerLine("#include <fstream>")
        self.emitter.headerLine("#include <string>")
        self.emitter.headerLine("#include <vector>")
        self.emitter.headerLine("#include <cstdlib>")
        self.emitter.headerLine("#include <ctime>")
        self.emitter.headerLine("#include <cmath>")
        self.emitter.headerLine("using namespace std;")
        
        # 2. 預寫 Main 的開頭到緩衝區
        # 注意：這裡我們手動操作 emitter，因為 main 的內容要在最後才組合
        self.emitter.main += "int main(void){\n"
        self.emitter.main += "    srand(time(NULL));\n"

        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        while not self.checkToken(TokenType.EOF):
            if self.checkToken(TokenType.FUNC):
                self.emitter.setCaptureMode("functions") # 切換到函式緩衝區
                self.func_def()
                self.emitter.setCaptureMode("main")      # 切換回主程式
            else:
                self.statement()

        self.emitter.main += "    return 0;\n"
        self.emitter.main += "}\n"

    def func_def(self):
        self.match(TokenType.FUNC)
        func_name = self.curToken.text
        self.match(TokenType.IDENTIFIER)
        
        # 解析參數: FUNC fib n -> auto fib(auto n)
        params = []
        while not self.checkToken(TokenType.NEWLINE):
            if self.checkToken(TokenType.IDENTIFIER):
                params.append(f"auto {self.curToken.text}")
                self.nextToken()
            else:
                break
        
        params_str = ", ".join(params)
        # C++14 支援 auto 回傳型態推導 (Recursive auto 需要 C++14 以上)
        self.emitter.emitLine(f"auto {func_name}({params_str}) {{")
        
        self.nl()
        
        while not self.checkToken(TokenType.ENDFUNC):
            self.statement()
        
        self.match(TokenType.ENDFUNC)
        self.emitter.emitLine("}")
        self.nl()

    def statement(self):
        if self.checkToken(TokenType.COMMENT):
            self.emitter.emitLine("    " + self.curToken.text)
            self.nextToken()

        elif self.checkToken(TokenType.ECHO):
            self.match(TokenType.ECHO)
            if self.checkToken(TokenType.STRING):
                text = self.curToken.text
                parts = re.split(r'`(.*?)`', text)
                self.emitter.emit("    cout")
                for i, part in enumerate(parts):
                    if i % 2 == 0:
                        if part: self.emitter.emit(f' << "{part}"')
                    else:
                        self.emitter.emit(f" << {part}")
                self.emitter.emitLine(" << endl;")
                self.match(TokenType.STRING)
            else:
                self.emitter.emit("    cout << (")
                self.expression()
                self.emitter.emitLine(") << endl;")

        elif self.checkToken(TokenType.DEF):
            self.match(TokenType.DEF)
            name = self.curToken.text
            self.match(TokenType.IDENTIFIER)
            self.match(TokenType.EQ)
            
            if self.checkToken(TokenType.STRING):
                val = self.curToken.text
                self.match(TokenType.STRING)
                self.emitter.emitLine(f'    string {name} = "{val}";')
            elif self.checkToken(TokenType.LBRACKET):
                self.match(TokenType.LBRACKET)
                self.emitter.emit(f"    double {name}[] = {{")
                self.expression()
                while self.checkToken(TokenType.COMMA):
                    self.emitter.emit(", ")
                    self.match(TokenType.COMMA)
                    self.expression()
                self.match(TokenType.RBRACKET)
                self.emitter.emitLine("};")
            else:
                self.emitter.emit(f"    auto {name} = ")
                self.expression()
                self.emitter.emitLine(";")

        elif self.checkToken(TokenType.RETURN):
            self.match(TokenType.RETURN)
            self.emitter.emit("    return ")
            self.expression()
            self.emitter.emitLine(";")

        elif self.checkToken(TokenType.INPUT):
            self.match(TokenType.INPUT)
            name = self.curToken.text
            self.match(TokenType.IDENTIFIER)
            self.emitter.emitLine(f"    cin >> {name};")

        elif self.checkToken(TokenType.IF):
            self.match(TokenType.IF)
            self.emitter.emit("    if(")
            self.comparison()
            
            # 支援 Optional THEN (為了你的 function.itz 語法)
            if self.checkToken(TokenType.THEN):
                self.match(TokenType.THEN)
            
            self.nl()
            self.emitter.emitLine("){")
            
            while not self.checkToken(TokenType.ENDIF) and not self.checkToken(TokenType.ELSE):
                self.statement()
            
            # 處理 ELSE 或 ELSE IF
            if self.checkToken(TokenType.ELSE):
                self.match(TokenType.ELSE)
                
                # 檢查是否為 ELSE IF
                if self.checkToken(TokenType.IF):
                    self.match(TokenType.IF)
                    self.emitter.emit("    } else if (")
                    self.comparison()
                    if self.checkToken(TokenType.THEN):
                        self.match(TokenType.THEN)
                    self.nl()
                    self.emitter.emitLine(") {")
                    # 遞迴呼叫 statement 直到 ENDIF
                    while not self.checkToken(TokenType.ENDIF) and not self.checkToken(TokenType.ELSE):
                        self.statement()
                    # 若還有 ELSE (針對 ELSE IF 後面的 ELSE)
                    if self.checkToken(TokenType.ELSE):
                        self.match(TokenType.ELSE)
                        self.nl()
                        self.emitter.emitLine("    } else {")
                        while not self.checkToken(TokenType.ENDIF):
                            self.statement()
                else:
                    self.nl()
                    self.emitter.emitLine("    } else {")
                    while not self.checkToken(TokenType.ENDIF):
                        self.statement()
            
            self.match(TokenType.ENDIF)
            self.emitter.emitLine("    }")

        elif self.checkToken(TokenType.WHILE):
            self.match(TokenType.WHILE)
            self.emitter.emit("    while(")
            self.comparison()
            self.match(TokenType.REPEAT)
            self.nl()
            self.emitter.emitLine("){")
            while not self.checkToken(TokenType.ENDWHILE):
                self.statement()
            self.match(TokenType.ENDWHILE)
            self.emitter.emitLine("    }")

        elif self.checkToken(TokenType.FOR):
            self.match(TokenType.FOR)
            loop_var = self.curToken.text
            self.match(TokenType.IDENTIFIER)
            self.match(TokenType.EQ)
            self.emitter.emit(f"    for(auto {loop_var} = ")
            self.expression()
            self.emitter.emit(f"; {loop_var} <= ")
            self.match(TokenType.TO)
            self.expression()
            self.emitter.emit(f"; {loop_var}++) {{")
            self.nl()
            while not self.checkToken(TokenType.NEXT):
                self.statement()
            self.match(TokenType.NEXT)
            self.emitter.emitLine("    }")

        elif self.checkToken(TokenType.IDENTIFIER):
            name = self.curToken.text
            self.match(TokenType.IDENTIFIER)
            
            # 這裡要注意：如果是函式呼叫單獨一行 func(x)，會被這裡捕獲
            # 判斷是賦值 (=) 還是函式呼叫 (()
            if self.checkToken(TokenType.EQ):
                self.match(TokenType.EQ)
                self.emitter.emit(f"    {name} = ")
                self.expression()
                self.emitter.emitLine(";")
            elif self.checkToken(TokenType.LBRACKET):
                self.match(TokenType.LBRACKET)
                self.emitter.emit(f"    {name}[(int)(")
                self.expression()
                self.emitter.emit(")]")
                self.match(TokenType.RBRACKET)
                self.match(TokenType.EQ)
                self.emitter.emit(" = ")
                self.expression()
                self.emitter.emitLine(";")
            elif self.checkToken(TokenType.LPAREN):
                # 獨立的函式呼叫 fib(n)
                self.match(TokenType.LPAREN)
                self.emitter.emit(f"    {name}(")
                if not self.checkToken(TokenType.RPAREN):
                    self.expression()
                    while self.checkToken(TokenType.COMMA):
                        self.emitter.emit(", ")
                        self.match(TokenType.COMMA)
                        self.expression()
                self.match(TokenType.RPAREN)
                self.emitter.emitLine(");")
            else:
                 sys.exit(f"[Error] Unexpected identifier usage: {name}")
                 
        elif self.checkToken(TokenType.FWRITE):
            self.match(TokenType.FWRITE)
            
            # 1. 解析檔名 (可以是字串或變數)
            fileName = ""
            if self.checkToken(TokenType.STRING):
                fileName = f'"{self.curToken.text}"'
                self.nextToken()
            else:
                fileName = self.curToken.text
                self.match(TokenType.IDENTIFIER)
            
            self.match(TokenType.COMMA)
            
            # 2. 生成 C++ 寫入區塊
            # 使用 { } 限制作用域，避免多個 FWRITE 導致變數 f 重複定義
            self.emitter.emitLine("    {")
            self.emitter.emitLine(f'        ofstream f({fileName});')
            self.emitter.emit("        f << ")
            self.expression() # 寫入內容 (支援變數或字串)
            self.emitter.emitLine(";")
            self.emitter.emitLine("        f.close();")
            self.emitter.emitLine("    }")

        # 語法: FAPPEND filename, content
        elif self.checkToken(TokenType.FAPPEND):
            self.match(TokenType.FAPPEND)
            
            fileName = ""
            if self.checkToken(TokenType.STRING):
                fileName = f'"{self.curToken.text}"'
                self.nextToken()
            else:
                fileName = self.curToken.text
                self.match(TokenType.IDENTIFIER)
            
            self.match(TokenType.COMMA)
            
            self.emitter.emitLine("    {")
            self.emitter.emitLine(f'        ofstream f({fileName}, ios::app);') # ios::app 是追加模式
            self.emitter.emit("        f << ")
            self.expression()
            self.emitter.emitLine(";")
            self.emitter.emitLine("        f.close();")
            self.emitter.emitLine("    }")

        # 語法: FREAD filename, varName
        elif self.checkToken(TokenType.FREAD):
            self.match(TokenType.FREAD)
            
            fileName = ""
            if self.checkToken(TokenType.STRING):
                fileName = f'"{self.curToken.text}"'
                self.nextToken()
            else:
                fileName = self.curToken.text
                self.match(TokenType.IDENTIFIER)
            
            self.match(TokenType.COMMA)
            
            # 取得要存入的變數名稱
            varName = self.curToken.text
            self.match(TokenType.IDENTIFIER)
            
            # 生成 C++ 讀取邏輯 (一次讀取整個檔案)
            self.emitter.emitLine("    {")
            self.emitter.emitLine(f'        ifstream f({fileName});')
            self.emitter.emitLine("        if(f) {")
            self.emitter.emitLine(f'            {varName}.assign((istreambuf_iterator<char>(f)), (istreambuf_iterator<char>()));')
            self.emitter.emitLine("        }")
            self.emitter.emitLine("        f.close();")
            self.emitter.emitLine("    }")
            

        else:
            sys.exit(f"[Parsing Error] Unexpected token at start of statement: {self.curToken.kind} ({self.curToken.text})")

        self.nl()

    def nl(self):
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

    def comparison(self):
        self.expression()
        if self.isComparisonOperator():
            # [特殊處理] 如果是單等號 =，在 C++ 比較中要轉成 ==
            if self.checkToken(TokenType.EQ):
                self.emitter.emit("==")
                self.nextToken()
            else:
                self.emitter.emit(self.curToken.text)
                self.nextToken()
            self.expression()

    def isComparisonOperator(self):
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTE) or \
               self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTE) or \
               self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ) or \
               self.checkToken(TokenType.EQ)  # <--- [新增] 讓單等號也能當比較運算符

    def expression(self):
        self.term()
        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.term()

    def term(self):
        self.unary()
        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH) or \
              self.checkToken(TokenType.MOD) or self.checkToken(TokenType.DOUBLESLASH):
            if self.checkToken(TokenType.MOD):
                self.nextToken()
                self.emitter.emit(" % (int) ") 
            elif self.checkToken(TokenType.DOUBLESLASH):
                self.nextToken()
                self.emitter.emit(" / ")
            else:
                self.emitter.emit(self.curToken.text)
                self.nextToken()
            self.unary()

    def unary(self):
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()        
        self.primary()

    def primary(self):
        if self.checkToken(TokenType.NUMBER):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        
        elif self.checkToken(TokenType.IDENTIFIER):
            name = self.curToken.text
            self.match(TokenType.IDENTIFIER)
            
            # 函式呼叫 fib(n)
            if self.checkToken(TokenType.LPAREN):
                self.match(TokenType.LPAREN)
                self.emitter.emit(f"{name}(")
                if not self.checkToken(TokenType.RPAREN):
                    self.expression()
                    while self.checkToken(TokenType.COMMA):
                        self.emitter.emit(", ")
                        self.match(TokenType.COMMA)
                        self.expression()
                self.match(TokenType.RPAREN)
                self.emitter.emit(")")
            
            # 陣列存取 arr[i]
            elif self.checkToken(TokenType.LBRACKET):
                self.match(TokenType.LBRACKET)
                self.emitter.emit(f"{name}[(int)(")
                self.expression()
                self.emitter.emit(")]")
                self.match(TokenType.RBRACKET)
            else:
                self.emitter.emit(name)

        # [新增] 支援字串表達式
        elif self.checkToken(TokenType.STRING):
            # 因為 Lexer 已經去掉了前後引號，我們產生 C++ 程式碼時要補回去
            self.emitter.emit(f'"{self.curToken.text}"') 
            self.nextToken()
        
        elif self.checkToken(TokenType.RAND):
            self.match(TokenType.RAND)
            self.emitter.emit("rand()")
        
        elif self.checkToken(TokenType.LPAREN):
            self.match(TokenType.LPAREN)
            self.emitter.emit("(")
            self.expression()
            self.emitter.emit(")")
            self.match(TokenType.RPAREN)

        else:
            sys.exit(f"[Parsing Error] Unexpected token in expression: {self.curToken.kind}")