# src/lexer.py
import sys
from src.token import Token, TokenType

class Lexer:
    def __init__(self, source):
        self.source = source + '\n'
        self.curChar = ''
        self.curPos = -1
        self.nextChar()

    def nextChar(self):
        self.curPos += 1
        if self.curPos >= len(self.source):
            self.curChar = '\0'
        else:
            self.curChar = self.source[self.curPos]

    def peek(self):
        if self.curPos + 1 >= len(self.source):
            return '\0'
        return self.source[self.curPos+1]

    def abort(self, message):
        sys.exit(f"[Lexing Error] {message}")

    def skipWhitespace(self):
        while self.curChar in [' ', '\t', '\r']:
            self.nextChar()

    def getToken(self):
        self.skipWhitespace()
        
        token = None

        if self.curChar == '\n':
            token = Token('\n', TokenType.NEWLINE)
            self.nextChar()
        
        elif self.curChar == '\0':
            token = Token('', TokenType.EOF)

        # --- 1. 處理註解 (只支援 #) ---
        elif self.curChar == '#':
            self.nextChar() # 跳過 #
            startPos = self.curPos
            while self.curChar != '\n' and self.curChar != '\0':
                self.nextChar()
            text = self.source[startPos : self.curPos]
            # 轉成 C 語言註解格式
            token = Token(f"//{text}", TokenType.COMMENT)

        # --- 2. 處理字串 ---
        elif self.curChar == '"':
            self.nextChar()
            startPos = self.curPos
            while self.curChar != '"':
                if self.curChar in ['\r', '\n', '\\', '%']: pass
                self.nextChar()
            tokenText = self.source[startPos : self.curPos]
            token = Token(tokenText, TokenType.STRING)
            self.nextChar()

        # --- 3. 處理變數 (反引號) ---
        elif self.curChar == '`':
            self.nextChar()
            startPos = self.curPos
            while self.curChar != '`':
                self.nextChar()
            tokenText = self.source[startPos : self.curPos]
            token = Token(tokenText, TokenType.IDENTIFIER)
            self.nextChar()

        # --- 4. 處理數字 ---
        elif self.curChar.isdigit():
            startPos = self.curPos
            while self.peek().isdigit():
                self.nextChar()
            if self.peek() == '.':
                self.nextChar()
                while self.peek().isdigit():
                    self.nextChar()
            tokenText = self.source[startPos : self.curPos + 1]
            token = Token(tokenText, TokenType.NUMBER)
            self.nextChar()

        # --- 5. 處理關鍵字與識別字 ---
        elif self.curChar.isalpha():
            startPos = self.curPos
            while self.peek().isalnum() or self.peek() == '_':
                self.nextChar()
            tokenText = self.source[startPos : self.curPos + 1]
            keyword = Token.check_if_keyword(tokenText)
            
            if keyword is None:
                token = Token(tokenText, TokenType.IDENTIFIER)
            else:
                token = Token(tokenText, keyword)
            self.nextChar()

        # --- 6. 處理運算符號 (包含 // 與 /) ---
        elif self.curChar == '/':
            if self.peek() == '/':
                # 這是運算符 // (整數除法)，不再是註解！
                self.nextChar()
                self.nextChar()
                token = Token('//', TokenType.DOUBLESLASH)
            else:
                # 這是運算符 /
                token = Token('/', TokenType.SLASH)
                self.nextChar()
                
        elif self.curChar == '+':
            token = Token(self.curChar, TokenType.PLUS)
            self.nextChar()
        elif self.curChar == '-':
            token = Token(self.curChar, TokenType.MINUS)
            self.nextChar()
        elif self.curChar == '*':
            token = Token(self.curChar, TokenType.ASTERISK)
            self.nextChar()
        elif self.curChar == '%':
            token = Token(self.curChar, TokenType.MOD)
            self.nextChar()

        # --- 7. 其他符號 ---
        elif self.curChar == '[':
            token = Token('[', TokenType.LBRACKET)
            self.nextChar()
        elif self.curChar == ']':
            token = Token(']', TokenType.RBRACKET)
            self.nextChar()
        elif self.curChar == ',':
            token = Token(',', TokenType.COMMA)
            self.nextChar()
        elif self.curChar == '(':
            token = Token('(', TokenType.LPAREN)
            self.nextChar()
        elif self.curChar == ')':
            token = Token(')', TokenType.RPAREN)
            self.nextChar()
        
        elif self.curChar == '=':
            if self.peek() == '=':
                self.nextChar()
                token = Token('==', TokenType.EQEQ)
            else:
                token = Token('=', TokenType.EQ)
            self.nextChar()
        elif self.curChar == '>':
            if self.peek() == '=':
                self.nextChar()
                token = Token('>=', TokenType.GTE)
            else:
                token = Token('>', TokenType.GT)
            self.nextChar()
        elif self.curChar == '<':
            if self.peek() == '=':
                self.nextChar()
                token = Token('<=', TokenType.LTE)
            elif self.peek() == '>':
                self.nextChar()
                token = Token('<>', TokenType.NOTEQ)
            else:
                token = Token('<', TokenType.LT)
            self.nextChar()
        elif self.curChar == '!':
            if self.peek() == '=':
                self.nextChar()
                token = Token('!=', TokenType.NOTEQ)
                self.nextChar()
            else:
                self.abort("Expected !=, got !" + self.peek())

        else:
            self.abort("Unknown token: " + self.curChar)

        return token