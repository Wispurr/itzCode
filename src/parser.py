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
        # 注意：我們不再需要 self.symbols 了！C++ auto 會幫我們處理一切
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
        
        self.emitter.headerLine("using namespace std;") # 方便使用 cout/cin
        # self.emitter.headerLine("#define fastio ios::sync_with_stdio(0), cin.tie(0), cout.tie(0)") # 加速器
        self.emitter.headerLine("#define endl '\\n'") # endl to '\n'
        
        self.emitter.headerLine("int main(void){")
        # self.emitter.headerLine("    fastio;")
        self.emitter.headerLine("    srand(time(NULL));")
        
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

        # 1. ECHO (升級版: 使用 cout)
        elif self.checkToken(TokenType.ECHO):
            self.match(TokenType.ECHO)
            if self.checkToken(TokenType.STRING):
                text = self.curToken.text
                
                # 使用 Regex 依據反引號 ` 切割字串
                # 範例: "Age: `age`, Score: `score`" -> ['Age: ', 'age', ', Score: ', 'score', '']
                parts = re.split(r'`(.*?)`', text)
                
                self.emitter.emit("    cout")
                for i, part in enumerate(parts):
                    if i % 2 == 0:
                        # 偶數部分是普通字串 (例如 "Age: ")
                        if part: # 如果不是空字串
                            self.emitter.emit(f' << "{part}"')
                    else:
                        # 奇數部分是變數 (例如 age)
                        self.emitter.emit(f" << {part}")
                
                self.emitter.emitLine(" << endl;")
                self.match(TokenType.STRING)
            else:
                # ECHO 運算式
                self.emitter.emit("    cout << (")
                self.expression()
                self.emitter.emitLine(") << endl;")

        # 2. DEF (升級版: 使用 auto)
        elif self.checkToken(TokenType.DEF):
            self.match(TokenType.DEF)
            name = self.curToken.text
            self.match(TokenType.IDENTIFIER)
            self.match(TokenType.EQ)
            
            if self.checkToken(TokenType.STRING):
                val = self.curToken.text
                self.match(TokenType.STRING)
                # 字串改用 std::string，比 char* 更安全且好用
                self.emitter.emitLine(f'    string {name} = "{val}";')
            
            elif self.checkToken(TokenType.LBRACKET):
                # 陣列還是維持 double 以支援運算，或者你可以用 auto 但 C++ 陣列初始化語法較嚴格
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
                # [神技] 直接用 auto，讓 C++ 決定是 int 還是 double
                self.emitter.emit(f"    auto {name} = ")
                self.expression()
                self.emitter.emitLine(";")

        # 3. INPUT (升級版: 使用 cin)
        elif self.checkToken(TokenType.INPUT):
            self.match(TokenType.INPUT)
            name = self.curToken.text
            self.match(TokenType.IDENTIFIER)
            # cin 自動識別型別，不需要 %d 或 %s
            self.emitter.emitLine(f"    cin >> {name};")

        # 4. IF
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

        # 5. WHILE
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

        # 6. FOR
        elif self.checkToken(TokenType.FOR):
            self.match(TokenType.FOR)
            loop_var = self.curToken.text
            self.match(TokenType.IDENTIFIER)
            self.match(TokenType.EQ)
            # 這裡也可以用 auto
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

        # 7. 賦值
        elif self.checkToken(TokenType.IDENTIFIER):
            name = self.curToken.text
            self.match(TokenType.IDENTIFIER)
            
            if self.checkToken(TokenType.LBRACKET):
                self.match(TokenType.LBRACKET)
                self.emitter.emit(f"    {name}[(int)(")
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
        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH) or \
              self.checkToken(TokenType.MOD) or self.checkToken(TokenType.DOUBLESLASH):
            
            if self.checkToken(TokenType.MOD):
                self.nextToken()
                # 使用 auto 後，我們可以大膽地讓運算式保持原樣
                # 但為了保險，如果是浮點數取餘數，C++ 還是會報錯
                # 這裡最簡單的做法還是強制轉型，或者我們相信使用者會用整數
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
        
        elif self.checkToken(TokenType.LPAREN):
            self.match(TokenType.LPAREN)
            self.emitter.emit("(")
            self.expression()
            self.emitter.emit(")")
            self.match(TokenType.RPAREN)

        else:
            sys.exit(f"[Parsing Error] Unexpected token in expression: {self.curToken.kind}")