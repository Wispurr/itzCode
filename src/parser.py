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
        self.emitter.headerLine("#include <bits/stdc++.h>")
        self.emitter.headerLine("int main(void){")
        self.emitter.headerLine("   srand(time(NULL));")
        
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        while not self.checkToken(TokenType.EOF):
            self.statement()

        self.emitter.emitLine("    return 0;")
        self.emitter.emitLine("}")

    def statement(self):
        # 0. 註解
        if self.checkToken(TokenType.COMMENT):
            self.emitter.emitLine("    " + self.curToken.text)
            self.nextToken()

        # 1. ECHO
        elif self.checkToken(TokenType.ECHO):
            self.match(TokenType.ECHO)
            if self.checkToken(TokenType.STRING):
                text = self.curToken.text
                c_fmt = text
                vars_list = []
                matches = re.findall(r'`(.*?)`', text)
                for v in matches:
                    c_fmt = c_fmt.replace(f'`{v}`', '%g') # %g 自動適配 double
                    vars_list.append(v)
                
                args = ""
                if len(vars_list) > 0:
                    args = ", " + ", ".join(vars_list)
                
                self.emitter.emitLine(f'    printf("{c_fmt}\\n"{args});')
                self.match(TokenType.STRING)
            else:
                # 支援 ECHO 運算式
                self.emitter.emit("    printf(\"%.2f\\n\", (double)(")
                self.expression()
                self.emitter.emitLine("));")

        # 2. DEF (變數與陣列定義)
        elif self.checkToken(TokenType.DEF):
            self.match(TokenType.DEF)
            name = self.curToken.text
            self.match(TokenType.IDENTIFIER)
            self.match(TokenType.EQ)
            
            if self.checkToken(TokenType.STRING):
                val = self.curToken.text
                self.match(TokenType.STRING)
                self.emitter.emitLine(f'    char* {name} = "{val}";')
            elif self.checkToken(TokenType.LBRACKET):
                # --- 陣列定義: DEF arr = [1, 2, 3] ---
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
                # --- 一般數字變數 (改用 double) ---
                self.emitter.emit(f"    double {name} = ")
                self.expression()
                self.emitter.emitLine(";")

        # 3. IF
        elif self.checkToken(TokenType.IF):
            self.match(TokenType.IF)
            self.emitter.emit("    if(")
            self.comparison()
            self.match(TokenType.THEN)
            self.nl()
            self.emitter.emitLine("){")
            while not self.checkToken(TokenType.ENDIF) and not self.checkToken(TokenType.ELSE):
                self.statement()
            if self.checkToken(TokenType.ELSE):
                self.match(TokenType.ELSE)
                self.nl()
                self.emitter.emitLine("    } else {")
                while not self.checkToken(TokenType.ENDIF):
                    self.statement()
            self.match(TokenType.ENDIF)
            self.emitter.emitLine("    }")

        # 4. WHILE
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

        # 5. FOR
        elif self.checkToken(TokenType.FOR):
            self.match(TokenType.FOR)
            loop_var = self.curToken.text
            self.match(TokenType.IDENTIFIER)
            self.match(TokenType.EQ)
            self.emitter.emit(f"    for(double {loop_var} = ")
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

        # 6. 賦值 (Assignment)
        elif self.checkToken(TokenType.IDENTIFIER):
            name = self.curToken.text
            self.match(TokenType.IDENTIFIER)
            
            # 判斷是變數賦值還是陣列賦值
            if self.checkToken(TokenType.LBRACKET):
                # arr[i] = val
                self.match(TokenType.LBRACKET)
                self.emitter.emit(f"    {name}[(int)(") # C語言陣列索引需為 int
                self.expression()
                self.emitter.emit(")]")
                self.match(TokenType.RBRACKET)
            else:
                self.emitter.emit(f"    {name}")

            self.match(TokenType.EQ)
            self.emitter.emit(" = ")
            self.expression()
            self.emitter.emitLine(";")

        self.nl()

    def nl(self):
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

    def comparison(self):
        self.expression()
        if self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()

    def isComparisonOperator(self):
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTE) or \
               self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTE) or \
               self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ)

    def expression(self):
        self.term()
        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.term()

    def term(self):
        self.unary()
        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH) or self.checkToken(TokenType.MOD):
            
            if self.checkToken(TokenType.MOD):
                self.nextToken()
                self.emitter.emit(" % (int) ") 
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
            # 陣列存取 arr[i]
            if self.checkToken(TokenType.LBRACKET):
                self.match(TokenType.LBRACKET)
                self.emitter.emit(f"{name}[(int)(")
                self.expression()
                self.emitter.emit(")]")
                self.match(TokenType.RBRACKET)
            else:
                self.emitter.emit(name)
        
        elif self.checkToken(TokenType.RAND):
            self.match(TokenType.RAND)
            self.emitter.emit("rand()")
        
        # --- 新增: 處理括號 (Expression) ---
        elif self.checkToken(TokenType.LPAREN):
            self.match(TokenType.LPAREN)
            self.emitter.emit("(") # 將左括號寫入 C
            self.expression()      # 遞迴處理內部的表達式
            self.emitter.emit(")") # 將右括號寫入 C
            self.match(TokenType.RPAREN)

        else:
            sys.exit(f"[Parsing Error] Unexpected token in expression: {self.curToken.kind}")