# src/token.py
from enum import Enum

class TokenType(Enum):
    EOF = 'EOF'
    NEWLINE = 'NEWLINE'
    NUMBER = 'NUMBER'
    IDENTIFIER = 'ID'
    STRING = 'STRING'
    COMMENT = 'COMMENT'
    
    # Keywords
    ECHO = 'ECHO'        # Print to console
    DEF = 'DEF'          # Define a variable
    INPUT = 'INPUT'      # Input from user
    
    IF = 'IF'            # Conditional statement
    THEN = 'THEN'        # Part of IF statement
    ELSE = 'ELSE'        # Part of IF statement
    ENDIF = 'ENDIF'      # End of IF statement
    
    WHILE = 'WHILE'      # Start of a while loop
    REPEAT = 'REPEAT'    # Start of a loop
    ENDWHILE = 'ENDWHILE'# End of a loop
    
    FOR = 'FOR'          # Start of a for loop
    TO = 'TO'            # Part of FOR loop
    NEXT = 'NEXT'        # End of FOR loop
    STEP = 'STEP'        # Step in FOR loop
    
    RAND = 'RAND'        # Random number generation

    # Symbols
    LBRACKET = 'LBRACKET' # [
    RBRACKET = 'RBRACKET' # ]
    LPAREN = 'LPAREN'     # (
    RPAREN = 'RPAREN'     # )
    COMMA = 'COMMA'       # ,

    # Expression Operators
    EQ = 'EQ'                       # =
    PLUS = 'PLUS'                   # +
    MINUS = 'MINUS'                 # -
    ASTERISK = 'ASTERISK'           # *  
    SLASH = 'SLASH'                 # /
    DOUBLESLASH = 'DOUBLESLASH'     # //
    MOD = 'MOD'                     # %  
    
    # Comparison Operators
    EQEQ = 'EQEQ'         # ==
    NOTEQ = 'NOTEQ'       # !=
    LT = 'LT'             # <
    LTE = 'LTE'           # <=
    GT = 'GT'             # >
    GTE = 'GTE'           # >=
    
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