import re
symTab = [];
valTab = [];
catTab = [];
class Token(object):
	def __init__(self, type, val, pos):
		self.type = type
		self.val = val
		self.pos = pos

	def __str__(self):
		return '%s\t \"%s\" at %s' % (self.type, self.val, self.pos)


class LexerError(Exception):
	def __init__(self, pos):
		self.pos = pos
class Lexer(object):
	def __init__(self, rules, skip_whitespace=True):
		idx = 1
		regex_parts = []
		self.group_type = {}

		for regex, type in rules:
			groupname = 'GROUP%s' % idx
			regex_parts.append('(?P<%s>%s)' % (groupname, regex))
			self.group_type[groupname] = type
			idx += 1

		self.regex = re.compile('|'.join(regex_parts))
		self.skip_whitespace = skip_whitespace
		self.re_ws_skip = re.compile('\S')


	def input(self, buf):
		self.buf = buf
		self.pos = 0

	def token(self):
		if self.pos >= len(self.buf):
			return None
		else:
			if self.skip_whitespace:
				m = self.re_ws_skip.search(self.buf, self.pos)

				if m:
					self.pos = m.start()
				else:
					return None

			m = self.regex.match(self.buf, self.pos)
			if m:
				groupname = m.lastgroup
				tok_type = self.group_type[groupname]
				tok = Token(tok_type, m.group(groupname), self.pos)
				self.pos = m.end()
				return tok

			# if we're here, no rule matched
			raise LexerError(self.pos)

	def tokens(self):
		while 1:
			tok = self.token()
			if tok is None: break
			yield tok
parse_code ="";
Tokenizer = [];
def generate_token(parse_code):
	global Tokenizer;
	sp = parse_code.split('\n')
	for i in range(0,len(sp)):
		lineNo = i;
		lines = sp[i];
		lines = lines.strip();
		line = lines.split(' ');
		Tokenizer.extend(line);
	Tokenizer = list(filter(None, Tokenizer))
	return Tokenizer;
count = 0;
def getNextToken():
	global count;
	count = count+1;
	if(count <= len(Tokenizer)):
		return Tokenizer[count-1];
	else:
		exit(0);
def retract():
	global count;
	if count != 0:
		count = count - 1;
def parse():
	S();
def S():
	if header():
		if S():
			return True; 
	elif A():
		return True;
	else:
		return False;
def header():
	tok = getNextToken();
	if tok == '#include<stdio.h>':
		return True;
	elif tok == '#include<stdlib.h>':
		return True;
	else:
		#print("Header Error\n");
		retract();
		return False;
def A():
	tok1 = getNextToken();
	if tok1 == 'int':
		tok2 = getNextToken();
		if tok2 == 'main':
			tok3 = getNextToken();
			if tok3 == '(' and arg():
				tok4 = getNextToken();
				if tok4 == ')':
					tok5 = getNextToken();
					if tok5 == '{':
						if Block():
							tok6 = getNextToken();
							tok7 = getNextToken();
							tok8 = getNextToken();
							tok9 = getNextToken();
							if tok6 == 'return' and tok7 == '0' and tok8 == ';' and tok9 == '}':
								return True;
							else:
								print("Error in Return statement\n");
								retract();
								retract();
								retract();
								retract();
								return False;
		
					else:
						print("Error:Missing {\n");
						retract();
						return False;
				else:
					print("Error:Missing )\n");
					retract();
					return False;
			else:
				print("Error in argument list or missing (\n");
				retract();
				return False;
		else:
			print("Error:Expecting main function\n");
			retract();
			return False;
	else:
		retract();
		print("Error:Expecting return type to be int\n");
		return False;
def arg():
	tok1 = getNextToken();
	if tok1 == 'int':
		tok2 = getNextToken();
		if tok2 == 'argc':	
			tok3 = getNextToken();
			if tok3 == ',': 
				tok4 = getNextToken();
				if tok4 == 'char*':
					tok5 = getNextToken();
					if tok5 == 'argv':
						tok6 = getNextToken();
						if tok6 == '[]':
							return True;
						else:
							print("Error:Missing []\n");
							retract();
							return False;
					else:
						print("Error:Missing a variable to char*\n");
						retract();
						return False;
				else:
					print("Error:Missing a pointer to char\n");
					retract();
					return False;
			else:
				print("Error:Missing ,\n");
				retract();
				return False;
		else:
			print("Error:Missing a variable to int,\n");
			retract();
			return False;
	else:
		print("Error:Missing int\n");
		retract();
		return False;
def Block():
	if T():
		if T():
			return True;
		else:
			return False;
	else:
		return False;
def K():
	tok1 = getNextToken()
	if tok1 == "int" or tok1 == "char" or tok1 == "float" or tok1 == "double":
		return True
	else:
		#print("Error: Valid Type (int, char, float or double) expected!")
		retract();
		return False
def T():
	global symTab;
	if K():
		tok1 = getNextToken();
		global symTab;
		if tok1 in symTab:
			tok2 = getNextToken();
			if tok2 == "=":
				E();
				tok3 = getNextToken();
				if tok3 == ";":
					T();
					return True
				else:
					print("Error: Semicolon (;) expected!")
					retract();
					return False
			elif tok2 == ";":
				T();
				return True
			else:
				print("Error: Semicolon (;) or Equals (=) expected!")
				retract();
				return False
		else:
			print("Error: Valid Identifier expected!")
			retract();
			return False
	elif F():
		return True
	
	elif getNextToken() in symTab:
		if getNextToken() == "=":
			if E():
				if(getNextToken() == ";"):
					if T():
						return True
					else:
						retract();
						return False
				else:
					print("Error: Semicolon (;) expected!")
					retract();
					return False;
			else:
				return False
		else:
			print("Error1: Equals (=) expected")
			retract();
			return False;
	else:
		retract();
		return False

def F():
	if getNextToken() == "for":
		if getNextToken() == "(":
			if Assign():
				if getNextToken() == ";":
					if cond():
						if getNextToken() == ";":
							if Expr():
								if getNextToken() == ")":
									if getNextToken() == "{":
										if Block():
											if getNextToken() == "}":
												return True
											else:
												print("Error: Closing Brace (}) expected")
												retract();
												return False
										else:
											return False
									else:
										print("Error: Opening Brace ({) expected")
										retract();
										return False
								else:
									print("Error: Closing Parenthesis \")\" expected")
									retract();
									return False
							else:
								return False
						else:
							print("Error: Semicolon (;) expected!")
							retract();
							return False
					else:
						print("Call to method cond() expected!")
						return False
				else:
					print("Error: Semicolon (;) expected!")
					retract();
					return False
			else:
				return False
		else:
			print("Error: Opening Parenthesis \"(\" expected")
			retract();
			return False
	else:
		#print("Error: Keyword \"for\" expected!")
		retract();
		return False
def Ebar():
	tok1 = getNextToken()
	if tok1 == '+' or tok1 == '-':
		if J():
			if Ebar():
				return True
			else:
				retract();
				return False
		else:
			retract();
			return False
	else:
		retract();
		print("error : expected + or - operator")
		return False;
	
def E():
	if J():
		if Ebar():
			return True
		else:
			return False
	else:
		return False

def Jbar():
	tok1 = getNextToken()
	if tok1 == '*' or tok1 == '/':
		if L():
			if Jbar():
				return True
			else:
				retract();
				return False
		else:
			retract();
			return False
	else:
		retract();
		#print("error : expected * or / operator")
		return False;
	
def J():
	if L():
		if Jbar():
			return True
		else:
			return False
	else:
		return False


def L():
	tok1=getNextToken();
	if tok1=='(':
		if E():
			tok2=getNextToken();
			if tok2 == ')':
				return True
	elif preID(tok1):
		return True
	elif preNum(tok1):
		return True;
	else:
		retract();
		return False;
def preID(tok1):
	global symTab;
	for i in symTab:
		if tok1 == i:
			return True;
	for i in valTab:
		if tok1 == i:
			return True;
	return False;
def preNum(tok1):
	for i in tok1:
		if (ord(i) >= 48 and ord(i) <= 57) or (ord(i) == 46):
			continue;
		else:
			return False;
	return True;
	
def Assign():
	tok1 = getNextToken()
	if(tok1 in symTab):
		tok2 = getNextToken()
		if(tok2=="="):
			E()
		else:
			retract();
			print("Error: Missing =")
			return False;
	else:
		return True

def Cond():
	if E():
		tok1 = getNextToken()
		if(tok1 in ['>','<','||','&&','>=','<=']):
			if E():
				return True;
		else:
			retract();
			return False;

def Expr():
	if(Assign()):
		return True
	else:
		tok1 = getNextToken()
		if(tok1 in symTab):
			tok2 = getNextToken()
			if(tok2 in ["++","--"]):
				return True
		else:
			retract();
			return False;
			
precedence = [['/','1'],['*','1'],['+','2'],['-','2']];
def precedenceOf(t):
	token = t[0];
	for i in range(len(precedence)):
		if(token == precedence[i][0]):
			return int(precedence[i][1]);
	return -1;
tempVar = 1;
intermediate = "";
def icgExpr(expr):
	global tempVar;
	global intermediate;
	opera = ['+','-','*','/','=']
	precessed = [];
	opc = 0;
	operators = [];
	for i in range(10):
		operators.append([[],[]]);
	
	processed = [False]*(len(expr));
	for i in range(len(expr)):
		token = expr[i];
		for j in range(len(precedence)):
			if(token == precedence[j][0]):
				operators[opc][0] = str(token);
				operators[opc][1] = str(i);
				opc += 1;
				break;
	
	for i in range(opc-1,0,-1):
		for j in range(i):
			if (precedenceOf(operators[j][0]) > precedenceOf(operators[j+1][0])):
				temp = operators[j][0];
				operators[j][0] = operators[j+1][0];
				operators[j+1][0] = temp;
				temp = operators[j][1];
				operators[j][1] = operators[j+1][1];
				operators[j+1][1] = temp;
	for i in range(opc):
		j = int(operators[i][1]+"");
		op1 = "";
		op2 = "";
		if(processed[j-1] == True):
			if(precedenceOf(operators[i-1][0]) == precedenceOf(operators[i][0])):
				op1 = str(str("t")+str(tempVar));
				tempVar += 1;
			else:
				for x in range(opc):
					if((j-2) == int(operators[x][1])):
						op1 = str(str("t")+str(tempVar));
						tempVar += 1;
		else:
			k = 0;
			for k in range(j-1,0,-1):
				if expr[k] in opera:
					break;
			op1 = expr[k+1:j]+"";
		if(processed[j+1] == True):
			for x in range(opc):
				if((j+2) == int(operators[x][1])):
					op2 = str(str("t")+str(tempVar));
		else:
			k = 0;
			for k in range(j+1,len(expr)):
				if expr[k] in opera:
					break;
			for k in range(j+1,len(expr)):
				if expr[k] in opera:
					break;
			if k != (len(expr)-1):
				op2 = expr[j+1:k]+"";
			else:
				op2 = expr[j+1:k+1]+"";
		print("t",(tempVar+1)," = ",op1,operators[i][0],op2);
		intermediate += "t"+str(tempVar+1)+" = "+str(op1)+str(operators[i][0])+str(op2)+"\n";
		tempVar += 1;
		processed[j] = processed[j-1] = processed[j+1] = True;
	lval = expr.split("=");
	if(len(lval) > 1):
		if not(opc == 0 and "=" in expr):
			print(lval[0].strip()," = ","t",(tempVar));
			intermediate += str(lval[0].strip())+" = "+"t"+str(tempVar)+"\n";
			tempVar += 1;
		else:
			decl = lval[0].strip().split(" ");
			if(len(decl) > 1):
				print(decl[1]," = ",lval[1]);
				intermediate += str(decl[1])+" = "+str(lval[1])+"\n";
			else:
				print(decl[0]," = ",lval[1]);
				intermediate += str(decl[0])+" = "+str(lval[1])+"\n";
	
	
rules = [
	('int|float|char|long|double|for|printf|main|return',		'KEYWORD'),
	('#include<stdio.h>|#include<stdlib.h>',	'LIBRARY'),
	('\;',				'SEMICOLON'),
  	('\,',				'COMMA'),
    ('\d+',             'NUMBER'),
    ('[a-zA-Z_]\w*',    'IDENTIFIER'),
    ('\++',				'INCREMENT'),
    ('\--',				'DECREMENT'),
    ('\+',              'PLUS'),
    ('\d*\.\d+',		'DECIMAL'),
    ('\'[a-zA-Z]+\'',		'CHARACTER'),
    ('\-',              'MINUS'),
    ('\*',              'MULTIPLY'),
    ('\/',              'DIVIDE'),
    ('\(',              'LP'),
    ('\)',              'RP'),
    ('\{',              'LB'),
    ('\}',              'RB'),
    ('\[\]',				'ARRAY'),
    ('=',               'ASSIGN'),
    ('==',              'EQ'),
    ('>',              'GT'),
    ('<',              'LT'),
    ('||',              'OR'),
  	('&&',              'AND')
  	
]
def checkSemantics(string):
	global valTab;
	global symTab;
	global catTab;
	if "=" in string:
		rhs = string.split("=");
		rhsParam = rhs[1].split(" ");
		for i in range(len(symTab)):
			for j in rhsParam:
				if symTab[i] == j and valTab[i] == 'undefined':
					print("Error:",symTab[i]," is used before initialization on rhs of an assignment");
	for i in range(len(symTab)):
		for j in range(len(symTab)):
			if i != j and symTab[i] == symTab[j]:
				print("Error:Redefinition of ",symTab[i]," in the program");
				return;

def removeComments(string):
    string = re.sub(re.compile("/\*.*?\*/",re.DOTALL ) ,"" ,string); # remove all occurance streamed comments (/*COMMENT */) from string
    string = re.sub(re.compile("//.*?\n" ) ,"\n" ,string); # remove all occurance singleline comments (//COMMENT\n ) from string
    return string;
tempVar = 1;
ast = "";
def astExpr(expr):
	global tempVar;
	global intermediate;
	global ast;
	ast = "";
	opera = ['+','-','*','/','=']
	precessed = [];
	opc = 0;
	operators = [];
	for i in range(10):
		operators.append([[],[]]);
	
	processed = [False]*(len(expr));
	for i in range(len(expr)):
		token = expr[i];
		for j in range(len(precedence)):
			if(token == precedence[j][0]):
				operators[opc][0] = str(token);
				operators[opc][1] = str(i);
				opc += 1;
				break;
	

	for i in range(opc-1,0,-1):
		for j in range(i):
			if (precedenceOf(operators[j][0]) > precedenceOf(operators[j+1][0])):
				temp = operators[j][0];
				operators[j][0] = operators[j+1][0];
				operators[j+1][0] = temp;
				temp = operators[j][1];
				operators[j][1] = operators[j+1][1];
				operators[j+1][1] = temp;
	
	for i in range(opc):
		j = int(operators[i][1]+"");
		op1 = "";
		op2 = "";
		if(processed[j-1] == True):
			if(precedenceOf(operators[i-1][0]) == precedenceOf(operators[i][0])):
				op1 = str(str("t")+str(tempVar));
				tempVar += 1;
			else:
				for x in range(opc):
					if((j-2) == int(operators[x][1])):
						op1 = str(str("t")+str(tempVar));
						tempVar += 1;
		else:
			k = 0;
			for k in range(j-1,0,-1):
				if expr[k] in opera:
					break;
			op1 = expr[k+1:j]+"";
		if(processed[j+1] == True):
			for x in range(opc):
				if((j+2) == int(operators[x][1])):
					op2 = str(str("t")+str(tempVar));
		else:
			k = 0;
			for k in range(j+1,len(expr)):
				if expr[k] in opera:
					break;
			for k in range(j+1,len(expr)):
				if expr[k] in opera:
					break;
			if k != (len(expr)-1):
				op2 = expr[j+1:k]+"";
			else:
				op2 = expr[j+1:k+1]+"";
		
		ast += "t"+str(tempVar+1)+" = "+str(op1)+str(operators[i][0])+str(op2)+"\n";
		tempVar += 1;
		processed[j] = processed[j-1] = processed[j+1] = True;
	lval = expr.split("=");
	if(len(lval) > 1):
		if not(opc == 0 and "=" in expr):
			ast += str(lval[0].strip())+" = "+"t"+str(tempVar)+"\n";
			tempVar += 1;
		else:
			decl = lval[0].strip().split(" ");
			if(len(decl) > 1):
				ast += str(decl[1])+" = "+str(lval[1])+"\n";
			else:
				ast += str(decl[0])+" = "+str(lval[1])+"\n";
	ast = ast.strip();
	ret = "";
	ast_lines = ast.split("\n");
	if "<" in expr or ">" in expr or "<=" in expr or ">=" in expr:
		ast_lines = [expr];
	for i in ast_lines:
		if "=" in i:
			param = i.split("=");
			param[1] = param[1].strip();
		
			if "+" in param[1]:
				args = param[1].split("+");
				if ret == "":
					ret = "(+, "+str(args[0])+", "+str(args[1])+")";
				else:
					ret = "(+, "+str(args[0])+", "+ ret+")";
			elif "-" in param[1]:
				args = param[1].split("-");
				if ret == "":
					ret = "(-, "+str(args[0])+", "+str(args[1])+")";
				else:
					ret = "(-, "+str(args[0])+", "+ ret+")";
			elif "*" in param[1]:
				args = param[1].split("*");
				if ret == "":
					ret = "(*, "+str(args[0])+", "+str(args[1])+")";
				else:
					ret = "(*, "+str(args[0])+", "+ ret+")";
			elif "/" in param[1]:
				args = param[1].split("/");
				if ret == "":
					ret = "(/, "+str(args[0])+", "+str(args[1])+")";
				else:
					ret = "(/, "+str(args[0])+", "+ ret+")";
			else:
				if ret == "":
					ret = "(=, "+str(param[0])+", "+str(param[1])+")";
				else:
					ret = "(=, "+str(param[0])+", "+ ret+")";
		elif "<" in i:
			args = i.split("<");
			if ret == "":
				ret = "(<, "+str(args[0])+", "+str(args[1])+")";
			else:
				ret = "(<, "+str(args[0])+", "+ ret+")";
		elif "<=" in i:
			args = i.split("<=");
			if ret == "":
				ret = "(<=, "+str(args[0])+", "+str(args[1])+")";
			else:
				ret = "(<=, "+str(args[0])+", "+ ret+")";
		elif ">" in i:
			args = i.split(">");
			if ret == "":
				ret = "(>, "+str(args[0])+", "+str(args[1])+")";
			else:
				ret = "(>, "+str(args[0])+", "+ ret+")";
		elif ">=" in i:
			args = i.split(">=");
			if ret == "":
				ret = "(>=, "+str(args[0])+", "+str(args[1])+")";
			else:
				ret = "(>=, "+str(args[0])+", "+ ret+")";
		
	return ret;
def generateAST():
	f = open("progMod.c", "r")
	expr = []
	forexpr = []
	forHeader = "";
	for i in f:
		print(i);
		i = i.replace('\n', '')
		if forHeader != "" and "\t}" in i:
			forHeader = "";
		elif "for" in i:
			forHeader = i
			init = re.split(r"\(|;", forHeader)[1]
			cond = re.split(r";", forHeader)[1]
			incr = re.split(r";|\)", forHeader)[2]
		elif "=" in i:
			check = i.strip()
			check = check.strip(";")
			if forHeader == "":
				expr.append(check)
			else:
				forexpr.append(check)
	print("For:",forexpr);
	print("expr:",expr);
	print("The Abstract Syntax Tree for the given input is:")

	for i in expr:
		out = i.split("=")
		if not("+" in i or "-" in i or "*" in i or "/" in i):
			print("(=, ", out[0], ", ", out[1], ")", sep = "")
		else:
			print(astExpr(i));

	print("(for, "+str(astExpr(init))+", "+str(astExpr(cond))+", ",end = "");
	for i in forexpr:
		print(astExpr(i)+", ",end="");
	print(astExpr(incr),")");
with open('prog.c') as f:
	s = f.read();
s1 = removeComments(s)
s1 = s1.replace("\n\n","\n");
with open('progMod.c','w+') as f1:
	f1.write(s1);


count = 0;
with open('progMod.c') as f2:
	code = f2.read();
code = re.sub(re.compile("\".*?\"",re.DOTALL),"",code);
icg_code = code;
code = code.replace("("," ( ");
code = code.replace(")"," ) ");
code = code.replace("{"," { ");
code = code.replace("}"," } ");
code = code.replace(";"," ; ");
code = code.replace("++"," ++ ");
code = code.replace("-"," -- ");
code = code.replace("="," = ");
code = code.replace("=="," == ");
code = code.replace("||"," || ");
code = code.replace("&&"," && ");
code = code.replace("\n\n","\n");
code = code.replace(","," , ");

parse_code = code;
sem_code = code;
lx = Lexer(rules, skip_whitespace=True)

sp = code.split('\n')
for i in range(0,len(sp)):
	lineNo = i;
	lines = sp[i];
	lines = lines.strip();
	line = lines.split(' ');
	for j in line:
		lx.input(j)
		try:
			for tok in lx.tokens():
				print(str(tok)+" Position and Line "+str(lineNo+1))
		except LexerError as err:
			print('LexerError at position %s' % err.pos)
	
keyword = re.compile("int|float|char|long|double");
identifier = re.compile(r"^[^\d\W]\w*\Z", re.UNICODE);
number = re.compile(r"[0-9][0-9]*");
lines = code.split("\n");
for j in lines:
	l = j.strip();
	l = l.split(' ');
	if(re.match(keyword,l[0]) is not None):
		if(re.match(identifier,l[1]) is not None):
			if(l[2] == '='):
				symTab.append(l[1]);
				valTab.append(l[3]);
				catTab.append(l[0]);
			elif(l[2] == ';'):
				symTab.append(l[1]);
				valTab.append('undefined');
				catTab.append(l[0]);
			elif(l[2] == ','):
				symTab.append(l[1]);
				valTab.append('undefined');
				catTab.append(l[0]);
				if(re.match(identifier,l[3]) is not None):
					if(l[4] == '='):
						symTab.append(l[3]);
						valTab.append(l[5]);
						catTab.append(l[0]);
					elif(l[2] == ';'):
						symTab.append(l[3]);
						valTab.append('undefined');
						catTab.append(l[0]);
	elif(re.match(identifier,l[0]) is not None):
		if l[0] not in symTab and l[0] != "for":
			if(l[1] == '='):
				symTab.append(l[0]);
				valTab.append(l[2]);
				catTab.append('undefined');
			elif(l[1] == ';'):
				symTab.append(l[0]);
				valTab.append('undefined');
				catTab.append('undefined');
		elif l[0] == "for" and l[2] not in symTab:
			symTab.append(l[2]);
			valTab.append(l[4]);
			catTab.append('undefined');
		else:
			for i in range(len(symTab)):
				if symTab[i] == l[0]:
					break;
			if(l[1] == '='):
				symTab[i] = l[0];
				valTab[i] = l[2];
			elif(l[1] == ';'):
				symTab[i] = l[0];
				valTab[i] = 'undefined';
for i in code.split('\n'):
	if "(" in i and ";" in i:
		a = re.split(r'[(]|;',i);
		b = a[1].strip();
		if "=" in b:
			b1 = b.split("=");
			if b1[0].strip() in symTab:
				pos = symTab.index(b1[0].strip());
				valTab[pos] = b1[1].strip();
print("---------------------------------------------------------------------------------------------------------------------");
print("Symbol table");
for i in range(0,len(symTab)):
	print(str(catTab[i])+"  ->  "+str(symTab[i])+"  ->  "+str(valTab[i]));
tokens = generate_token(parse_code);
sem_code_lines = sem_code.split('\n');
for i in sem_code_lines:
	checkSemantics(i);
for i in range(len(catTab)):
	if catTab[i] == 'undefined':
		print("Error Undefined type of ",symTab[i]);
parse();

print("---------------------------------------------------------------------------------------------------------------------");
print("Generating Abstract Syntax Tree for the code:\n");
generateAST();
print("---------------------------------------------------------------------------------------------------------------------");
print("Printing Intermediate Code in 3 Address format\n");
icg_lines = icg_code.split('\n');
labelCount = 0;
insideFor = 0;
forExpr = "";
labelCountFor = -1;

for i in icg_lines:
	i = i.strip();
	if "for" in i:
		init1 = i.split(";");
		init = init1[0].split("(")[1];
		icgExpr(init);
		cond = init1[1];
		insideFor = 1;
		forExpr = init1[2].split(")")[0];
		labelCountFor = labelCount;
		print("Label L",labelCount,":",sep="");
		intermediate += "Label L"+str(labelCount)+":\n";
		labelCount += 1;
		print("x = ",cond);
		intermediate += "x = "+str(cond)+"\n";
		print("ifFalse x goto L",labelCount);
		intermediate += "ifFalse x goto L"+str(labelCount)+"\n";
	elif "=" in i:
		icgExpr(i);
	elif i == "}" and insideFor == 1:
		icgExpr(forExpr);
		print("goto L",labelCountFor);
		intermediate += "goto L"+str(labelCountFor)+"\n";
		labelCountFor = -1;
		insideFor = 0;
		print("Label L",labelCount,":",sep="");
		intermediate += "Label L"+str(labelCount)+":\n";
	
	
	elif "return" in i:
		print("return 0");
		intermediate += "return 0\n";
print("---------------------------------------------------------------------------------------------------------------------");
print("printing intermediate code in Quadruple format:\nOperator\tArgument 1\tArgument 2\t Result");
quad_lines = intermediate.split("\n");

for i in quad_lines:
	Oper = "";
	Arg1 = "";
	Arg2 = "";
	Res = "";
	if "=" in i and ("+" not in i and "-" not in i and "*" not in i and "/" not in i and "<" not in i and ">" not in i and "<=" not in i and ">=" not in i):
		Oper = "=";
		t = i.split("=");
		Res = t[0].strip();
		Arg1 = t[1].split(";")[0].strip();
	elif "=" in i and "+" in i:
		Oper = "+";
		t = i.split("=");
		Res = t[0].strip();
		Arguments = t[1].split("+");
		Arg1 = Arguments[0].strip();
		Arg2 = Arguments[1].split(";")[0].strip();
	elif "=" in i and "-" in i:
		Oper = "-";
		t = i.split("=");
		Res = t[0].strip();
		Arguments = t[1].split("-");
		Arg1 = Arguments[0].strip();
		Arg2 = Arguments[1].split(";")[0].strip();
	elif "=" in i and "*" in i:
		Oper = "*";
		t = i.split("=");
		Res = t[0].strip();
		Arguments = t[1].split("*");
		Arg1 = Arguments[0].strip();
		Arg2 = Arguments[1].split(";")[0].strip();
	elif "=" in i and "/" in i:
		Oper = "/";
		t = i.split("=");
		Res = t[0].strip();
		Arguments = t[1].split("/");
		Arg1 = Arguments[0].strip();
		Arg2 = Arguments[1].split(";")[0].strip();
	elif "Label" in i:
		Oper = "Label";
		Res = i.split(" ")[1].split(":")[0].strip();
	elif "ifFalse" in i:
		para = i.split();
		Arg1 = para[1];
		Res = str(para[3]);
		Oper = "ifFalse";
		print(Oper,"\t",Arg1,"\t\t",Arg2,"\t\t",Res);
		continue;
	elif "goto" in i:
 		Oper = "goto";
 		para = i.split(" ");
 		Res = str(para[1]);
	elif "<" in i or ">" in i or "<=" in i or ">=" in i:
		para = i.split("=");
		Res = para[0].strip();
		para1 = re.split('<|>|<=|>=',para[1]);
		Arg1 = para1[0].strip();
		Arg2 = para1[1].strip();
		if "<" in para[1]:
			Oper = "<";
		elif ">" in para[1]:
			Oper = ">"
		elif "<=" in para[1]:
			Oper = "<="
		elif ">=" in para[1]:
			Oper = ">="
	elif "return" in i:
		Oper = "return";
		Arg1 = i.split(" ")[1].strip();
	print(Oper,"\t\t",Arg1,"\t\t",Arg2,"\t\t",Res);
print("---------------------------------------------------------------------------------------------------------------------");
