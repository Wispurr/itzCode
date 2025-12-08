# src/token.py
from enum import Enum

class TokenType(Enum):
    EOF = 'EOF'
    NEWLINE = 'NEWLINE'
    NUMBER = 'NUMBER'
    IDENTIFIER = 'ID'
    STRING = 'STRING'
    COMMENT = 'COMMENT'
    
    # 關鍵字
    ECHO = 'ECHO'
    DEF = 'DEF'
    IF = 'IF'
    THEN = 'THEN'
    ELSE = 'ELSE'
    ENDIF = 'ENDIF'
    WHILE = 'WHILE'
    REPEAT = 'REPEAT'
    ENDWHILE = 'ENDWHILE'
    FOR = 'FOR'
    TO = 'TO'
    NEXT = 'NEXT'
    STEP = 'STEP'
    RAND = 'RAND'

    # 符號
    LBRACKET = 'LBRACKET' # [
    RBRACKET = 'RBRACKET' # ]
    LPAREN = 'LPAREN'     # (
    RPAREN = 'RPAREN'     # )
    COMMA = 'COMMA'       # ,

    # 運算
    EQ = 'EQ' 
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    ASTERISK = 'ASTERISK'
    SLASH = 'SLASH'
    MOD = 'MOD'
    
    # 比較
    EQEQ = 'EQEQ'
    NOTEQ = 'NOTEQ'
    LT = 'LT'
    LTE = 'LTE'
    GT = 'GT'
    GTE = 'GTE'
    
class Token:
    def __init__(self, token_text, token_kind):
        self.text = token_text
        self.kind = token_kind

    @staticmethod
    def check_if_keyword(token_text):
        for kind in TokenType:
            # 確保完全匹配且是關鍵字 (排除運算符號)
            if kind.name == token_text and 1 < len(token_text) and token_text.isalpha():
                return kind
        return None